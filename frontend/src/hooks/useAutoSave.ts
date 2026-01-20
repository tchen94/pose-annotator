import { useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import useVideoContext from "../providers/useVideoContext";
import useTokenContext from "../providers/useTokenContext";

const AUTOSAVE_DELAY = 3000;
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const useAutoSave = () => {
  const { videoData, annotations, currentFrameNumber } = useVideoContext();
  const token = useTokenContext();
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSavedRef = useRef<string>("");

  const { mutate: autoSave } = useMutation({
    mutationFn: async (payload: any) => {
      const response = await fetch(`${API_URL}/annotations/auto-save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Auto-save failed");
      return response.json();
    },
    onSuccess: () => {
      console.log("Auto-save successful");
    },
    onError: (error) => {
      console.error("Auto-save error:", error);
    },
  });

  useEffect(() => {
    if (!videoData || !currentFrameNumber) return;

    const currentAnnotations = annotations[currentFrameNumber];
    const currentState = JSON.stringify(currentAnnotations);

    // Only autosave if something changed
    if (currentState === lastSavedRef.current) return;

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set a new timeout for auto save
    timeoutRef.current = setTimeout(async () => {
      autoSave({
        frame_set_id: videoData.frame_set_id,
        video_id: videoData.video_id,
        frame_num: currentFrameNumber,
        annotations: currentAnnotations,
        orig_width: videoData.orig_width,
        orig_height: videoData.orig_height,
        render_width: videoData.render_width,
        render_height: videoData.render_height,
        total_frames: videoData.count,
        last_frame_annotated: currentFrameNumber,
        token: token,
      });

      lastSavedRef.current = currentState;
    }, AUTOSAVE_DELAY);

    // Cleanup function to clear timeout if component unmounts or dependencies change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [annotations, currentFrameNumber, videoData, autoSave]);
};

export default useAutoSave;
