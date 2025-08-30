import os
import tempfile
import threading
import base64
import wave
from typing import Optional, List
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from playsound import playsound

def _save_mp3(text: str, lang: str, out_path: str) -> str:
    tts = gTTS(text=text, lang=lang)
    tts.save(out_path)
    return out_path

class VoiceProcessor:
    def __init__(self, lang_code: str = "en-IN"):
        self.lang_code = lang_code
        self.r = sr.Recognizer()
        self._stream_lock = threading.Lock()
        self._stream_chunks: List[bytes] = []

    def listen_from_mic(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        with sr.Microphone() as source:
            audio = self.r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            return self.r.recognize_google(audio, language=self.lang_code)
        except Exception:
            return None

    def recognize_file(self, filepath: str) -> Optional[str]:
        with sr.AudioFile(filepath) as source:
            audio = self.r.record(source)
        try:
            return self.r.recognize_google(audio, language=self.lang_code)
        except Exception:
            return None

    def text_to_speech(self, text: str, lang: str = "en", out_filename: Optional[str] = None) -> str:
        out_path = out_filename or tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        _save_mp3(text, lang, out_path)
        return out_path

    def play_audio(self, file_path: str):
        playsound(file_path)

    def add_stream_chunk(self, chunk_bytes: bytes):
        with self._stream_lock:
            self._stream_chunks.append(chunk_bytes)

    def clear_stream(self):
        with self._stream_lock:
            self._stream_chunks = []

    def _write_stream_to_wav(self) -> str:
        with self._stream_lock:
            chunks = list(self._stream_chunks)
        if not chunks:
            raise RuntimeError("No stream chunks available")
        try:
            from io import BytesIO
            segments = [AudioSegment.from_file(BytesIO(c)) for c in chunks]
            combined = sum(segments[1:], segments[0]) if segments else AudioSegment.silent(duration=0)
            out = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            combined.export(out, format="wav")
            return out
        except Exception:
            out = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            combined_bytes = b"".join(chunks)
            with wave.open(out, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(combined_bytes)
            return out

    def finalize_stream_and_recognize(self) -> Optional[str]:
        wav_path = self._write_stream_to_wav()
        try:
            result = self.recognize_file(wav_path)
        finally:
            try:
                os.remove(wav_path)
            except Exception:
                pass
        return result

def decode_base64_to_bytes(b64_string: str) -> bytes:
    if "," in b64_string:
        _, b64_string = b64_string.split(",", 1)
    return base64.b64decode(b64_string)
