"""Main orchestrator for dual-loop system."""

import threading
import time
import logging
import sys
import os
from datetime import datetime
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
    VISUAL_WARNING_PERSISTENCE_DURATION,
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
        camera_id: Optional[int] = None,
    ):
        """Initialize dual-loop system."""
        self.test_mode = test_mode
        self.running = False

        from src.config import CAMERA_DEVICE_ID

        device_id = camera_id if camera_id is not None else CAMERA_DEVICE_ID
        self.camera = CameraHandler(
            test_mode=test_mode,
            test_video_path=test_video_path,
            use_camera=use_camera,
            device_id=device_id,
        )
        self.audio = AudioHandler()

        self.tracker = YOLOTracker()
        self.safety_monitor = SafetyMonitor(CAMERA_WIDTH, CAMERA_HEIGHT)

        self.history_buffer = HistoryBuffer()
        self.scene_composer = SceneComposer()
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.narrator = LLMNarrator()

        self.reflex_queue = ThreadSafeQueue(maxsize=5)
        self.cognitive_queue = ThreadSafeQueue(maxsize=1)
        self.reflex_thread: Optional[threading.Thread] = None
        self.cognitive_thread: Optional[threading.Thread] = None

        self.frame_id = 0
        self.current_frame: Optional[np.ndarray] = None
        self.current_image_name: Optional[str] = None
        self.annotated_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()

        self.keyboard_listener: Optional[keyboard.Listener] = None

        self.last_warning_time = 0
        self.warning_cooldown = 1.0
        self.last_warned_hazard_id = None
        self.hazard_warning_cooldown = 3.0
        from src.config import GLOBAL_WARNING_COOLDOWN

        self.global_warning_cooldown = GLOBAL_WARNING_COOLDOWN

        self.show_visualization = SHOW_TRACKING_VISUALIZATION

        self.last_hazard_detection_time = 0.0
        self.visual_warning_duration = VISUAL_WARNING_PERSISTENCE_DURATION

        self.video_writer: Optional[cv2.VideoWriter] = None
        self.record_video = False
        self.video_output_path: Optional[str] = None
        self.video_width: int = 0
        self.video_height: int = 0

    def start(self, record_video: bool = False):
        """Start the dual-loop system."""
        logger.info("Starting dual-loop system...")

        if not self.narrator.check_connection():
            logger.warning("Ollama not available. Cognitive loop narration may fail.")

        if record_video:
            self._init_video_recording()

        self.running = True

        self.reflex_thread = threading.Thread(target=self._reflex_loop, daemon=True)
        self.reflex_thread.start()

        self.cognitive_thread = threading.Thread(
            target=self._cognitive_loop, daemon=True
        )
        self.cognitive_thread.start()

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

            success, frame, image_name = self.camera.read_frame()
            if not success:
                logger.warning("Failed to read frame")
                time.sleep(0.1)
                continue

            with self.frame_lock:
                self.current_frame = frame.copy()
                self.current_image_name = image_name
                self.frame_id += 1

            try:
                self.reflex_queue.put(
                    (self.frame_id, frame.copy(), time.time(), image_name), block=False
                )
            except:
                pass

            if self.show_visualization:
                with self.frame_lock:
                    if self.annotated_frame is not None:
                        try:
                            cv2.imshow(
                                "Describe My Environment - Tracking",
                                self.annotated_frame,
                            )
                            cv2.waitKey(1)

                            if self.record_video and self.video_writer is not None:
                                frame_to_write = self.annotated_frame
                                h, w = frame_to_write.shape[:2]
                                if (w, h) != (self.video_width, self.video_height):
                                    frame_to_write = cv2.resize(
                                        frame_to_write,
                                        (self.video_width, self.video_height),
                                    )
                                self.video_writer.write(frame_to_write)
                        except Exception as e:
                            logger.debug(f"Error displaying frame: {e}")
                            pass

            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

    def _reflex_loop(self):
        """Reflex loop: fast safety monitoring at 30 FPS."""
        logger.info("Reflex loop started")

        while self.running:
            try:
                item = self.reflex_queue.get(timeout=0.1)
                if item is None:
                    continue

                if len(item) == 4:
                    frame_id, frame, timestamp, image_name = item
                else:
                    frame_id, frame, timestamp = item
                    image_name = None

                result = self.tracker.track(
                    frame, frame_id, timestamp, return_annotated=self.show_visualization
                )

                if self.show_visualization:
                    detections, annotated_frame = result
                else:
                    detections, _ = result
                    annotated_frame = None

                for detection in detections:
                    if detection.track_id is not None:
                        object_id = detection.track_id
                    else:
                        object_id = hash(
                            (tuple(detection.box), detection.class_name)
                        ) % (2**31)
                    self.history_buffer.add_detection(object_id, detection)

                hazards = self.safety_monitor.check_hazards(
                    detections, self.history_buffer
                )

                current_time = time.time()
                if hazards:
                    self.last_hazard_detection_time = current_time

                time_since_last_hazard = current_time - self.last_hazard_detection_time
                should_show_warning = (
                    hazards or time_since_last_hazard < self.visual_warning_duration
                )

                if (
                    should_show_warning
                    and self.show_visualization
                    and annotated_frame is not None
                ):
                    cv2.putText(
                        annotated_frame,
                        "HAZARD DETECTED",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3,
                    )

                if self.show_visualization and annotated_frame is not None:
                    with self.frame_lock:
                        self.annotated_frame = annotated_frame.copy()

                if self.safety_monitor.should_warn(hazards):
                    current_time = time.time()

                    time_since_last_warning = current_time - self.last_warning_time
                    if time_since_last_warning < self.global_warning_cooldown:
                        logger.debug(
                            f"Skipping warning - global cooldown active "
                            f"(last warning {time_since_last_warning:.2f}s ago, need {self.global_warning_cooldown}s)"
                        )
                        continue

                    warning_msg = self.safety_monitor.get_warning_message(hazards)
                    high_priority = any(h.priority == "high" for h in hazards)

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

                    is_same_hazard = (
                        current_hazard_id is not None
                        and current_hazard_id == self.last_warned_hazard_id
                    )

                    if is_same_hazard:
                        if time_since_last_warning < self.hazard_warning_cooldown:
                            logger.debug(
                                f"Skipping warning - same hazard still active "
                                f"(last warned {time_since_last_warning:.2f}s ago)"
                            )
                            continue

                    if self.test_mode and TEST_MODE_QUIET_HAZARDS:
                        if high_priority and frame_id % 30 == 0:
                            img_info = f" [{image_name}]" if image_name else ""
                            logger.info(f"HAZARD (test mode{img_info}): {warning_msg}")
                    else:
                        img_info = (
                            f" [{image_name}]"
                            if (self.test_mode and image_name)
                            else ""
                        )
                        logger.warning(f"HAZARD{img_info}: {warning_msg}")

                    if not (self.test_mode and TEST_MODE_DISABLE_AUDIO):

                        should_beep = True
                        if high_priority:
                            for hazard in hazards:
                                if hazard.priority == "high":
                                    hazard_obj = self.history_buffer.get_object(
                                        hazard.object_id
                                    )
                                    if hazard_obj:
                                        latest = hazard_obj.get_latest()
                                        if latest:
                                            frame_area = (
                                                self.safety_monitor.frame_width
                                                * self.safety_monitor.frame_height
                                            )
                                            area_ratio = latest.area / frame_area
                                            if area_ratio > 0.4:
                                                should_beep = False
                                                logger.debug(
                                                    f"Suppressing beep - object too close (area ratio: {area_ratio:.2f})"
                                                )
                                                break

                        if high_priority:
                            if should_beep:
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

                            logger.info(
                                f"Speaking hazard warning after beep: {warning_msg}"
                            )
                            self.audio.speak_text(warning_msg, priority=True)
                            self.last_warning_time = current_time
                            self.last_warned_hazard_id = current_hazard_id

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
                item = self.cognitive_queue.get(timeout=0.5)
                if item is None:
                    continue

                logger.info("Cognitive loop triggered")

                with self.frame_lock:
                    if self.current_frame is None:
                        continue
                    frame = self.current_frame.copy()
                    current_frame_id = self.frame_id
                    current_image_name = self.current_image_name

                if self.test_mode and current_image_name:
                    logger.info(f"Processing image: {current_image_name}")

                scene_description = self.scene_composer.generate_scene_description(
                    frame
                )
                logger.debug(f"Scene: {scene_description}")

                tracked_objects = self.history_buffer.get_all_objects()
                object_movements = self.trajectory_analyzer.analyze_all_objects(
                    tracked_objects
                )
                logger.debug(f"Movements: {object_movements}")

                if self.test_mode:
                    logger.info("--- INPUTS TO LLM ---")
                    logger.info(f"Scene Description: {scene_description}")
                    if object_movements:
                        logger.info("Detected Objects & Movements:")
                        for mv in object_movements:
                            logger.info(f"  - {mv}")
                    else:
                        logger.info("Detected Objects: None")
                    logger.info("---------------------")

                narration = self.narrator.generate_narration_from_components(
                    scene_description, object_movements
                )

                if narration:
                    if self.test_mode and current_image_name:
                        logger.info(f"Narration [{current_image_name}]: {narration}")
                    else:
                        logger.info(f"Narration: {narration}")

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
                    logger.info("Speaking fallback scene description...")
                    self.audio.speak_text(f"Scene: {scene_description}", priority=False)

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in cognitive loop: {e}")

    def _init_video_recording(self):
        """Initialize video recording to demo/ folder."""
        demo_dir = "demo"
        os.makedirs(demo_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"demo_{timestamp}.mp4"
        self.video_output_path = os.path.join(demo_dir, filename)

        frame_width = CAMERA_WIDTH
        frame_height = CAMERA_HEIGHT

        if self.camera.cap is not None:
            actual_width = int(self.camera.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_width > 0 and actual_height > 0:
                frame_width = actual_width
                frame_height = actual_height
                logger.info(f"Using camera dimensions: {frame_width}x{frame_height}")

        self.video_width = frame_width
        self.video_height = frame_height

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(
            self.video_output_path,
            fourcc,
            REFLEX_LOOP_FPS,
            (frame_width, frame_height),
        )

        if self.video_writer.isOpened():
            self.record_video = True
            logger.info(
                f"Video recording started: {self.video_output_path} ({frame_width}x{frame_height} @ {REFLEX_LOOP_FPS} FPS)"
            )
        else:
            logger.error("Failed to initialize video writer")
            self.video_writer = None
            self.record_video = False

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

        if self.audio:
            self.audio.stop()

        if self.show_visualization:
            cv2.destroyAllWindows()

        if self.reflex_thread:
            self.reflex_thread.join(timeout=2.0)
        if self.cognitive_thread:
            self.cognitive_thread.join(timeout=2.0)

        if self.keyboard_listener:
            self.keyboard_listener.stop()

        self.camera.release()
        self.audio.stop()

        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            if self.video_output_path:
                logger.info(f"Video saved to: {self.video_output_path}")

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
    parser.add_argument(
        "--camera-id",
        type=int,
        default=None,
        help="Camera device ID (overrides CAMERA_DEVICE_ID from config). "
        "Run 'python list_cameras.py' to find available cameras.",
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="Record annotated video output to demo/ folder",
    )
    args = parser.parse_args()

    # If --test-video is provided, use video. Otherwise, use camera if --use-camera or not in test mode
    use_camera = args.use_camera or (not args.test and args.test_video is None)

    # Use camera ID from command line if provided, otherwise use config default
    from src.config import CAMERA_DEVICE_ID

    camera_id = args.camera_id if args.camera_id is not None else CAMERA_DEVICE_ID

    system = DualLoopSystem(
        test_mode=args.test,
        test_video_path=args.test_video,
        use_camera=use_camera,
        camera_id=camera_id,
    )
    system.start(record_video=args.record)


if __name__ == "__main__":
    main()
