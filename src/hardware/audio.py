"""Audio output handler for beeps and TTS."""

import pyttsx3
import threading
import time
import logging
import sys
import os

from src.config import BEEP_FREQUENCY, BEEP_DURATION, TTS_RATE, BEEP_COOLDOWN, HAZARD_BEEP_COOLDOWN

logger = logging.getLogger(__name__)


class AudioHandler:
    """Handles audio output for safety warnings and narration."""
    
    def __init__(self):
        """Initialize audio handler."""
        self.tts_engine = None
        self._init_tts()
        self.audio_lock = threading.Lock()
        self.last_beep_time = 0
        self.beep_cooldown = BEEP_COOLDOWN
        self.last_hazard_beep_time = 0  # Track hazard beeps separately
        self.hazard_beep_cooldown = HAZARD_BEEP_COOLDOWN
        self.sounddevice_available = False
        self.tts_speaking = False  # Track if TTS is currently speaking
        self.beep_playing = False  # Track if beep is currently playing
        self._init_sounddevice()
    
    def _init_tts(self):
        """Initialize TTS engine."""
        try:
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
            
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize TTS engine: {e}")
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
            self.beep_playing = True
            try:
                if self.sounddevice_available:
                    import sounddevice as sd
                    import numpy as np
                    # Generate sine wave
                    sample_rate = 44100
                    t = np.linspace(0, duration, int(sample_rate * duration))
                    wave = np.sin(2 * np.pi * frequency * t)
                    # Play sound with error handling
                    try:
                        # Use audio lock to prevent conflicts with TTS
                        with self.audio_lock:
                            sd.play(wave, samplerate=sample_rate)
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
        
        # Play in separate thread to avoid blocking
        thread = threading.Thread(target=_beep, daemon=True)
        thread.start()
    
    def speak_text(self, text: str, priority: bool = False):
        """
        Speak text using TTS with fallback to macOS say command.
        Will wait for beeps to finish before speaking (beeps are prioritized).
        
        Args:
            text: Text to speak
            priority: If True, queues for immediate playback (but doesn't interrupt current speech)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to speak_text")
            return
        
        # Wait for beep to finish if it's playing (beeps are prioritized)
        if self.beep_playing:
            logger.debug(f"Beep playing, waiting before speaking: {text[:50]}...")
            # Wait a bit for beep to finish (beep duration is short)
            import time
            max_wait = 0.5  # Max wait time (beeps are usually ~0.2s)
            wait_time = 0
            while self.beep_playing and wait_time < max_wait:
                time.sleep(0.05)  # Check every 50ms
                wait_time += 0.05
        
        # Check if TTS is currently speaking - skip if busy (even priority messages)
        # This prevents cutting off mid-sentence
        if self.tts_speaking:
            logger.debug(f"TTS busy, skipping message: {text[:50]}...")
            return
        
        # Set flag BEFORE starting thread to prevent race condition
        # Use lock to make this atomic
        with self.audio_lock:
            if self.tts_speaking:
                logger.debug(f"TTS started speaking, skipping: {text[:50]}...")
                return
            self.tts_speaking = True
        
        def _speak_pyttsx3():
            """Try pyttsx3 first."""
            try:
                if self.tts_engine is None:
                    raise RuntimeError("TTS engine not initialized")
                
                logger.info(f"TTS thread started, speaking: {text[:80]}...")
                with self.audio_lock:
                    logger.info(f"Calling TTS engine.say()...")
                    self.tts_engine.say(text)
                    logger.info("Calling TTS engine.runAndWait()...")
                    self.tts_engine.runAndWait()
                    logger.info("TTS finished speaking successfully")
            except Exception as e:
                logger.warning(f"pyttsx3 failed: {e}")
                raise
            finally:
                # Always clear flag when done
                with self.audio_lock:
                    self.tts_speaking = False
        
        def _speak_system():
            """Fallback to macOS say command."""
            try:
                import subprocess
                logger.info("Using macOS 'say' command as fallback...")
                # Use say command with a clear voice
                subprocess.run(
                    ['say', '-v', 'Samantha', text],  # Try Samantha voice, fallback to default
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
            finally:
                # Always clear flag when done
                with self.audio_lock:
                    self.tts_speaking = False
        
        def _speak():
            """Try pyttsx3, fallback to system say."""
            try:
                _speak_pyttsx3()
            except Exception:
                # Fallback to system say command
                logger.warning("Falling back to macOS system 'say' command...")
                _speak_system()
        
        # Run in separate thread to avoid blocking
        logger.info(f"Starting TTS thread for: {text[:50]}...")
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
        logger.info(f"TTS thread started (daemon={thread.daemon})")
    
    def stop(self):
        """Stop any ongoing audio output."""
        if self.tts_engine is not None:
            try:
                self.tts_engine.stop()
            except Exception:
                pass

