# voice_utils.py — Open-source voice input (STT) and optional TTS
import io

# Lazy imports to avoid hard fail if deps missing
def get_speech_to_text():
    try:
        import speech_recognition as sr
        return sr
    except ImportError:
        return None


def listen_and_transcribe() -> tuple[str, str]:
    """
    Use microphone + SpeechRecognition (Google free STT). Returns (text, error_message).
    """
    sr = get_speech_to_text()
    if not sr:
        return "", "Install SpeechRecognition and PyAudio: pip install SpeechRecognition PyAudio"
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            # Record up to 10 seconds for one utterance
            audio = r.record(source, duration=10)
        except Exception as e:
            return "", f"Microphone error: {e}"
    try:
        # Google Web API (free, no key for short audio) — open-source client
        text = r.recognize_google(audio)
        return text.strip(), ""
    except sr.UnknownValueError:
        return "", "Could not understand audio."
    except sr.RequestError as e:
        return "", f"Speech service error: {e}"
    except Exception as e:
        return "", str(e)


def text_to_speech_audio(text: str) -> bytes | None:
    """Generate TTS audio (gTTS) and return WAV/MP3 bytes for playback. Open source."""
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        tts = gTTS(text=text[:500], lang="en")
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None
