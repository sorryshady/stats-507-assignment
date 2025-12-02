"""Audio output handler for beeps and TTS."""

import queue
import threading
import time
import logging
import sys
import os
from dataclasses import dataclass
from enum import IntEnum

from src.config import (
    BEEP_FREQUENCY,
    BEEP_DURATION,
    TTS_RATE,
    BEEP_COOLDOWN,
    HAZARD_BEEP_COOLDOWN,
)

logger = logging.getLogger(__name__)


class SpeechPriority(IntEnum):
    """Priority levels for speech queue."""

    LOW = 1  # Regular narration
    HIGH = 2  # Hazard warnings


@dataclass(order=True)
class SpeechRequest:
    """Represents a speech request in the queue."""

    priority: int
    text: str
    timestamp: float


class AudioHandler:
    """Handles audio output for safety warnings and narration."""

    def __init__(self):
        """Initialize audio handler."""
        self.tts_engine = None

        self.speech_queue = queue.PriorityQueue()
        self.speech_worker_thread = None
        self.speech_worker_running = False

        self.audio_lock = threading.Lock()
        self.last_beep_time = 0
        self.beep_cooldown = BEEP_COOLDOWN
        self.last_hazard_beep_time = 0
        self.hazard_beep_cooldown = HAZARD_BEEP_COOLDOWN
        self.sounddevice_available = False
        self.beep_playing = False

        self._init_tts()
        self._init_sounddevice()
        self._start_speech_worker()

    def _init_piper_tts(self):
        """Initialize Piper TTS engine (fast, high quality, local)."""
        try:
            import shutil

            piper_path = shutil.which("piper")

            if piper_path:
                logger.info(f"Found Piper TTS executable at: {piper_path}")
                self.use_piper = True
                self.piper_path = piper_path
                self.piper_model = "en_US-lessac-medium.onnx"
                self._ensure_piper_model()
            else:
                try:
                    import piper

                    logger.info("Piper Python package found (placeholder)")
                    self.use_piper = False
                except ImportError:
                    self.use_piper = False
                    logger.info(
                        "Piper TTS not found. Install with: pip install piper-tts or download binary"
                    )
        except Exception as e:
            logger.warning(f"Failed to initialize Piper TTS: {e}")
            self.use_piper = False

    def _ensure_piper_model(self):
        """Ensure a Piper model is available."""
        import os
        import requests

        model_name = "en_US-lessac-medium.onnx"
        json_name = "en_US-lessac-medium.onnx.json"

        if not os.path.exists(model_name):
            logger.info(f"Downloading Piper model: {model_name}...")
            pass

    def _init_tts(self):
        """Initialize pyttsx3 TTS engine (fallback)."""
        try:
            import pyttsx3

            self.tts_engine = pyttsx3.init()

            self.tts_engine.setProperty("rate", TTS_RATE)

            voices = self.tts_engine.getProperty("voices")
            if len(voices) > 0:
                preferred_voice = None
                for voice in voices:
                    voice_name = voice.name.lower()
                    if "enhanced" in voice_name or "premium" in voice_name:
                        preferred_voice = voice.id
                        break
                    if (
                        "female" in voice_name
                        or "samantha" in voice_name
                        or "karen" in voice_name
                    ):
                        preferred_voice = voice.id
                        break

                if preferred_voice:
                    self.tts_engine.setProperty("voice", preferred_voice)
                else:
                    self.tts_engine.setProperty("voice", voices[0].id)

            self.tts_engine.setProperty("volume", 0.9)

            logger.info("pyttsx3 TTS engine initialized (fallback)")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3 TTS engine: {e}")
            self.tts_engine = None

    def _init_sounddevice(self):
        """Try to initialize sounddevice, fallback to system beep if unavailable."""
        try:
            import sounddevice as sd
            import numpy as np

            test_wave = np.sin(2 * np.pi * 440 * np.linspace(0, 0.01, 441))
            sd.play(test_wave, samplerate=44100)
            sd.stop()
            self.sounddevice_available = True
            logger.info("sounddevice initialized successfully")
        except Exception as e:
            logger.warning(
                f"sounddevice not available, using system beep fallback: {e}"
            )
            self.sounddevice_available = False

    def play_beep(
        self, frequency: int = BEEP_FREQUENCY, duration: float = BEEP_DURATION
    ):
        """Play a beep sound for safety warnings."""
        current_time = time.time()
        if current_time - self.last_beep_time < self.beep_cooldown:
            return

        if self.beep_playing:
            logger.debug("Beep already playing, skipping")
            return

        self.last_beep_time = current_time

        def _beep():
            """Generate and play beep in background thread."""
            self.beep_playing = True
            try:
                if self.sounddevice_available:
                    import sounddevice as sd
                    import numpy as np

                    sample_rate = 44100
                    num_samples = int(sample_rate * duration)
                    t = np.linspace(0, duration, num_samples, dtype=np.float32)
                    wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)

                    try:
                        with self.audio_lock:
                            sd.play(wave, samplerate=sample_rate)
                        sd.wait()
                    except Exception as e:
                        logger.debug(f"sounddevice play failed: {e}")
                        self.sounddevice_available = False
                        raise
                else:
                    raise NotImplementedError("Using system beep")
            except Exception:
                try:
                    sys.stdout.write("\a")
                    sys.stdout.flush()
                except Exception:
                    pass
            finally:
                self.beep_playing = False

        thread = threading.Thread(target=_beep, daemon=True)
        thread.start()

    def _start_speech_worker(self):
        """Start the speech worker thread that processes the queue."""
        if self.speech_worker_running:
            return

        self.speech_worker_running = True

        def _speech_worker():
            """Worker thread that processes speech queue sequentially."""
            logger.info("Speech worker thread started")
            while self.speech_worker_running:
                try:
                    request = self.speech_queue.get(timeout=1.0)

                    if self.beep_playing:
                        logger.debug(
                            f"Beep playing, waiting before speaking: {request.text[:50]}..."
                        )
                        max_wait = 0.5
                        wait_time = 0
                        while self.beep_playing and wait_time < max_wait:
                            time.sleep(0.05)
                            wait_time += 0.05

                    priority_name = "HIGH" if request.priority < -1 else "LOW"
                    logger.info(
                        f"Processing speech request (priority={priority_name}): {request.text[:50]}..."
                    )
                    self._process_speech(request.text)

                    self.speech_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in speech worker thread: {e}")
                    import traceback

                    logger.error(traceback.format_exc())

        self.speech_worker_thread = threading.Thread(target=_speech_worker, daemon=True)
        self.speech_worker_thread.start()
        logger.info("Speech worker thread initialized")

    def speak_text(self, text: str, priority: bool = False):
        """Queue text for speech using TTS."""
        if not text or not text.strip():
            logger.warning("Empty text provided to speak_text")
            return

        priority_level = SpeechPriority.HIGH if priority else SpeechPriority.LOW
        queue_priority = -priority_level.value

        request = SpeechRequest(
            priority=queue_priority, text=text, timestamp=time.time()
        )

        try:
            self.speech_queue.put(request, block=False)
            logger.debug(
                f"Queued speech request (priority={priority_level.name}): {text[:50]}..."
            )
        except queue.Full:
            logger.warning("Speech queue is full, dropping request")

    def _process_speech(self, text: str):
        """Process a single speech request using available TTS engine."""
        if sys.platform == "darwin":
            self._speak_system(text)
        elif self.tts_engine is not None:
            self._speak_pyttsx3(text)
        else:
            self._speak_system(text)

    def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3."""
        try:
            import pyttsx3

            if self.tts_engine is None:
                raise RuntimeError("TTS engine not initialized")

            logger.info(f"Speaking with pyttsx3: {text[:80]}...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info("pyttsx3 finished speaking successfully")
        except Exception as e:
            logger.warning(f"pyttsx3 failed: {e}")
            # Fallback to system say
            logger.info("Falling back to system say...")
            self._speak_system(text)

    def _speak_system(self, text: str):
        """Fallback to macOS say command."""
        try:
            import subprocess

            logger.info("Using macOS 'say' command as fallback...")
            subprocess.run(["say", "-v", "Samantha", text], check=True, timeout=30)
            logger.info("System say command completed successfully")
        except subprocess.TimeoutExpired:
            logger.error("System say command timed out")
        except FileNotFoundError:
            logger.error("macOS 'say' command not found")
        except Exception as e:
            logger.error(f"System say command failed: {e}")

    def stop(self):
        """Stop any ongoing audio output and worker thread."""
        self.speech_worker_running = False

        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

        if self.tts_engine is not None:
            try:
                import pyttsx3

                self.tts_engine.stop()
            except Exception:
                pass

        if self.speech_worker_thread is not None:
            self.speech_worker_thread.join(timeout=2.0)
