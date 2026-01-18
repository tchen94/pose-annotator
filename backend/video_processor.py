from typing import Optional, Union
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
        """Return a string representation of the object."""
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

    def resize(
        self,
        frames: Union[np.ndarray, list[np.ndarray]],
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> np.ndarray:
        """
        Resize a video frame to specified dimensions.

        Parameters
        ----------
        frames : np.ndarray or list[np.ndarray]
            The input frame(s) to resize. Can be a single frame as a NumPy
            array or a list of frames as NumPy arrays.
        width : int, optional
            The target width in pixels. If only width is given, the height is
            calculated to maintain aspect ratio.
        height : int, optional
            The target height in pixels. If only height is given, the width is
            calculated to maintain aspect ratio.

        Returns
        -------
        resized_frames : np.ndarray or list[np.ndarray]
            The resized frame(s) as a NumPy array or list of arrays.

        Notes
        -----
        - If both width and height are given, resizes to exact dimensions
          (may distort if aspect ratio differs).
        - If only one dimension is provided, calculates the other to maintain
          aspect ratio.
        - If neither is provided, returns the original frame unchanged.
        """
        is_list = isinstance(frames, list)
        if not is_list:
            frames = [frames]

        resized_frames = []
        for frame in frames:

            # Get original dimensions
            original_height, original_width = frame.shape[:2]

            if width is None and height is None:
                resized = frame
            else:
                # Calculate missing dimension to maintain aspect ratio
                if width is None:
                    aspect_ratio = original_width / original_height
                    calc_width = int(height * aspect_ratio)
                    resized = cv2.resize(frame, (calc_width, height))
                elif height is None:
                    aspect_ratio = original_width / original_height
                    calc_height = int(width / aspect_ratio)
                    resized = cv2.resize(frame, (width, calc_height))
                else:
                    resized = cv2.resize(frame, (width, height))
            resized_frames.append(resized)
        return resized_frames if is_list else resized_frames[0]

    def crop(
        self,
        frames: Union[np.ndarray, list[np.ndarray]],
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
        frames : np.ndarray
            The input frame(s) to crop.
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
        is_list = isinstance(frames, list)
        if not is_list:
            frames = [frames]

        cropped_frames = []
        for frame in frames:
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

            # Calculate crop coordinates based on cropped_side
            if cropped_side:
                if cropped_side == 'left':
                    x_start = 0
                    y_start = 0
                elif cropped_side == 'right':
                    x_start = frame_width - crop_width
                    y_start = 0
                elif cropped_side == 'top':
                    x_start = 0
                    y_start = 0
                elif cropped_side == 'bottom':
                    x_start = 0
                    y_start = frame_height - crop_height
                else:
                    raise ValueError(
                        f"Invalid cropped_side: {cropped_side}. "
                        f"Must be 'left', 'right', 'top', or 'bottom'.")
            elif from_center:
                x_start = (frame_width - crop_width) // 2
                y_start = (frame_height - crop_height) // 2
            else:
                x_start = 0
                y_start = 0

            x_end = x_start + crop_width
            y_end = y_start + crop_height

            # Perform the crop
            cropped = frame[y_start:y_end, x_start:x_end]
            cropped_frames.append(cropped)

        return cropped_frames if is_list else cropped_frames[0]