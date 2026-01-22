import toast, { Toaster } from "react-hot-toast";
import LeftArrow from "../../assets/left-arrow.svg";
import RightArrow from "../../assets/right-arrow.svg";
import PenAnnotation from "../../assets/pen-annotate.svg";
import Save from "../../assets/save.svg";
import Export from "../../assets/export.svg";
import useVideoContext from "../../providers/useVideoContext";
import { BODY_PART } from "../../constants/constants";
import type { BodyPartAnnotations } from "../../constants/types";
import { useMutation } from "@tanstack/react-query";
import { saveAnnotations } from "../../api/annotations";
import useTokenContext from "../../providers/useTokenContext";

interface CanvasControl {
  label: string;
  className: string;
  icon: string;
  onClick?: () => void;
  active?: boolean;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

  const token = useTokenContext();

  const isFrameComplete = (frame: number) => {
    const frameAnnotations = annotations[frame];

    return Object.values(frameAnnotations).every((annotation) => {
      const { x, y, not_visible } = annotation;
      return (x !== null && y !== null && !not_visible) || not_visible;
    });
  };

  const fetchFrame = async (frame_set_id: string, frameIdx: number) => {
    const response = await fetch(
      `${API_URL}/frame-set/${frame_set_id}/frame?index=${frameIdx}`,
    );
    if (!response.ok) throw new Error("Failed to fetch frame");

    const data = await response.json();
    setCurrentFrame(data.frame_img);
    setCurrentFrameNumber(data.frame_num);
    setCurrentFrameIdx(data.frame_idx);

    // Initalize frame annotations if it doesn't exist
    setAnnotations((prevAnnotations) => {
      // If annotations already exist for this frame, don't overwrite
      if (prevAnnotations[data.frame_num]) {
        return prevAnnotations;
      }

      const frameAnnotations: BodyPartAnnotations = {};
      BODY_PART.forEach((part) => {
        frameAnnotations[part] = { x: null, y: null, not_visible: false };
      });

      return {
        ...prevAnnotations,
        [data.frame_num]: frameAnnotations,
      };
    });
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
      toast.error("Missing annotation(s)");
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

  const { mutate: saveAnnotationsMutation, isPending } = useMutation({
    mutationFn: saveAnnotations,
    onSuccess: () => {
      toast.success("Annotations saved successfully");
    },
    onError: (error) => {
      toast.error("Failed to save annotations");
      console.error(`Error saving annotations: ${error}`);
    },
  });

  const handleSaveAnnotations = async () => {
    if (!videoData) return;

    saveAnnotationsMutation({
      frame_set_id: videoData.frame_set_id,
      video_id: videoData.video_id,
      orig_width: videoData.orig_width,
      orig_height: videoData.orig_height,
      render_width: videoData.render_width,
      render_height: videoData.render_height,
      annotations: annotations,
      last_frame_annotated: currentFrameNumber,
      token: token || undefined,
    });
  };

  const exportVideoAnnotations = async () => {
    // Send annotations to the backend for CSV conversion
    const json = JSON.stringify(annotations);

    try {
      const response = await fetch(`${API_URL}/annotations/export-csv`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: json,
      });

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
      className: "px-4 py-2 bg-[#B8E6D5] rounded hover:bg-[#A3D9C7]",
      icon: LeftArrow,
      onClick: handleStepBack,
    },
    {
      label: "Step Forward",
      className: "px-4 py-2 bg-[#B8E6D5] rounded hover:bg-[#A3D9C7]",
      icon: RightArrow,
      onClick: handleStepForward,
    },
    {
      label: "Annotate",
      className: annotationMode
        ? "px-4 py-2 bg-[#A3D9C7] rounded ring-2 ring-red shadow-lg shadow-red-200/50"
        : "px-4 py-2 bg-[#B8E6D5] rounded hover:bg-[#A3D9C7]",
      icon: PenAnnotation,
      onClick: handleToggleAnnotationMode,
      active: annotationMode,
    },
    {
      label: "Save",
      className: `px-4 py-2 bg-[#B8E6D5] rounded hover:bg-[#A3D9C7] ${isPending ? "opacity-50" : ""}`,
      icon: Save,
      onClick: handleSaveAnnotations,
    },
    {
      label: "Export",
      className: "px-4 py-2 bg-[#B8E6D5] rounded hover:bg-[#A3D9C7]",
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
            <img src={control.icon} alt={control.label} className="w-5 h-5" />
          </button>
        ))}
      </div>
    </>
  );
};

export default Toolbar;
