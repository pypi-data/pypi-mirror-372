# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloSTT",
    version="0.1.9",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SpeechRecognition',
        'requests',
        "faster-whisper",
        "torch",
        "pyaudio",
        "numpy",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modern Speech Recognition with both active and ambient listening and keyboard input capabilities for modern AI-driven applications.",
)
