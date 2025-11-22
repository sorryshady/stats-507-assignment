"""Camera input handler for iPhone/webcam feed."""

import cv2
import numpy as np
from typing import Optional, Tuple
import os
import glob
from pathlib import Path
import logging

from src.config import CAMERA_DEVICE_ID, CAMERA_FPS, CAMERA_WIDTH, CAMERA_HEIGHT

logger = logging.getLogger(__name__)


class CameraHandler:
    """Handles camera input from iPhone or webcam."""

    def __init__(
        self,
        device_id: int = CAMERA_DEVICE_ID,
        test_mode: bool = False,
        test_video_path: Optional[str] = None,
        test_images_dir: str = "test_images",
        use_camera: bool = False,
    ):
        """
        Initialize camera handler.

        Args:
            device_id: Camera device ID (0 for default webcam)
            test_mode: If True, enable test mode features (logging, etc.)
            test_video_path: Path to test video file (if provided, uses video instead of camera)
            test_images_dir: Directory containing test images (fallback if no video)
            use_camera: If True, use camera even in test mode (test_mode + camera)
        """
        self.device_id = device_id
        self.test_mode = test_mode
        self.test_video_path = test_video_path
        self.test_images_dir = test_images_dir
        self.use_camera = use_camera
        self.cap: Optional[cv2.VideoCapture] = None
        self.test_images: list = []
        self.test_image_index = 0
        self.using_video = False

        # Determine input source
        if test_video_path:
            # Use test video if provided
            self._load_test_video(test_video_path)
        elif use_camera or not test_mode:
            # Use camera if explicitly requested or not in test mode
            self._initialize_camera()
        else:
            # Fallback to test images
            self._load_test_images()

    def _initialize_camera(self):
        """Initialize OpenCV video capture."""
        try:
            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                raise RuntimeError(
                    f"Failed to open camera {self.device_id}. "
                    f"Run 'python list_cameras.py' to find available cameras."
                )

            # Get actual camera properties before setting
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            backend = self.cap.getBackendName()

            # Set desired camera properties (may not always be supported)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

            # Get final properties (may differ from requested)
            final_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            final_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            final_fps = self.cap.get(cv2.CAP_PROP_FPS)

            logger.info(
                f"Camera {self.device_id} initialized: {final_width}x{final_height} @ {final_fps:.1f} FPS "
                f"(Backend: {backend})"
            )

            # Warn if resolution differs significantly (might indicate wrong camera)
            if final_width >= 1920 or final_height >= 1080:
                logger.info(
                    "High resolution detected - this might be iPhone Continuity Camera"
                )
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            logger.info("Tip: Run 'python list_cameras.py' to find available cameras")
            raise

    def _load_test_video(self, video_path: str):
        """Load test video file."""
        video_file = Path(video_path)
        if not video_file.exists():
            logger.error(f"Test video file not found: {video_path}")
            logger.info("Falling back to test images...")
            self._load_test_images()
            return

        self.cap = cv2.VideoCapture(str(video_file))
        if not self.cap.isOpened():
            logger.error(f"Failed to open test video: {video_path}")
            logger.info("Falling back to test images...")
            self._load_test_images()
            return

        self.using_video = True
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"Loaded test video: {video_path}")
        logger.info(f"Video properties: {frame_count} frames @ {fps:.2f} FPS")

    def _load_test_images(self):
        """Load test images from directory (fallback mode)."""
        test_path = Path(self.test_images_dir)
        if not test_path.exists():
            logger.warning(f"Test images directory {self.test_images_dir} not found")
            return

        # Load common image formats
        extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
        for ext in extensions:
            self.test_images.extend(glob.glob(str(test_path / ext)))

        self.test_images.sort()
        logger.info(f"Loaded {len(self.test_images)} test images (fallback mode)")
        logger.warning(
            "Using static images - consider using a video file for better testing"
        )

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """
        Read a frame from camera, test video, or test images.

        Returns:
            Tuple of (success, frame, source_name) where:
            - success: bool indicating if frame was read successfully
            - frame: numpy array or None
            - source_name: str source identifier (video filename, image name, "camera", or None)
        """
        if self.using_video:
            return self._read_test_video_frame()
        elif self.cap is not None:
            # Using camera
            success, frame = self._read_camera_frame()
            source_name = (
                "camera" if self.test_mode else None
            )  # Include source name in test mode
            return success, frame, source_name
        else:
            # Using test images
            return self._read_test_frame()

    def _read_camera_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame from camera."""
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            return False, None

        return True, frame

    def _read_test_video_frame(
        self,
    ) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """Read frame from test video file."""
        if self.cap is None:
            return False, None, None

        ret, frame = self.cap.read()

        if not ret:
            # Video ended, loop back to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

            if not ret:
                logger.warning("Failed to read from test video")
                return False, None, None

        # Get video filename for logging
        video_name = (
            Path(self.test_video_path).name if self.test_video_path else "test_video"
        )
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        # Add frame number to identifier
        source_name = f"{video_name} (frame {current_frame})"

        return True, frame, source_name

    def _read_test_frame(self) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """Read frame from test images (loops through images - fallback mode)."""
        if len(self.test_images) == 0:
            logger.error("No test images available")
            return False, None, None

        img_path = self.test_images[self.test_image_index]
        frame = cv2.imread(img_path)

        if frame is None:
            logger.warning(f"Failed to load test image: {img_path}")
            return False, None, None

        # Get image name for logging
        from pathlib import Path

        image_name = Path(img_path).name

        # Cycle through images
        self.test_image_index = (self.test_image_index + 1) % len(self.test_images)

        # Add small delay to simulate realistic frame rate
        import time

        time.sleep(1.0 / CAMERA_FPS)

        return True, frame, image_name

    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            logger.info("Camera released")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
