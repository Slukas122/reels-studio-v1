import {spawnSync} from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const valueAfter = (flag, fallback) => {
  const index = process.argv.indexOf(flag);
  return index === -1 ? fallback : process.argv[index + 1];
};
const input = path.resolve(root, valueAfter("--input", "outputs/reel-raw.mp4"));
const output = path.resolve(root, valueAfter("--output", "outputs/reel-final.mp4"));
const outputs = path.join(root, "outputs") + path.sep;
if (!input.startsWith(outputs) || !output.startsWith(outputs)) {
  console.error("Input and output must be inside outputs/");
  process.exit(1);
}
if (!fs.existsSync(input)) {
  console.error("Missing outputs/reel-raw.mp4. Run npm run render first.");
  process.exit(1);
}
const remotion = path.join(root, "node_modules", ".bin", process.platform === "win32" ? "remotion.cmd" : "remotion");
const result = spawnSync(remotion, ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-i", input, "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-af", "loudnorm=I=-14:LRA=7:TP=-1.5", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-y", output], {cwd: root, stdio: "inherit"});
if (result.status !== 0) process.exit(result.status ?? 1);
console.log(`Finished ${output}`);
