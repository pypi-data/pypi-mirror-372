import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
import tempfile

class VoiceProcessor:
    def __init__(self, lang_code="en-IN"):
        self.lang_code = lang_code
        self.recognizer = sr.Recognizer()

    def listen_from_mic(self, duration=None):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, phrase_time_limit=duration)
        try:
            text = self.recognizer.recognize_google(audio, language=self.lang_code)
            return text
        except:
            return None

    def text_to_speech(self, text, filename=None, lang=None):
        lang = lang or self.lang_code.split("-")[0]
        if not filename:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            filename = tmp_file.name
            tmp_file.close()
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return filename

    def play_audio(self, filepath):
        if os.path.exists(filepath):
            playsound(filepath)

    def listen_and_speak(self, duration=None, filename=None):
        text = self.listen_from_mic(duration)
        if text:
            mp3_file = self.text_to_speech(text, filename)
            self.play_audio(mp3_file)
            return text, mp3_file
        return None, None

    def listen_multiple_times(self, duration=10, count=1, filename_prefix="audio"):
        results = []
        for i in range(1, count + 1):
            text = self.listen_from_mic(duration)
            if text:
                mp3_file = self.text_to_speech(text, filename=f"{filename_prefix}_{i}.mp3")
                self.play_audio(mp3_file)
                results.append((text, mp3_file))
            else:
                results.append((None, None))
        return results
