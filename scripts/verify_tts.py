"""Verify TTS (Text-to-Speech) setup and functionality."""

import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_system_audio_output():
    """Test macOS system audio output using say command."""
    print("\n" + "=" * 60)
    print("Testing macOS System Audio (say command)")
    print("=" * 60)

    try:
        import subprocess

        print("\n1. Testing macOS 'say' command...")
        print("   You should hear: 'Testing system audio output'")
        print("   Speaking now...")

        result = subprocess.run(
            ["say", "Testing system audio output"], capture_output=True, timeout=5
        )

        if result.returncode == 0:
            print("   ✓ System say command executed successfully")
            print("\n   Did you hear the test message? (y/n): ", end="")
            response = input().strip().lower()
            if response == "y":
                print("   ✓ System audio is working!")
                return True
            else:
                print("   ✗ System audio not working")
                return False
        else:
            print(f"   ✗ say command failed: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"   ✗ Error testing system audio: {e}")
        return False


def test_pyttsx3():
    """Test pyttsx3 TTS engine."""
    print("=" * 60)
    print("Testing pyttsx3 TTS Engine")
    print("=" * 60)

    try:
        import pyttsx3

        print("✓ pyttsx3 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pyttsx3: {e}")
        print("\n   Please install: pip install pyttsx3")
        return False

    try:
        print("\n1. Initializing TTS engine...")
        engine = pyttsx3.init()
        print("   ✓ TTS engine initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize TTS engine: {e}")
        return False

    try:
        print("\n2. Checking available voices...")
        voices = engine.getProperty("voices")
        print(f"   ✓ Found {len(voices)} voice(s)")

        if len(voices) > 0:
            current_voice = engine.getProperty("voice")
            print(f"   Current voice: {current_voice}")

            # Try to find a better voice (enhanced or female)
            enhanced_voices = [
                v
                for v in voices
                if "enhanced" in v.id.lower() or "premium" in v.id.lower()
            ]
            female_voices = [
                v
                for v in voices
                if any(
                    name in v.name.lower()
                    for name in ["samantha", "karen", "victoria", "zira"]
                )
            ]

            if enhanced_voices:
                print(f"   Found {len(enhanced_voices)} enhanced voice(s)")
            if female_voices:
                print(f"   Found {len(female_voices)} female voice(s)")

            print("\n   First 5 voices:")
            for i, voice in enumerate(voices[:5]):
                marker = " (current)" if voice.id == current_voice else ""
                print(f"   - {voice.name}{marker}")
                if i < len(voices) - 1 and i < 4:
                    print(f"     ID: {voice.id}")
        else:
            print("   ⚠ No voices found - TTS may not work properly")
    except Exception as e:
        print(f"   ✗ Error checking voices: {e}")

    try:
        print("\n3. Testing speech output with current voice...")
        print(
            "   You should hear: 'Hello, this is a test of the text to speech system.'"
        )
        print("   Speaking now...")

        engine.setProperty("rate", 180)  # Words per minute
        engine.setProperty("volume", 1.0)  # Max volume

        test_text = "Hello, this is a test of the text to speech system."
        engine.say(test_text)

        start_time = time.time()
        engine.runAndWait()
        elapsed = time.time() - start_time

        print(f"   ✓ TTS completed in {elapsed:.2f} seconds")
        print("\n   Did you hear the test message? (y/n): ", end="")

        response = input().strip().lower()
        if response == "y":
            print("   ✓ TTS is working correctly!")
            return True
        else:
            print("   ✗ TTS completed but no audio was heard")

            # Try alternative: macOS say command
            print("\n   Trying macOS system 'say' command as fallback...")
            if test_system_audio_output():
                print("\n   ⚠ pyttsx3 is not outputting audio, but system audio works.")
                print(
                    "   Consider using macOS 'say' command as fallback in the main app."
                )
                return False
            else:
                print("\n   Troubleshooting:")
                print("   - Check system volume (try increasing it)")
                print("   - Check macOS System Settings > Sound > Output")
                print("   - Verify audio output device is correct")
                print("   - Try: System Settings > Privacy & Security > Accessibility")
                print("   - Grant Terminal/Python permission to control computer")
                return False

    except Exception as e:
        print(f"   ✗ Error during speech test: {e}")
        import traceback

        print("\n   Full error:")
        traceback.print_exc()
        return False


def test_voice_selection():
    """Test different voice options."""
    print("\n" + "=" * 60)
    print("Voice Selection Test")
    print("=" * 60)

    try:
        import pyttsx3

        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        if len(voices) == 0:
            print("No voices available to test")
            return

        print("\nTesting different voices...")
        print("You can try different voices by modifying src/hardware/audio.py")
        print("\nAvailable voices:")

        for i, voice in enumerate(voices):
            print(f"\n{i+1}. {voice.name}")
            print(f"   ID: {voice.id}")
            print(f"   Languages: {getattr(voice, 'languages', 'N/A')}")

            if i < 3:  # Test first 3 voices
                print(f"   Testing voice {i+1}...")
                engine.setProperty("voice", voice.id)
                engine.say(f"This is voice {i+1}, {voice.name}")
                engine.runAndWait()
                time.sleep(0.5)

    except Exception as e:
        print(f"Error testing voices: {e}")


def test_sounddevice():
    """Test sounddevice for beep functionality."""
    print("\n" + "=" * 60)
    print("Testing sounddevice (for beeps)")
    print("=" * 60)

    try:
        import sounddevice as sd
        import numpy as np

        print("✓ sounddevice imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sounddevice: {e}")
        print("\n   Please install: pip install sounddevice")
        return False

    try:
        print("\n1. Testing audio device...")
        devices = sd.query_devices()
        default_device = sd.default.device
        print(f"   ✓ Found {len(devices)} audio device(s)")
        print(f"   Default device: {default_device}")
    except Exception as e:
        print(f"   ✗ Error querying devices: {e}")
        return False

    try:
        print("\n2. Testing beep generation...")
        print("   You should hear a beep sound...")

        frequency = 800
        duration = 0.2
        sample_rate = 44100

        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t)

        sd.play(wave, samplerate=sample_rate)
        sd.wait()

        print("   ✓ Beep played")
        print("\n   Did you hear the beep? (y/n): ", end="")

        response = input().strip().lower()
        if response == "y":
            print("   ✓ sounddevice is working correctly!")
            return True
        else:
            print("   ✗ Beep played but no sound was heard")
            print("\n   Troubleshooting:")
            print("   - Check system volume")
            print("   - Check macOS audio permissions")
            return False

    except Exception as e:
        print(f"   ✗ Error during beep test: {e}")
        import traceback

        print("\n   Full error:")
        traceback.print_exc()
        return False


def main():
    """Run all TTS verification tests."""
    print("\n" + "=" * 60)
    print("TTS Setup Verification")
    print("=" * 60)
    print()

    # Test pyttsx3
    tts_working = test_pyttsx3()

    # Test sounddevice
    beep_working = test_sounddevice()

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"TTS (pyttsx3): {'✓ Working' if tts_working else '✗ Not working'}")
    print(f"Beeps (sounddevice): {'✓ Working' if beep_working else '✗ Not working'}")

    if not tts_working:
        print("\n⚠ TTS is not working. Possible solutions:")
        print("\n   1. Check audio output device:")
        print("      - System Settings > Sound > Output")
        print("      - Make sure correct speakers/headphones are selected")
        print("      - Try increasing system volume")
        print("\n   2. Check macOS permissions:")
        print("      - System Settings > Privacy & Security > Accessibility")
        print("      - Grant Terminal/Python permission to control computer")
        print("      - Restart Terminal after granting permissions")
        print("\n   3. Try alternative TTS method:")
        print("      - The app can use macOS 'say' command as fallback")
        print("      - This will be implemented if pyttsx3 fails")

    if not beep_working:
        print("\n⚠ Beep functionality is not working.")
        print("   The system will fall back to system beep if sounddevice fails.")
        print("   Check audio output device in System Settings > Sound")

    if tts_working and beep_working:
        print("\n✓ All audio systems are working correctly!")

    print()


if __name__ == "__main__":
    main()
