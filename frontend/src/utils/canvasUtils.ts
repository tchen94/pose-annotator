interface KeyPoint {
  x: number | null;
  y: number | null;
  not_visible: boolean;
}

interface BodyPartAnnotations {
  [bodyPart: string]: KeyPoint;
}

export const drawAnnotations = (
  canvas: HTMLCanvasElement,
  frameAnnotation: BodyPartAnnotations,
  videoWidth: number,
  videoHeight: number,
) => {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Calculate scaling factors
  const scaleX = canvas.width / videoWidth;
  const scaleY = canvas.height / videoHeight;

  // Draw each annotation
  Object.entries(frameAnnotation).forEach(([bodyPart, keyPoint]) => {
    if (
      keyPoint &&
      keyPoint.x !== null &&
      keyPoint.y !== null &&
      !keyPoint.not_visible
    ) {
      const canvasX = keyPoint.x * scaleX;
      const canvasY = keyPoint.y * scaleY;

      const color = setColor(bodyPart);

      // Draw circle
      ctx.beginPath();
      ctx.arc(canvasX, canvasY, 5, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  });
};

export const getClickCoordinates = (
  e: React.MouseEvent<HTMLCanvasElement>,
  canvas: HTMLCanvasElement,
  videoWidth: number,
  videoHeight: number,
): { x: number; y: number } => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  // Convert to the original video frame coordinates
  const scaleX = videoWidth / canvas.width;
  const scaleY = videoHeight / canvas.height;

  return {
    x: Math.round(x * scaleX),
    y: Math.round(y * scaleY),
  };
};

const setColor = (bodyPart: string): string => {
  const updatedBodyPart = bodyPart.toLowerCase();

  if (updatedBodyPart.startsWith("left")) {
    return "#ef476f";
  } else if (updatedBodyPart.startsWith("right")) {
    return "#118ab2";
  } else if (updatedBodyPart === "nose") {
    return "#ffd166";
  }

  return "#06d6a0";
};
