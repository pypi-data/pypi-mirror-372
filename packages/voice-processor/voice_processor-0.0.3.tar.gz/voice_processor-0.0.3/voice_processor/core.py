import speech_recognition as sr
import pyttsx3
import threading
import time
import requests
import json
import wave
import io
import os
from pygame import mixer

class VoiceProcessor:
    def __init__(self, language="en-US", timeout=5, pause_threshold=1.0):
        self.language = language
        self.timeout = timeout
        self.pause_threshold = pause_threshold
        self.is_listening = False
        self.recognized_text = ""
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = pause_threshold
        self.tts_engine = None
        mixer.init()
        
    def _listen_in_background(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=10)
                
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.recognized_text = text
            except sr.UnknownValueError:
                self.recognized_text = ""
            except sr.RequestError as e:
                print(f"API request error: {e}")
                self.recognized_text = ""
                
        except sr.WaitTimeoutError:
            self.recognized_text = ""
        except Exception as e:
            print(f"Listening error: {e}")
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
    
    def speak(self, text, language="ml"):
        try:
            if language in ["ml", "ta", "hi", "te", "kn"]:
                return self._speak_indian_language(text, language)
            else:
                return self._speak_english(text)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return False
    
    def _speak_english(self, text):
        try:
            if self.tts_engine is None:
                self.tts_engine = pyttsx3.init()
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"English TTS error: {e}")
            return False
    
    def _speak_indian_language(self, text, language):
        try:
            api_url = f"https://api.sanskritweb.net/cerevoice/{language}/synthesize"
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'text': text,
                'voice': 'default'
            }
            
            response = requests.post(api_url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                audio_content = response.content
                
                with wave.open(io.BytesIO(audio_content), 'rb') as wav_file:
                    sample_width = wav_file.getsampwidth()
                    channels = wav_file.getnchannels()
                    frame_rate = wav_file.getframerate()
                    frames = wav_file.readframes(wav_file.getnframes())
                
                temp_file = "temp_speech.wav"
                with wave.open(temp_file, 'wb') as wav_out:
                    wav_out.setnchannels(channels)
                    wav_out.setsampwidth(sample_width)
                    wav_out.setframerate(frame_rate)
                    wav_out.writeframes(frames)
                
                mixer.music.load(temp_file)
                mixer.music.play()
                
                while mixer.music.get_busy():
                    time.sleep(0.1)
                
                mixer.music.stop()
                mixer.music.unload()
                
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                return True
            else:
                print(f"TTS API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Indian language TTS error: {e}")
            return self._speak_english(text)

def listen_and_convert(language="ml-IN", timeout=5):
    processor = VoiceProcessor(language=language, timeout=timeout)
    return processor.listen()

def text_to_speech(text, language="ml"):
    processor = VoiceProcessor()
    return processor.speak(text, language)