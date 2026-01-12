import { useEffect, useRef, useState } from "react";

const VideoPlayer = () => {
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleVideoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setVideoSrc(url);
    }
  };

  useEffect(() => {
    const vid = videoRef.current;
    const canvas = canvasRef.current;

    if (vid && canvas) {
      const updateCanvasSize = () => {
        canvas.width = vid.offsetWidth;
        canvas.height = vid.offsetHeight;
      };
      vid.addEventListener("loadedmetadata", updateCanvasSize);
      window.addEventListener("resize", updateCanvasSize);

      return () => {
        vid.removeEventListener("loadedmetadata", updateCanvasSize);
        window.removeEventListener("resize", updateCanvasSize);
      };
    }
  }, [videoSrc]);

  return (
    <div className="w-[70%] max-w-6xl mx-auto mt-8">
      {videoSrc ? (
        <div className="relative max-h-[80vh]">
          <video
            ref={videoRef}
            className="w-full h-auto max-h-[80vh] rounded-3xl shadow-lg"
            controls
          >
            <source src={videoSrc} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 rounded-3xl pointer-events-none"
            style={{ mixBlendMode: "normal" }}
          />
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-3xl">
          <h3 className="text-xl mb-4">Upload a Video</h3>
          <input
            type="file"
            accept="video/*"
            onChange={handleVideoUpload}
            className="text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
          />
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
