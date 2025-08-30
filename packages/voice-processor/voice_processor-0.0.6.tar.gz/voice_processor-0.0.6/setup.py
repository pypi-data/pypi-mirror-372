from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="voice-processor",
    version="0.0.6",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "gTTS>=2.3.0",
        "playsound>=1.3.0",
        "pydub>=0.25.1"
    ],
    author="mrfidal",
    author_email="mrfidal@proton.me",
    description="Voice processing: STT, TTS, and audio playback",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebreach/voice-processor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech"
    ],
    python_requires=">=3.8",
)
