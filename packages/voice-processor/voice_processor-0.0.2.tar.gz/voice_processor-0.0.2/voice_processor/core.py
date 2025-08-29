import speech_recognition as sr
import pyttsx3
import threading
import time

class VoiceProcessor:
    def __init__(self, language="en-US", timeout=3, pause_threshold=1.0):
        self.language = language
        self.timeout = timeout
        self.pause_threshold = pause_threshold
        self.is_listening = False
        self.recognized_text = ""
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = pause_threshold
        self.tts_engine = pyttsx3.init()
        
    def _listen_in_background(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=5)
                
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.recognized_text = text
            except sr.UnknownValueError:
                self.recognized_text = ""
            except sr.RequestError:
                self.recognized_text = ""
                
        except sr.WaitTimeoutError:
            self.recognized_text = ""
        finally:
            self.is_listening = False
            
    def listen(self):
        if self.is_listening:
            return ""
            
        self.is_listening = True
        self.recognized_text = ""
        
        listen_thread = threading.Thread(target=self._listen_in_background)
        listen_thread.daemon = True
        listen_thread.start()
        
        try:
            while self.is_listening:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.is_listening = False
            
        return self.recognized_text
    
    def speak(self, text, rate=150, volume=0.9, voice_index=0):
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_index].id)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception:
            return False

def listen_and_convert(language="en-US", timeout=3):
    processor = VoiceProcessor(language=language, timeout=timeout)
    return processor.listen()

def text_to_speech(text, rate=150, volume=0.9, voice_index=0):
    processor = VoiceProcessor()
    return processor.speak(text, rate, volume, voice_index)