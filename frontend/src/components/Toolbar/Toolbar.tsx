import toast, { Toaster } from "react-hot-toast";
import LeftArrow from "../../assets/left-arrow.svg";
import RightArrow from "../../assets/right-arrow.svg";
import PenAnnotation from "../../assets/pen-annotate.svg";
// import Save from "../../assets/save.svg";
import Export from "../../assets/export.svg";
import useVideoContext from "../../providers/useVideoContext";
import { BODY_PART } from "../../constants/constants";
import type { BodyPartAnnotations } from "../../constants/types";

interface CanvasControl {
  label: string;
  className: string;
  icon: string;
  onClick?: () => void;
  active?: boolean;
}

const Toolbar = () => {
  const {
    videoData,
    currentFrameNumber,
    setCurrentFrameNumber,
    setCurrentFrame,
    currentFrameIdx,
    setCurrentFrameIdx,
    annotationMode,
    setAnnotationMode,
    annotations,
    setAnnotations,
  } = useVideoContext();

  const isFrameComplete = (frame: number) => {
    const frameAnnotations = annotations[frame];

    return Object.values(frameAnnotations).every((annotation) => {
      const { x, y, not_visible } = annotation;
      return (x !== null && y !== null && !not_visible) || not_visible;
    });
  };

  const fetchFrame = async (frame_set_id: string, frameIdx: number) => {
    const response = await fetch(
      `http://localhost:8000/frame-set/${frame_set_id}/frame?index=${frameIdx}`,
    );
    if (!response.ok) throw new Error("Failed to fetch frame");

    const data = await response.json();
    setCurrentFrame(data.frame_img);
    setCurrentFrameNumber(data.frame_num);
    setCurrentFrameIdx(data.frame_idx);

    // Initalize frame annotations if it doesn't exist
    if (!annotations[data.frame_num]) {
      const frameAnnotations: BodyPartAnnotations = {};
      BODY_PART.forEach((part) => {
        frameAnnotations[part] = { x: null, y: null, not_visible: false };
      });

      setAnnotations({
        ...annotations,
        [data.frame_num]: frameAnnotations,
      });
    }
  };

  const handleStepBack = () => {
    if (!videoData) return;

    fetchFrame(
      videoData.frame_set_id,
      currentFrameIdx > 0 ? currentFrameIdx - 1 : 0,
    );
  };

  const handleStepForward = () => {
    if (!videoData) return;

    if (!isFrameComplete(currentFrameNumber)) {
      toast.error("Missing annotations");
      return;
    }

    fetchFrame(
      videoData.frame_set_id,
      currentFrameIdx < videoData.count - 1
        ? currentFrameIdx + 1
        : videoData.count - 1,
    );
  };

  const handleToggleAnnotationMode = () => {
    setAnnotationMode(!annotationMode);
  };

  const exportVideoAnnotations = async () => {
    // Send annotations to the backend for CSV conversion
    const json = JSON.stringify(annotations);

    try {
      const response = await fetch(
        "http://localhost:8000/annotations/export-csv",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: json,
        },
      );

      if (!response.ok) throw new Error("Failed to export annotations as CSV");

      const blob = await response.blob();

      // Create the download
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${videoData?.video_id}_annotations.csv`;

      // Trigger the download
      document.body.appendChild(link);
      link.click();

      // Cleanup the link
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success("Annotations exported successfully");
    } catch (error) {
      toast.error("Failed to export annotations");
    }
  };

  const CANVAS_CONTROLS: CanvasControl[] = [
    {
      label: "Step Back",
      className: "px-4 py-2 bg-gray-500 rounded hover:bg-gray-700",
      icon: LeftArrow,
      onClick: handleStepBack,
    },
    {
      label: "Step Forward",
      className: "px-4 py-2 bg-gray-500 rounded hover:bg-gray-700",
      icon: RightArrow,
      onClick: handleStepForward,
    },
    {
      label: "Annotate",
      className: annotationMode
        ? "px-4 py-2 bg-gray-700 rounded ring-2 ring-blue-400 shadow-md shadow-blue-100/50"
        : "px-4 py-2 bg-gray-500 rounded hover:bg-gray-700",
      icon: PenAnnotation,
      onClick: handleToggleAnnotationMode,
      active: annotationMode,
    },
    // TODO: TBD IF WE WILL NEED TO IMPLEMENT THIS, ANJA TO DECIDE
    // {
    //   label: "Save",
    //   className: "px-4 py-2 bg-gray-500 rounded hover:bg-gray-700",
    //   icon: Save,
    // },
    {
      label: "Export",
      className: "px-4 py-2 bg-gray-500 rounded hover:bg-gray-700",
      icon: Export,
      onClick: exportVideoAnnotations,
    },
  ];

  return (
    <>
      <Toaster position="top-center" />
      <div className="flex flex-row items-center space-x-4 py-2">
        {CANVAS_CONTROLS.map((control) => (
          <button
            key={control.label}
            className={control.className}
            title={control.label}
            onClick={control.onClick}
          >
            <img
              src={control.icon}
              alt={control.label}
              className="w-5 h-5 invert"
            />
          </button>
        ))}
      </div>
    </>
  );
};

export default Toolbar;
