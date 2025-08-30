from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="voice-processor",
    version="0.0.8",
    description="A Python package for voice recognition, text-to-speech, and continuous voice listening",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="mrfidal",
    author_email="mrfidal@proton.me",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "gTTS>=2.3.0",
        "playsound>=1.3.0",
        "PyAudio>=0.2.13"
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
