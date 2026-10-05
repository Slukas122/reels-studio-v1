import {createTikTokStyleCaptions, type TikTokPage} from "@remotion/captions";
import {AbsoluteFill, cancelRender, continueRender, delayRender, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {useEffect, useState} from "react";
import {captions, timeline} from "./data";

const clean = (word: string) => word.toLocaleLowerCase().replace(/[^\p{L}\p{N}]/gu, "");

const CaptionPage: React.FC<{page: TikTokPage}> = ({page}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const absoluteMs = page.startMs + (frame / fps) * 1000;
  const highlights = new Set(timeline.captions.highlightWords.map(clean));
  const speakers = new Map(captions.map((item) => [Math.round(item.startMs), (item as typeof item & {speaker?: string}).speaker]));
  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: timeline.captions.position === "middle" ? "center" : "flex-end",
        padding: timeline.captions.position === "middle" ? "300px 64px" : "300px 64px 390px",
        fontFamily: timeline.brand.fontFamily,
      }}
    >
      <div
        style={{
          maxWidth: 960,
          padding: "18px 28px 22px",
          borderRadius: 20,
          background: timeline.brand.captionBoxColor,
          boxShadow: timeline.brand.captionBoxColor === "transparent" ? "none" : "0 12px 42px rgba(0,0,0,0.28)",
          color: timeline.brand.textColor,
          fontSize: timeline.captions.fontSize,
          fontWeight: 800,
          lineHeight: 1.08,
          letterSpacing: -0.7,
          textAlign: "center",
          textTransform: "none",
          whiteSpace: "pre-wrap",
        }}
      >
        {page.tokens.map((token, index) => {
          const active = token.fromMs <= absoluteMs && token.toMs > absoluteMs;
          const important = highlights.has(clean(token.text));
          const speaker = speakers.get(Math.round(token.fromMs));
          const speakerColor = speaker ? timeline.captions.speakerColors[speaker] : undefined;
          const scale = active ? interpolate(absoluteMs, [token.fromMs, token.fromMs + 90], [1, 1.025], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}) : 1;
          return (
            <span
              key={`${token.fromMs}-${index}`}
              style={{
                display: "inline-block",
                marginLeft: index === 0 ? 0 : "0.3em",
                color: active || important ? timeline.brand.accentColor : speakerColor ?? timeline.brand.textColor,
                transform: `scale(${scale})`,
                transformOrigin: "center bottom",
                textShadow: "0 4px 12px rgba(0,0,0,0.72)",
              }}
            >
              {token.text.trim()}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

type TranslatedCue = {startMs: number; endMs: number; text: string; speaker?: string | null};

const TranslatedCaptions: React.FC<{locale: string}> = ({locale}) => {
  const {fps} = useVideoConfig();
  const [cues, setCues] = useState<TranslatedCue[] | null>(null);
  const [handle] = useState(() => delayRender(`Load ${locale} captions`));
  useEffect(() => {
    fetch(staticFile(`locales/${locale}.json`))
      .then((response) => {
        if (!response.ok) throw new Error(`Missing subtitles for ${locale}`);
        return response.json() as Promise<TranslatedCue[]>;
      })
      .then((value) => { setCues(value); continueRender(handle); })
      .catch((error) => cancelRender(error));
  }, [handle, locale]);
  if (!cues) return null;
  return <AbsoluteFill>{cues.map((cue, index) => (
    <Sequence key={`${cue.startMs}-${index}`} from={Math.round(cue.startMs / 1000 * fps)} durationInFrames={Math.max(1, Math.round((cue.endMs - cue.startMs) / 1000 * fps))}>
      <AbsoluteFill style={{alignItems: "center", justifyContent: timeline.captions.position === "middle" ? "center" : "flex-end", padding: timeline.captions.position === "middle" ? "300px 64px" : "300px 64px 390px", fontFamily: timeline.brand.fontFamily}}>
        <div style={{maxWidth: 960, padding: "18px 28px 22px", borderRadius: 30, background: timeline.brand.captionBoxColor, color: cue.speaker ? timeline.captions.speakerColors[cue.speaker] ?? timeline.brand.textColor : timeline.brand.textColor, fontSize: timeline.captions.fontSize, fontWeight: 900, lineHeight: 1.02, textAlign: "center", textShadow: "0 4px 12px rgba(0,0,0,0.72)"}}>{cue.text}</div>
      </AbsoluteFill>
    </Sequence>
  ))}</AbsoluteFill>;
};

export const Captions: React.FC<{locale?: string}> = ({locale = "source"}) => {
  const {fps} = useVideoConfig();
  if (locale !== "source") return <TranslatedCaptions locale={locale} />;
  if (!timeline.captions.enabled || captions.length === 0) return null;
  const {pages} = createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 900});
  return (
    <AbsoluteFill>
      {pages.map((page, index) => {
        const next = pages[index + 1];
        const start = Math.round((page.startMs / 1000) * fps);
        const endMs = next?.startMs ?? Math.min(timeline.spokenDurationMs, page.startMs + 1400);
        const duration = Math.max(1, Math.round(((endMs - page.startMs) / 1000) * fps));
        return (
          <Sequence key={`${page.startMs}-${index}`} from={start} durationInFrames={duration}>
            <CaptionPage page={page} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
