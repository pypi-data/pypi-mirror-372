import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
import tempfile

class VoiceProcessor:
    def __init__(self, lang_code="en-IN"):
        self.lang_code = lang_code
        self.recognizer = sr.Recognizer()

    # Listen from microphone
    def listen_from_mic(self, duration=None):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, phrase_time_limit=duration)
            text = self.recognizer.recognize_google(audio, language=self.lang_code)
            return text
        except sr.RequestError:
            return "Error: Could not request results from Google Speech Recognition."
        except sr.UnknownValueError:
            return "Error: Could not understand audio."
        except OSError:
            return "Error: No microphone detected."
        except Exception as e:
            return f"Error: {str(e)}"

    # Convert text to speech (mp3)
    def text_to_speech(self, text, filename=None, lang=None):
        lang = lang or self.lang_code.split("-")[0]
        if not filename:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            filename = tmp_file.name
            tmp_file.close()
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return filename

    # Play audio
    def play_audio(self, filepath):
        if os.path.exists(filepath):
            playsound(filepath)

    # Full flow: listen then speak
    def listen_and_speak(self, duration=None, filename=None):
        text = self.listen_from_mic(duration)
        if text and not text.startswith("Error"):
            mp3_file = self.text_to_speech(text, filename)
            self.play_audio(mp3_file)
            return text, mp3_file
        return text, None

    # Multiple recordings
    def listen_multiple_times(self, duration=10, count=1, filename_prefix="audio"):
        results = []
        for i in range(1, count + 1):
            text = self.listen_from_mic(duration)
            if text and not text.startswith("Error"):
                mp3_file = self.text_to_speech(text, filename=f"{filename_prefix}_{i}.mp3")
                self.play_audio(mp3_file)
                results.append((text, mp3_file))
            else:
                results.append((text, None))
        return results

    # NEW: Recognize text from audio file
    def recognize_audio_file(self, filepath):
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist."
        try:
            audio = sr.AudioFile(filepath)
            with audio as source:
                audio_data = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio_data, language=self.lang_code)
            return text
        except sr.RequestError:
            return "Error: Could not request results from Google Speech Recognition."
        except sr.UnknownValueError:
            return "Error: Could not understand audio."
        except Exception as e:
            return f"Error: {str(e)}"
