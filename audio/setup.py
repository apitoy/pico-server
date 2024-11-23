from setuptools import setup, find_packages

setup(
    name="pico_audio_card",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'circuitpython-stubs',
        'adafruit-circuitpython-typing'
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="USB Audio Card emulator for Raspberry Pi Pico",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pico-audio-card",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
