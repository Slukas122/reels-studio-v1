import {spawnSync} from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {downloadWhisperModel, installWhisperCpp, toCaptions, transcribe} from "@remotion/install-whisper-cpp";
import {toTimedWords} from "./whisper-words.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const valueAfter = (flag, fallback) => {
  const index = process.argv.indexOf(flag);
  return index === -1 ? fallback : process.argv[index + 1];
};
const model = valueAfter("--model", "small");
const language = valueAfter("--language", "auto");
const whisperVersion = "1.5.5";
const plan = JSON.parse(fs.readFileSync(path.join(root, "data/edit-plan.json"), "utf8"));
const input = path.join(root, "public", plan.source);
const cache = path.join(root, ".cache");
const whisperPath = path.join(cache, "whisper.cpp");
const wav = path.join(cache, "source-16khz.wav");
fs.mkdirSync(cache, {recursive: true});

const remotion = path.join(root, "node_modules", ".bin", process.platform === "win32" ? "remotion.cmd" : "remotion");
const converted = spawnSync(remotion, ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", input, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-y", wav], {cwd: root, stdio: "inherit"});
if (converted.status !== 0) process.exit(converted.status ?? 1);

await installWhisperCpp({to: whisperPath, version: whisperVersion});
await downloadWhisperModel({model, folder: whisperPath});
const whisperCppOutput = await transcribe({model, whisperPath, whisperCppVersion: whisperVersion, inputPath: wav, tokenLevelTimestamps: true, language});
const {captions} = toCaptions({whisperCppOutput});
const words = toTimedWords(captions);
fs.writeFileSync(path.join(root, "data/source-whisper-tokens.json"), `${JSON.stringify(captions, null, 2)}\n`);
fs.writeFileSync(path.join(root, "data/source-captions.json"), `${JSON.stringify(words, null, 2)}\n`);
fs.writeFileSync(path.join(root, "data/transcript.txt"), `${words.map((item) => item.text).join("").trim()}\n`);
fs.rmSync(wav, {force: true});
console.log(`Wrote ${words.length} timed words from ${captions.length} Whisper tokens using model ${model} and language ${language}.`);
