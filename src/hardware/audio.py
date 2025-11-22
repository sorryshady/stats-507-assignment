"""Audio output handler for beeps and TTS."""

import queue
import threading
import time
import logging
import sys
import os
from dataclasses import dataclass
from enum import IntEnum

from src.config import BEEP_FREQUENCY, BEEP_DURATION, TTS_RATE, BEEP_COOLDOWN, HAZARD_BEEP_COOLDOWN

logger = logging.getLogger(__name__)


class SpeechPriority(IntEnum):
    """Priority levels for speech queue."""
    LOW = 1  # Regular narration
    HIGH = 2  # Hazard warnings


@dataclass
class SpeechRequest:
    """Represents a speech request in the queue."""
    text: str
    priority: SpeechPriority
    timestamp: float


class AudioHandler:
    """Handles audio output for safety warnings and narration."""
    
    def __init__(self):
        """Initialize audio handler."""
        self.tts_engine = None
        
        # Queue system for speech
        self.speech_queue = queue.PriorityQueue()  # Lower number = higher priority
        self.speech_worker_thread = None
        self.speech_worker_running = False
        
        self.audio_lock = threading.Lock()
        self.last_beep_time = 0
        self.beep_cooldown = BEEP_COOLDOWN
        self.last_hazard_beep_time = 0  # Track hazard beeps separately
        self.hazard_beep_cooldown = HAZARD_BEEP_COOLDOWN
        self.sounddevice_available = False
        self.beep_playing = False  # Track if beep is currently playing
        
        # Initialize TTS (pyttsx3)
        self._init_tts()
        
        self._init_sounddevice()
        
        # Start speech worker thread
        self._start_speech_worker()
    
    def _init_piper_tts(self):
        """Initialize Piper TTS engine (fast, high quality, local)."""
        try:
            # We'll use a subprocess to call piper CLI if installed
            # Or use the python bindings if available
            import shutil
            
            # Check for piper executable
            piper_path = shutil.which("piper")
            
            if piper_path:
                logger.info(f"Found Piper TTS executable at: {piper_path}")
                self.use_piper = True
                self.piper_path = piper_path
                # We need a model - check if one exists or download one
                self.piper_model = "en_US-lessac-medium.onnx"
                self._ensure_piper_model()
            else:
                # Try python package
                try:
                    import piper
                    logger.info("Piper Python package found (placeholder)")
                    # The python package might differ in usage, stick to CLI if possible
                    self.use_piper = False 
                except ImportError:
                    self.use_piper = False
                    logger.info("Piper TTS not found. Install with: pip install piper-tts or download binary")
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
            # Download model logic here (simplified for now)
            # For now, we'll assume user needs to download it or we provide instructions
            pass

    def _init_tts(self):
        """Initialize pyttsx3 TTS engine (fallback)."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Set speech rate (faster = more natural)
            self.tts_engine.setProperty('rate', TTS_RATE)
            
            # Try to find a better quality voice
            voices = self.tts_engine.getProperty('voices')
            if len(voices) > 0:
                # Prefer female voices or higher quality voices
                # On macOS, look for enhanced voices
                preferred_voice = None
                for voice in voices:
                    voice_name = voice.name.lower()
                    # Prefer enhanced or high-quality voices
                    if 'enhanced' in voice_name or 'premium' in voice_name:
                        preferred_voice = voice.id
                        break
                    # Or prefer female voices (often sound more natural)
                    if 'female' in voice_name or 'samantha' in voice_name or 'karen' in voice_name:
                        preferred_voice = voice.id
                        break
                
                if preferred_voice:
                    self.tts_engine.setProperty('voice', preferred_voice)
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set volume (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.9)
            
            logger.info("pyttsx3 TTS engine initialized (fallback)")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3 TTS engine: {e}")
            self.tts_engine = None
    
    def _init_sounddevice(self):
        """Try to initialize sounddevice, fallback to system beep if unavailable."""
        try:
            import sounddevice as sd
            import numpy as np
            # Test if sounddevice works
            test_wave = np.sin(2 * np.pi * 440 * np.linspace(0, 0.01, 441))
            sd.play(test_wave, samplerate=44100)
            sd.stop()
            self.sounddevice_available = True
            logger.info("sounddevice initialized successfully")
        except Exception as e:
            logger.warning(f"sounddevice not available, using system beep fallback: {e}")
            self.sounddevice_available = False
    
    def play_beep(self, frequency: int = BEEP_FREQUENCY, duration: float = BEEP_DURATION):
        """
        Play a beep sound for safety warnings.
        Beeps are prioritized - they play immediately and TTS will wait.
        Optimized to avoid frame stutter by doing all work in background thread.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
        """
        # Rate limiting: don't beep too frequently
        current_time = time.time()
        if current_time - self.last_beep_time < self.beep_cooldown:
            return
        
        # Don't beep if already beeping
        if self.beep_playing:
            logger.debug("Beep already playing, skipping")
            return
        
        self.last_beep_time = current_time
        
        def _beep():
            """Generate and play beep in background thread to avoid blocking."""
            self.beep_playing = True
            try:
                if self.sounddevice_available:
                    import sounddevice as sd
                    import numpy as np
                    # Generate sine wave in thread (moved here to avoid blocking main thread)
                    sample_rate = 44100
                    num_samples = int(sample_rate * duration)
                    # Use more efficient array generation with float32
                    t = np.linspace(0, duration, num_samples, dtype=np.float32)
                    wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)
                    
                    # Play sound without holding lock during wait (lock only for play call)
                    try:
                        # Only lock during the play() call, not during wait()
                        with self.audio_lock:
                            sd.play(wave, samplerate=sample_rate)
                        # Wait outside lock to avoid blocking TTS unnecessarily
                        sd.wait()
                    except Exception as e:
                        logger.debug(f"sounddevice play failed: {e}")
                        self.sounddevice_available = False
                        raise
                else:
                    # Fallback: system beep (works on macOS/Linux)
                    raise NotImplementedError("Using system beep")
            except Exception:
                # Fallback: system beep
                try:
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                except Exception:
                    pass  # Silent failure if even system beep fails
            finally:
                self.beep_playing = False
        
        # Play in separate thread to avoid blocking main/reflex loop
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
                    # Get next speech request (blocks until available)
                    # PriorityQueue returns lowest priority value first
                    # Format: (priority_value, request)
                    priority_value, request = self.speech_queue.get(timeout=1.0)
                    
                    # Wait for beep to finish if it's playing (beeps are prioritized)
                    if self.beep_playing:
                        logger.debug(f"Beep playing, waiting before speaking: {request.text[:50]}...")
                        max_wait = 0.5  # Max wait time (beeps are usually ~0.2s)
                        wait_time = 0
                        while self.beep_playing and wait_time < max_wait:
                            time.sleep(0.05)  # Check every 50ms
                            wait_time += 0.05
                    
                    # Process the speech request
                    logger.info(f"Processing speech request (priority={request.priority.name}): {request.text[:50]}...")
                    self._process_speech(request.text)
                    
                    # Mark task as done
                    self.speech_queue.task_done()
                    
                except queue.Empty:
                    # Timeout - check if we should continue
                    continue
                except Exception as e:
                    logger.error(f"Error in speech worker thread: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
        
        self.speech_worker_thread = threading.Thread(target=_speech_worker, daemon=True)
        self.speech_worker_thread.start()
        logger.info("Speech worker thread initialized")
    
    def speak_text(self, text: str, priority: bool = False):
        """
        Queue text for speech using TTS.
        Speech requests are queued and processed sequentially.
        
        Args:
            text: Text to speak
            priority: If True, uses HIGH priority (hazard warnings), otherwise LOW (narration)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to speak_text")
            return
        
        # Determine priority level
        priority_level = SpeechPriority.HIGH if priority else SpeechPriority.LOW
        
        # Create speech request
        request = SpeechRequest(
            text=text,
            priority=priority_level,
            timestamp=time.time()
        )
        
        # Add to queue (lower number = higher priority, so HIGH=2 comes before LOW=1)
        # We invert priority so HIGH priority gets lower queue number
        queue_priority = -priority_level.value
        
        try:
            self.speech_queue.put((queue_priority, request), block=False)
            logger.debug(f"Queued speech request (priority={priority_level.name}): {text[:50]}...")
        except queue.Full:
            logger.warning("Speech queue is full, dropping request")
    
    def _process_speech(self, text: str):
        """Process a single speech request using available TTS engine."""
        if self.tts_engine is not None:
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
            subprocess.run(
                ['say', '-v', 'Samantha', text],
                check=True,
                timeout=30
            )
            logger.info("System say command completed successfully")
        except subprocess.TimeoutExpired:
            logger.error("System say command timed out")
        except FileNotFoundError:
            logger.error("macOS 'say' command not found")
        except Exception as e:
            logger.error(f"System say command failed: {e}")
    
    def stop(self):
        """Stop any ongoing audio output and worker thread."""
        # Stop speech worker
        self.speech_worker_running = False
        
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        
        # Stop TTS engines
        if self.tts_engine is not None:
            try:
                import pyttsx3
                self.tts_engine.stop()
            except Exception:
                pass
        
        # Wait for worker thread to finish
        if self.speech_worker_thread is not None:
            self.speech_worker_thread.join(timeout=2.0)

