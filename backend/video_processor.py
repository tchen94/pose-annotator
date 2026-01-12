from typing import Optional
from os import path
import cv2
import numpy as np

class VideoProcessor:
    """A class to process a video for the Pose Annotator."""

    def __init__(
        self,
        video_path: str
    ):
        """Initialize the VideoProcessor instance.

        Attributes
        ----------
        video_path : str
            The path of the input video file.
        """
        self.video_path = video_path
        self.video_file = path.basename(video_path)
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __repr__(self):
        """Return a string representatin of the object."""
        return f"VideoProcessor object for '{self.video_file}' at " \
               f"{self.fps:.2f} Hz"

    def __timestamp_to_frame(self, timestamp: str) -> int:
        """Convert a timestamp ('MM:SS' or 'MM:SS:MS') to a frame number."""
        time_components = timestamp.split(':')
        if len(time_components) > 2:
            ms = int(time_components[2])
            total_seconds = (int(time_components[0]) * 60) + int(
                time_components[1]) + (ms * 0.001)
        else:
            total_seconds = (int(time_components[0]) * 60) + int(
                time_components[1])
        return int(total_seconds * round(self.fps))

    def get_frame(
        self,
        timestamp: Optional[str] = None,
        number: Optional[int] = None
    ) -> np.ndarray:
        """
        Retrieve a specific frame at a given timestamp or frame number.

        Parameters
        ----------
        timestamp : str, optional
            The timestamp in 'MM:SS' or 'MM:SS:MS' format.
        number : int, optional
            The frame index at which a video frame is retrieved.

        Returns
        -------
        frame : np.ndarray
            The requested video frame as a NumPy array.
        """

        if timestamp:
            # Set the video position to the given timestamp
            frame_number = self.__timestamp_to_frame(timestamp)
        else:
            frame_number = number
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError(f"No frame found.")
        return frame

    def crop(
        self,
        frame: np.ndarray,
        width_perc: Optional[float] = None,
        height_perc: Optional[float] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        from_center: bool = True,
        cropped_side: Optional[str] = None
    ) -> np.ndarray:
        """
        Crop a video frame to specified dimensions.

        Parameters
        ----------
        frame : np.ndarray
            The input frame to crop.
        width_perc : float, optional
            The width as a percentage (0 to 1) of the original frame width.
        height_perc : float, optional
            The height as a percentage (0 to 1) of the original frame height.
        width_px : int, optional
            The explicit width in pixels.
        height_px : int, optional
            The explicit height in pixels.
        from_center : bool, optional
            If True, crop from the center. If False, crop from top-left
            corner; by default, True.
        cropped_side : str, optional
            If specified, further crop to 'left', 'right', 'top', or 'bottom'
            half. Only applies when `width_perc` and/or `height_perc` are
            provided.

        Returns
        -------
        cropped_frame : np.ndarray
            The cropped frame as a NumPy array.

        Notes
        -----
        Pixel values take precedence over percentage values if both are
        provided.
        """
        frame_height, frame_width = frame.shape[:2]

        # Calculate crop width
        if width_px is not None:
            crop_width = min(width_px, frame_width)
        elif width_perc is not None:
            crop_width = int(frame_width * width_perc)
        else:
            crop_width = frame_width

        # Calculate crop height
        if height_px is not None:
            crop_height = min(height_px, frame_height)
        elif height_perc is not None:
            crop_height = int(frame_height * height_perc)
        else:
            crop_height = frame_height

        # Calculate crop coordinates
        if from_center:
            x_start = (frame_width - crop_width) // 2
            y_start = (frame_height - crop_height) // 2
        else:
            x_start = 0
            y_start = 0
        x_end = x_start + crop_width
        y_end = y_start + crop_height

        # Perform the initial crop
        cropped_frame = frame[y_start:y_end, x_start:x_end]

        # Apply side cropping if specified (only when using percentages)
        if cropped_side and (
                width_perc is not None or height_perc is not None):
            h, w = cropped_frame.shape[:2]

            if cropped_side == 'left':
                cropped_frame = cropped_frame[:, :w // 2]
            elif cropped_side == 'right':
                cropped_frame = cropped_frame[:, w // 2:]
            elif cropped_side == 'top':
                cropped_frame = cropped_frame[:h // 2, :]
            elif cropped_side == 'bottom':
                cropped_frame = cropped_frame[h // 2:, :]
            else:
                raise ValueError(f"Invalid cropped_side: {cropped_side}. "
                                 f"Must be 'left', 'right', 'top', or 'bottom'.")

        return cropped_frame