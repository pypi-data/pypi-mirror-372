from setuptools import setup, find_packages

setup(
    name="voice-processor",
    version="0.0.3",
    author="mrfidal",
    author_email="mrfidal@proton.me",
    description="Voice recognition and text-to-speech package with Indian language support",
    long_description="A package for voice recognition and text-to-speech conversion with support for Indian languages",
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
        "pyttsx3>=2.90",
        "requests>=2.25.1",
        "pygame>=2.0.1"
    ],
)