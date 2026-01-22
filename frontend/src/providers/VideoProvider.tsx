import {
  createContext,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

interface FirstFrame {
  frame_idx: number;
  frame_img: string;
  frame_num: number;
  height: number;
  width: number;
}
interface VideoData {
  count: number;
  first_frame: FirstFrame;
  fps: number;
  frame_numbers: number[];
  frame_set_id: string;
  total_frames: number;
  video_id: string;
  orig_height: number;
  orig_width: number;
  render_height: number;
  render_width: number;
}

interface KeyPointAnnotation {
  x: number | null;
  y: number | null;
  not_visible: boolean;
}

interface BodyPartAnnotations {
  [keypointName: string]: KeyPointAnnotation;
}

interface Annotations {
  [frameNumber: number]: BodyPartAnnotations;
  orig_width: number | null;
  orig_height: number | null;
  render_width: number | null;
  render_height: number | null;
}

interface VideoContextType {
  videoData: VideoData | null;
  setVideoData: (data: VideoData) => void;
  currentFrame: string;
  setCurrentFrame: (frame: string) => void;
  frames: number[];
  setFrames: (frames: number[]) => void;
  currentFrameNumber: number;
  setCurrentFrameNumber: (num: number) => void;
  currentFrameIdx: number;
  setCurrentFrameIdx: (idx: number) => void;
  annotations: Annotations;
  setAnnotations: Dispatch<SetStateAction<Annotations>>;
  selectedBodyPart: string | null;
  setSelectedBodyPart: (bodyPart: string | null) => void;
  annotationMode: boolean;
  setAnnotationMode: (mode: boolean) => void;
}

const initState: VideoContextType = {
  videoData: null,
  setVideoData: () => {},
  frames: [],
  setFrames: () => {},
  currentFrame: "",
  setCurrentFrame: () => {},
  currentFrameNumber: 0,
  setCurrentFrameNumber: () => {},
  currentFrameIdx: 0,
  setCurrentFrameIdx: () => {},
  annotations: {
    orig_width: null,
    orig_height: null,
    render_width: null,
    render_height: null,
  },
  setAnnotations: () => {},
  selectedBodyPart: null,
  setSelectedBodyPart: () => {},
  annotationMode: false,
  setAnnotationMode: () => {},
};

export const VideoContext = createContext<VideoContextType>(initState);

export const VideoProvider = ({ children }: { children: ReactNode }) => {
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [frames, setFrames] = useState<number[]>([]);
  const [currentFrame, setCurrentFrame] = useState<string>("");
  const [currentFrameIdx, setCurrentFrameIdx] = useState<number>(0);
  const [currentFrameNumber, setCurrentFrameNumber] = useState<number>(0);
  const [annotations, setAnnotations] = useState<Annotations>({
    orig_width: null,
    orig_height: null,
    render_width: null,
    render_height: null,
  });
  const [selectedBodyPart, setSelectedBodyPart] = useState<string | null>(null);
  const [annotationMode, setAnnotationMode] = useState<boolean>(false);

  return (
    <VideoContext.Provider
      value={{
        videoData,
        setVideoData,
        frames,
        setFrames,
        currentFrame,
        setCurrentFrame,
        currentFrameIdx,
        setCurrentFrameIdx,
        currentFrameNumber,
        setCurrentFrameNumber,
        annotations,
        setAnnotations,
        selectedBodyPart,
        setSelectedBodyPart,
        annotationMode,
        setAnnotationMode,
      }}
    >
      {children}
    </VideoContext.Provider>
  );
};

export default VideoProvider;
