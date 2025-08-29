from setuptools import setup, find_packages

setup(
    name="voice-processor",
    version="0.0.2",
    author="mrfidal",
    author_email="mrfidal@proton.me",
    description="Voice recognition and text-to-speech package",
    long_description="A package for voice recognition and text-to-speech conversion",
    long_description_content_type="text/markdown",
    url="https://github.com/bytebreach/voice-processor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "PyAudio>=0.2.11",
        "pyttsx3>=2.90"
    ],
)