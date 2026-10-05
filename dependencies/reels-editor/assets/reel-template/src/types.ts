export type Segment = {
  id: string;
  sourceStartMs: number;
  sourceEndMs: number;
  outputStartMs: number;
  outputEndMs: number;
  rate: number;
  focusX: number;
  focusY: number;
  scale: number;
};

export type Punch = {
  type: "punch";
  atMs: number;
  durationMs: number;
  scale: number;
};

export type Timeline = {
  version: 1;
  source: string;
  format: {width: number; height: number; fps: number};
  segments: Segment[];
  spokenDurationMs: number;
  totalDurationMs: number;
  hook: null | {text: string; durationMs: number; locales?: Record<string, string>};
  cta: null | {text: string; durationMs: number; mode: "overlay" | "endcard"; locales?: Record<string, string>};
  effects: Punch[];
  broll: Array<{src: string; fromMs: number; toMs: number; fit: "cover" | "contain"}>;
  sfx: Array<{src: string; atMs: number; volume: number}>;
  music: null | {src: string; volume: number};
  captions: {
    enabled: boolean;
    maxWordsPerPage: number;
    position: "middle" | "lower";
    highlightWords: string[];
    fontSize: number;
    speakerColors: Record<string, string>;
  };
  brand: {
    fontFamily: string;
    textColor: string;
    accentColor: string;
    backgroundColor: string;
    captionBoxColor: string;
    logo: string | null;
    fontFile: string | null;
  };
};
