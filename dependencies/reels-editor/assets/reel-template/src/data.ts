import type {Caption} from "@remotion/captions";
import rawCaptions from "./generated/captions.json";
import rawTimeline from "./generated/timeline.json";
import type {Timeline} from "./types";

export const timeline = rawTimeline as Timeline;
export const captions = rawCaptions as Caption[];
