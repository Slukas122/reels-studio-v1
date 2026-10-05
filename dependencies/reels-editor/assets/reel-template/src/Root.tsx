import "./index.css";
import {Composition} from "remotion";
import {Reel} from "./Reel";
import {timeline} from "./data";

export const RemotionRoot: React.FC = () => {
  const {fps, width, height} = timeline.format;
  return (
    <Composition
      id="Reel"
      component={Reel}
      durationInFrames={Math.max(1, Math.ceil((timeline.totalDurationMs / 1000) * fps))}
      fps={fps}
      width={width}
      height={height}
      defaultProps={{locale: "source"}}
    />
  );
};
