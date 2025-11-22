"""Main orchestrator for dual-loop system."""

import threading
import time
import logging
import sys
from queue import Queue, Empty
from typing import Optional, List
import numpy as np
import cv2
from pynput import keyboard

from src.config import (
    REFLEX_LOOP_FPS,
    COGNITIVE_LOOP_TIMEOUT,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    TEST_MODE_QUIET_HAZARDS,
    TEST_MODE_DISABLE_AUDIO,
    SHOW_TRACKING_VISUALIZATION,
)
from src.hardware.camera import CameraHandler
from src.hardware.audio import AudioHandler
from src.reflex_loop.tracker import YOLOTracker
from src.reflex_loop.safety import SafetyMonitor
from src.cognitive_loop.history import HistoryBuffer
from src.cognitive_loop.scene_composer import SceneComposer
from src.cognitive_loop.trajectory import TrajectoryAnalyzer
from src.cognitive_loop.narrator import LLMNarrator
from src.utils.threading import ThreadSafeQueue

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DualLoopSystem:
    """Orchestrates the dual-loop system."""

    def __init__(
        self,
        test_mode: bool = False,
        test_video_path: Optional[str] = None,
        use_camera: bool = False,
    ):
        """
        Initialize dual-loop system.

        Args:
            test_mode: If True, enable test mode features (logging, etc.)
            test_video_path: Path to test video file (if provided, uses video instead of camera)
            use_camera: If True, use camera even in test mode (test_mode + camera)
        """
        self.test_mode = test_mode
        self.running = False

        # Hardware
        self.camera = CameraHandler(
            test_mode=test_mode, test_video_path=test_video_path, use_camera=use_camera
        )
        self.audio = AudioHandler()

        # Tracking and safety
        self.tracker = YOLOTracker()
        self.safety_monitor = SafetyMonitor(CAMERA_WIDTH, CAMERA_HEIGHT)

        # Cognitive components
        self.history_buffer = HistoryBuffer()
        self.scene_composer = SceneComposer()
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.narrator = LLMNarrator()

        # Threading
        self.reflex_queue = ThreadSafeQueue(maxsize=5)
        self.cognitive_queue = ThreadSafeQueue(maxsize=1)
        self.reflex_thread: Optional[threading.Thread] = None
        self.cognitive_thread: Optional[threading.Thread] = None

        # Frame tracking
        self.frame_id = 0
        self.current_frame: Optional[np.ndarray] = None
        self.current_image_name: Optional[str] = (
            None  # For test mode image identification
        )
        self.annotated_frame: Optional[np.ndarray] = None  # For visualization
        self.frame_lock = threading.Lock()

        # Keyboard listener
        self.keyboard_listener: Optional[keyboard.Listener] = None

        # Warning rate limiting
        self.last_warning_time = 0
        self.warning_cooldown = (
            1.0  # Minimum seconds between spoken warnings (reduced for faster response)
        )
        self.last_warned_hazard_id = None  # Track which hazard we last warned about
        self.hazard_warning_cooldown = 3.0  # Don't warn about same hazard for 3 seconds

        # Visualization
        self.show_visualization = SHOW_TRACKING_VISUALIZATION

    def start(self):
        """Start the dual-loop system."""
        logger.info("Starting dual-loop system...")

        # Check Ollama connection
        if not self.narrator.check_connection():
            logger.warning("Ollama not available. Cognitive loop narration may fail.")

        self.running = True

        # Start reflex loop thread
        self.reflex_thread = threading.Thread(target=self._reflex_loop, daemon=True)
        self.reflex_thread.start()

        # Start cognitive loop thread
        self.cognitive_thread = threading.Thread(
            target=self._cognitive_loop, daemon=True
        )
        self.cognitive_thread.start()

        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()

        if self.test_mode:
            logger.info("Dual-loop system started in TEST MODE.")
            if self.camera.using_video:
                logger.info("Using test video file for continuous frame processing.")
            elif self.camera.use_camera or self.camera.cap is not None:
                logger.info("Using camera input with test mode features enabled.")
            else:
                logger.info(
                    "Using test images (consider --test-video or --use-camera for better testing)."
                )
            logger.info("Press Ctrl+C to exit.")
            logger.info("Hazard warnings are reduced in test mode for cleaner output.")
        else:
            logger.info(
                "Dual-loop system started. Press SPACE for narration, ESC to exit."
            )

        # Main loop: capture frames
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.stop()

    def _main_loop(self):
        """Main loop: capture frames and distribute to queues."""
        frame_time = 1.0 / REFLEX_LOOP_FPS

        while self.running:
            start_time = time.time()

            # Read frame
            success, frame, image_name = self.camera.read_frame()
            if not success:
                logger.warning("Failed to read frame")
                time.sleep(0.1)
                continue

            # Update current frame
            with self.frame_lock:
                self.current_frame = frame.copy()
                self.current_image_name = image_name  # Store image name for test mode
                self.frame_id += 1

            # Put frame in reflex queue (non-blocking)
            try:
                self.reflex_queue.put(
                    (self.frame_id, frame.copy(), time.time(), image_name), block=False
                )
            except:
                pass  # Queue full, skip this frame

            # Display visualization in main thread (OpenCV requires main thread)
            if self.show_visualization:
                with self.frame_lock:
                    if self.annotated_frame is not None:
                        try:
                            cv2.imshow(
                                "Describe My Environment - Tracking",
                                self.annotated_frame,
                            )
                            cv2.waitKey(1)  # Non-blocking, just refresh display
                        except Exception as e:
                            logger.debug(f"Error displaying frame: {e}")
                            # Disable visualization if it fails repeatedly
                            pass

            # Sleep to maintain FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

    def _reflex_loop(self):
        """Reflex loop: fast safety monitoring at 30 FPS."""
        logger.info("Reflex loop started")

        while self.running:
            try:
                # Get frame from queue
                item = self.reflex_queue.get(timeout=0.1)
                if item is None:
                    continue

                # Unpack with image_name (may be None in camera mode)
                if len(item) == 4:
                    frame_id, frame, timestamp, image_name = item
                else:
                    frame_id, frame, timestamp = item
                    image_name = None

                # Run tracking with optional visualization
                result = self.tracker.track(
                    frame, frame_id, timestamp, return_annotated=self.show_visualization
                )

                if self.show_visualization:
                    detections, annotated_frame = result
                else:
                    detections, _ = result
                    annotated_frame = None

                # Update history buffer
                for detection in detections:
                    # Use track_id if available, otherwise create hash-based ID
                    if detection.track_id is not None:
                        object_id = detection.track_id
                    else:
                        # Fallback: use hash of box and class for consistent ID
                        object_id = hash(
                            (tuple(detection.box), detection.class_name)
                        ) % (2**31)
                    self.history_buffer.add_detection(object_id, detection)

                # Store annotated frame for main thread to display (OpenCV requires main thread)
                if self.show_visualization and annotated_frame is not None:
                    with self.frame_lock:
                        self.annotated_frame = annotated_frame.copy()

                # Check for hazards
                hazards = self.safety_monitor.check_hazards(
                    detections, self.history_buffer
                )

                # Trigger warning if needed (with rate limiting)
                if self.safety_monitor.should_warn(hazards):
                    warning_msg = self.safety_monitor.get_warning_message(hazards)
                    high_priority = any(h.priority == "high" for h in hazards)

                    # Get the hazard ID (use first high priority hazard, or first hazard)
                    current_hazard_id = None
                    if high_priority:
                        high_priority_hazards = [
                            h for h in hazards if h.priority == "high"
                        ]
                        if high_priority_hazards:
                            current_hazard_id = high_priority_hazards[0].object_id
                    else:
                        if hazards:
                            current_hazard_id = hazards[0].object_id

                    # Check if this is the same hazard we just warned about (before any audio/logging)
                    current_time = time.time()
                    is_same_hazard = (
                        current_hazard_id is not None
                        and current_hazard_id == self.last_warned_hazard_id
                    )

                    # If same hazard and within cooldown, skip entire warning (don't interrupt speech)
                    if is_same_hazard:
                        time_since_last_warning = current_time - self.last_warning_time
                        if time_since_last_warning < self.hazard_warning_cooldown:
                            logger.debug(
                                f"Skipping warning - same hazard still active "
                                f"(last warned {time_since_last_warning:.2f}s ago)"
                            )
                            continue  # Skip this frame's warning entirely

                    # In test mode, include image name and reduce logging noise
                    if self.test_mode and TEST_MODE_QUIET_HAZARDS:
                        # Only log high priority hazards in test mode
                        if (
                            high_priority and frame_id % 30 == 0
                        ):  # Log every 30 frames max
                            img_info = f" [{image_name}]" if image_name else ""
                            logger.info(f"HAZARD (test mode{img_info}): {warning_msg}")
                    else:
                        img_info = (
                            f" [{image_name}]"
                            if (self.test_mode and image_name)
                            else ""
                        )
                        logger.warning(f"HAZARD{img_info}: {warning_msg}")

                    # Audio handling with better rate limiting
                    if not (self.test_mode and TEST_MODE_DISABLE_AUDIO):

                        # Check if object is too close (already very large) - don't beep constantly
                        # This prevents spam when user is close to camera
                        should_beep = True
                        if high_priority:
                            # Check if any hazard object is very large (too close)
                            for hazard in hazards:
                                if hazard.priority == "high":
                                    # Get the detection for this hazard
                                    hazard_obj = self.history_buffer.get_object(
                                        hazard.object_id
                                    )
                                    if hazard_obj:
                                        latest = hazard_obj.get_latest()
                                        if latest:
                                            # If bounding box area is very large (>40% of frame), it's too close
                                            frame_area = (
                                                self.safety_monitor.frame_width
                                                * self.safety_monitor.frame_height
                                            )
                                            area_ratio = latest.area / frame_area
                                            if (
                                                area_ratio > 0.4
                                            ):  # Object takes up >40% of frame (increased threshold)
                                                should_beep = False
                                                logger.debug(
                                                    f"Suppressing beep - object too close (area ratio: {area_ratio:.2f})"
                                                )
                                                break

                        # Beep first (prioritized), then speech provides context
                        # This way users get immediate warning signal, then details
                        if high_priority:
                            # Play beep first for immediate attention
                            if should_beep:
                                # Use longer cooldown for hazard beeps
                                if (
                                    current_time - self.audio.last_hazard_beep_time
                                ) >= self.audio.hazard_beep_cooldown:
                                    logger.info(
                                        f"Playing hazard beep (cooldown: {current_time - self.audio.last_hazard_beep_time:.2f}s)"
                                    )
                                    self.audio.play_beep()
                                    self.audio.last_hazard_beep_time = current_time
                                else:
                                    logger.debug(
                                        f"Beep on cooldown ({current_time - self.audio.last_hazard_beep_time:.2f}s < {self.audio.hazard_beep_cooldown}s)"
                                    )

                            # Then speak warning (will wait for beep to finish)
                            # Only rate limit if we just spoke (avoid immediate repeat)
                            if (
                                current_time - self.last_warning_time
                            ) >= 1.0:  # Reduced to 1 second
                                logger.info(
                                    f"Speaking hazard warning after beep: {warning_msg}"
                                )
                                # Speech will wait for beep to finish automatically
                                self.audio.speak_text(warning_msg, priority=True)
                                self.last_warning_time = current_time
                                # Remember which hazard we warned about
                                self.last_warned_hazard_id = current_hazard_id

                # Cleanup stale objects periodically
                if frame_id % 30 == 0:
                    self.history_buffer.cleanup_stale_objects(frame_id)

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in reflex loop: {e}")

    def _cognitive_loop(self):
        """Cognitive loop: on-demand narration."""
        logger.info("Cognitive loop started")

        while self.running:
            try:
                # Wait for trigger (SPACE key)
                item = self.cognitive_queue.get(timeout=0.5)
                if item is None:
                    continue

                logger.info("Cognitive loop triggered")

                # Get current frame snapshot
                with self.frame_lock:
                    if self.current_frame is None:
                        continue
                    frame = self.current_frame.copy()
                    current_frame_id = self.frame_id
                    current_image_name = self.current_image_name

                # Log which image is being processed (test mode)
                if self.test_mode and current_image_name:
                    logger.info(f"Processing image: {current_image_name}")

                # Step 1: Generate scene description
                scene_description = self.scene_composer.generate_scene_description(
                    frame
                )
                logger.debug(f"Scene: {scene_description}")

                # Step 2: Analyze trajectories
                tracked_objects = self.history_buffer.get_all_objects()
                object_movements = self.trajectory_analyzer.analyze_all_objects(
                    tracked_objects
                )
                logger.debug(f"Movements: {object_movements}")

                # Step 3: Generate narration
                narration = self.narrator.generate_narration_from_components(
                    scene_description, object_movements
                )

                if narration:
                    # Include image name in test mode
                    if self.test_mode and current_image_name:
                        logger.info(f"Narration [{current_image_name}]: {narration}")
                    else:
                        logger.info(f"Narration: {narration}")

                    # Always speak narration from cognitive loop (user requested it)
                    logger.info(f"Speaking narration: {narration[:50]}...")
                    try:
                        self.audio.speak_text(narration, priority=False)
                        logger.info("TTS call completed")
                    except Exception as e:
                        logger.error(f"Failed to call speak_text: {e}")
                        import traceback

                        logger.error(traceback.format_exc())
                else:
                    logger.warning("Failed to generate narration")
                    # Fallback: speak scene description
                    logger.info("Speaking fallback scene description...")
                    self.audio.speak_text(f"Scene: {scene_description}", priority=False)

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in cognitive loop: {e}")

    def _on_key_press(self, key):
        """Handle keyboard input."""
        try:
            if key == keyboard.Key.space:
                # Trigger cognitive loop
                try:
                    self.cognitive_queue.put("trigger", block=False)
                except:
                    pass  # Queue full
            elif key == keyboard.Key.esc:
                # Exit
                self.running = False
        except AttributeError:
            pass

    def stop(self):
        """Stop the dual-loop system."""
        logger.info("Stopping dual-loop system...")
        self.running = False

        # Close visualization window
        if self.show_visualization:
            cv2.destroyAllWindows()

        # Wait for threads
        if self.reflex_thread:
            self.reflex_thread.join(timeout=2.0)
        if self.cognitive_thread:
            self.cognitive_thread.join(timeout=2.0)

        # Stop keyboard listener
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        # Release resources
        self.camera.release()
        self.audio.stop()

        logger.info("Dual-loop system stopped")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Describe My Environment - AI Assistant"
    )
    parser.add_argument(
        "--test", action="store_true", help="Enable test mode features (logging, etc.)"
    )
    parser.add_argument(
        "--test-video",
        type=str,
        default=None,
        help="Path to test video file (if provided, uses video instead of camera)",
    )
    parser.add_argument(
        "--use-camera",
        action="store_true",
        help="Use camera input (works with --test for test mode + camera)",
    )
    args = parser.parse_args()

    # If --test-video is provided, use video. Otherwise, use camera if --use-camera or not in test mode
    use_camera = args.use_camera or (not args.test and args.test_video is None)

    system = DualLoopSystem(
        test_mode=args.test, test_video_path=args.test_video, use_camera=use_camera
    )
    system.start()


if __name__ == "__main__":
    main()
