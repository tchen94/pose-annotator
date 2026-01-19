import React, { useEffect, useRef, useState } from "react";
import useVideoContext from "../../providers/useVideoContext";
import Toolbar from "../Toolbar/Toolbar";
import { drawAnnotations, getClickCoordinates } from "../../utils/canvasUtils";
import AnnotationToolTip from "../AnnotationToolTip/AnnotationToolTip";
import { BODY_PART } from "../../constants/constants";
import type { BodyPartAnnotations } from "../../constants/types";
import AlertIcon from "../../assets/alert.svg";

interface Coordinates {
  x: number;
  y: number;
}

const VideoPlayer = () => {
  const {
    videoData,
    setVideoData,
    setFrames,
    currentFrame,
    setCurrentFrame,
    setCurrentFrameIdx,
    currentFrameNumber,
    setCurrentFrameNumber,
    annotationMode,
    annotations,
    setAnnotations,
  } = useVideoContext();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [numOfFrames, setNumOfFrames] = useState<number>(50);
  const [tooltipPos, setTooltipPos] = useState<Coordinates | null>(null);
  const [pendingAnnotation, setPendingAnnotation] =
    useState<Coordinates | null>(null);
  const [selectedBodyPart, setSelectedBodyPart] = useState<string>("");

  /**********************\
   *  VIDEO UPLOAD SECTION
   \*********************/

  const handleVideoUpload = async () => {
    if (!selectedFile) return;

    const form = new FormData();
    form.append("video", selectedFile);
    form.append("num_frames", numOfFrames.toString());

    const response = await fetch("http://localhost:8000/frame-set", {
      method: "POST",
      body: form,
    });
    if (!response.ok) throw new Error("Failed to upload video");

    const data = await response.json();
    setVideoData(data);
    setFrames(data.frame_numbers);

    setCurrentFrame(data.first_frame.frame_img);
    setCurrentFrameIdx(data.first_frame.frame_idx);
    setCurrentFrameNumber(data.first_frame.frame_num);

    // Initialize the annotations with video dimensions
    const firstFrameAnnotations: BodyPartAnnotations = {};
    BODY_PART.forEach((part) => {
      firstFrameAnnotations[part] = { x: null, y: null, not_visible: false };
    });

    setAnnotations({
      ...annotations,
      [data.first_frame.frame_num]: firstFrameAnnotations,
      orig_width: data.orig_width,
      orig_height: data.orig_height,
      render_width: data.render_width,
      render_height: data.render_height,
    });
  };

  // Set the canvas size to match the frame size
  useEffect(() => {
    const canvas = canvasRef.current;
    const img = imgRef.current;

    if (img && canvas) {
      const updateCanvasSize = () => {
        canvas.width = img.clientWidth;
        canvas.height = img.clientHeight;

        // Redraw annotations after resizing
        if (videoData) {
          drawAnnotations(
            canvas,
            annotations[currentFrameNumber] || {},
            videoData.render_width,
            videoData.render_height,
          );
        }
      };

      if (img.complete) updateCanvasSize();

      img.addEventListener("load", updateCanvasSize);
      window.addEventListener("resize", updateCanvasSize);

      return () => {
        img.removeEventListener("load", updateCanvasSize);
        window.removeEventListener("resize", updateCanvasSize);
      };
    }
  }, [videoData, annotations, currentFrameNumber]);

  /*******************\
   * ANNOTATION SECTION
  \*******************/

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!annotationMode || !videoData) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const { x, y } = getClickCoordinates(
      e,
      canvas,
      videoData.render_width,
      videoData.render_height,
    );

    // Store the pending annotation
    setPendingAnnotation({ x, y });

    // Show tooltip near the cursor
    setTooltipPos({
      x: e.clientX,
      y: e.clientY,
    });

    // Reset dropdown selection
    setSelectedBodyPart("");
  };

  const handleConfirmAnnotation = () => {
    if (!pendingAnnotation || !selectedBodyPart) return;

    // Add the annotation
    setAnnotations({
      ...annotations,
      [currentFrameNumber]: {
        ...annotations[currentFrameNumber],
        [selectedBodyPart]: {
          x: pendingAnnotation.x,
          y: pendingAnnotation.y,
          not_visible: false,
        },
      },
    });

    setTooltipPos(null);
    setPendingAnnotation(null);
    setSelectedBodyPart("");
  };

  const handleCancelAnnotation = () => {
    setTooltipPos(null);
    setPendingAnnotation(null);
    setSelectedBodyPart("");
  };

  // Redraw annotations when they change
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas && videoData) {
      drawAnnotations(
        canvas,
        annotations[currentFrameNumber] || {},
        videoData.render_width,
        videoData.render_height,
      );
    }
  }, [annotations, videoData, currentFrameNumber]);

  return (
    <div className="flex-1 mx-auto px-6">
      {videoData ? (
        <>
          <div className="relative mt-8 mx-auto w-fit leading-[0]">
            <img
              src={`data:image/jpeg;base64,${currentFrame}`}
              alt={`Frame ${currentFrameNumber}`}
              className="h-auto max-h-[90vh] shadow-lg"
              ref={imgRef}
            />
            <canvas
              ref={canvasRef}
              onMouseUp={handleMouseUp}
              className="absolute top-0 left-0"
              style={{
                mixBlendMode: "normal",
                pointerEvents: annotationMode ? "auto" : "none",
                cursor: annotationMode ? "crosshair" : "default",
              }}
            />
          </div>
          {tooltipPos && (
            <div
              className="absolute z-50"
              style={{
                left: `${tooltipPos.x}px`,
                top: `${tooltipPos.y}px`,
              }}
            >
              <AnnotationToolTip
                selectedBodyPart={selectedBodyPart}
                setSelectedBodyPart={setSelectedBodyPart}
                handleConfirmAnnotation={handleConfirmAnnotation}
                handleCancelAnnotation={handleCancelAnnotation}
                bodyParts={BODY_PART}
              />
            </div>
          )}
          <div className="mt-4 flex justify-center">
            <Toolbar />
          </div>
          <div className="text-white py-4 ml-4 flex justify-center items-center gap-2 px-2">
            <img
              src={AlertIcon}
              alt="alert"
              className="w-6 h-6 flex-shrink-0"
            />
            <span>
              Label keypoints from the subject's perspective. Their left = your
              right.
            </span>
          </div>
        </>
      ) : (
        <div className="flex items-center justify-center h-full">
          <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-3xl w-full max-w-lg">
            <h3 className="text-2xl mb-16 font-bold">Upload a Video</h3>

            <div className="w-fit mb-8 mx-auto">
              <div className="flex items-center justify-center gap-1 mr-4">
                <label className=" text-md w-[150px] mb-2">
                  Select Video File:
                </label>
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="text-md text-gray-500 max-w-[275px]
            file:mr-3 file:py-2 file:px-2
            file:rounded-full file:border-0
            file:text-md file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100 truncate"
                />
              </div>
            </div>

            <div className="w-fit mx-auto">
              <div className="flex items-center justify-center gap-1 mr-54 gap-4">
                <label className="text-md w-[150px] mb-2 whitespace-nowrap">
                  Number of Frames:
                </label>
                <input
                  type="number"
                  value={numOfFrames === 0 ? "" : numOfFrames}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === "") {
                      setNumOfFrames(0);
                    } else {
                      setNumOfFrames(parseInt(value));
                    }
                  }}
                  className="px-2 py-1 border border-gray-300 rounded-lg w-[60px]"
                />
              </div>
              <div className="h-6 mt-4">
                {numOfFrames <= 0 && (
                  <span className="text-red-500 text-sm block text-center">
                    Please enter a number greater than 0.
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={handleVideoUpload}
              disabled={
                !selectedFile || (numOfFrames <= 0 && selectedFile !== null)
              }
              className="w-[50%] px-6 py-3 mt-6 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-progress transition-colors"
            >
              Upload
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
