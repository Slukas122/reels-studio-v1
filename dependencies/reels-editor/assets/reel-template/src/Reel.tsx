import {Audio} from "@remotion/media";
import {AbsoluteFill, cancelRender, continueRender, delayRender, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {useEffect, useState} from "react";
import {Captions} from "./Captions";
import {timeline} from "./data";
import type {Segment} from "./types";

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

const BrandFont: React.FC<{file: string}> = ({file}) => {
  const [handle] = useState(() => delayRender("Load client font"));
  useEffect(() => {
    const face = new FontFace("ClientFont", `url("${staticFile(file)}")`);
    face.load()
      .then((loaded) => { document.fonts.add(loaded); continueRender(handle); })
      .catch((error) => cancelRender(error));
  }, [file, handle]);
  return null;
};

const Clip: React.FC<{segment: Segment}> = ({segment}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localMs = (frame / fps) * 1000;
  const globalMs = segment.outputStartMs + localMs;
  let punch = 1;
  for (const effect of timeline.effects) {
    if (globalMs >= effect.atMs && globalMs <= effect.atMs + effect.durationMs) {
      punch = Math.max(punch, interpolate(globalMs, [effect.atMs, effect.atMs + effect.durationMs * 0.28, effect.atMs + effect.durationMs], [1, effect.scale, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"}));
    }
  }
  return (
    <OffthreadVideo
      src={staticFile(timeline.source)}
      trimBefore={msToFrames(segment.sourceStartMs, fps)}
      trimAfter={msToFrames(segment.sourceEndMs, fps)}
      playbackRate={segment.rate}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        objectPosition: `${segment.focusX}% ${segment.focusY}%`,
        transform: `scale(${segment.scale * punch})`,
      }}
    />
  );
};

const isVideo = (src: string) => /\.(mp4|mov|m4v|webm|mkv)$/i.test(src);

const Broll: React.FC<{src: string; fit: "cover" | "contain"}> = ({src, fit}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [0, 0.15 * fps], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const style = {width: "100%", height: "100%", opacity, transform: "scale(1.015)"} as const;
  return isVideo(src) ? <OffthreadVideo src={staticFile(src)} muted style={{...style, objectFit: fit}} /> : <Img src={staticFile(src)} style={{...style, objectFit: fit}} />;
};

const TitleCard: React.FC<{text: string; kind: "hook" | "cta"}> = ({text, kind}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 180, mass: 0.7}});
  return (
    <AbsoluteFill style={{alignItems: "center", justifyContent: kind === "hook" ? "flex-start" : "center", padding: kind === "hook" ? "280px 100px 0" : "180px 100px", fontFamily: timeline.brand.fontFamily}}>
      <div style={{maxWidth: 860, color: timeline.brand.textColor, fontSize: kind === "hook" ? 66 : 70, fontWeight: 800, lineHeight: 1.06, letterSpacing: -1, textAlign: "center", textShadow: "0 3px 18px rgba(0,0,0,0.92), 0 1px 3px rgba(0,0,0,0.9)", overflowWrap: "anywhere", transform: `scale(${0.96 + enter * 0.04})`, opacity: enter}}>
        {text}
      </div>
    </AbsoluteFill>
  );
};

export const Reel: React.FC<{locale?: string}> = ({locale = "source"}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: timeline.brand.backgroundColor, overflow: "hidden"}}>
      {timeline.brand.fontFile ? <BrandFont file={timeline.brand.fontFile} /> : null}
      {timeline.segments.map((segment) => (
        <Sequence key={segment.id} from={msToFrames(segment.outputStartMs, fps)} durationInFrames={Math.max(1, msToFrames(segment.outputEndMs - segment.outputStartMs, fps))} name={segment.id}>
          <Clip segment={segment} />
        </Sequence>
      ))}

      {timeline.broll.map((item, index) => (
        <Sequence key={`${item.src}-${index}`} from={msToFrames(item.fromMs, fps)} durationInFrames={Math.max(1, msToFrames(item.toMs - item.fromMs, fps))}>
          <Broll src={item.src} fit={item.fit} />
        </Sequence>
      ))}

      <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(0,0,0,0.18), transparent 28%, transparent 68%, rgba(0,0,0,0.30))"}} />
      <Captions locale={locale} />

      {timeline.hook ? (
        <Sequence durationInFrames={msToFrames(timeline.hook.durationMs, fps)}>
          <TitleCard text={timeline.hook.locales?.[locale] ?? timeline.hook.text} kind="hook" />
        </Sequence>
      ) : null}

      {timeline.cta ? (
        <Sequence from={msToFrames(timeline.cta.mode === "endcard" ? timeline.spokenDurationMs : Math.max(0, timeline.spokenDurationMs - timeline.cta.durationMs), fps)} durationInFrames={msToFrames(timeline.cta.durationMs, fps)}>
          <TitleCard text={timeline.cta.locales?.[locale] ?? timeline.cta.text} kind="cta" />
        </Sequence>
      ) : null}

      {timeline.brand.logo ? <Img src={staticFile(timeline.brand.logo)} style={{position: "absolute", top: 72, right: 54, width: 150, height: 80, objectFit: "contain"}} /> : null}
      {timeline.music ? <Audio src={staticFile(timeline.music.src)} loop volume={() => timeline.music?.volume ?? 0} /> : null}
      {timeline.sfx.map((item, index) => (
        <Sequence key={`${item.src}-${index}`} from={msToFrames(item.atMs, fps)}>
          <Audio src={staticFile(item.src)} volume={() => item.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
