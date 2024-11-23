import time
import array
import math
import usb_hid
from machine import Pin, PWM

# Configure PWM
pwm = PWM(Pin(0))  # Use GP0 for PWM output
pwm.freq(1000)  # Set PWM frequency to 1 kHz

# Buffer for audio data
audio_buffer = array.array('h', [0] * 1024)  # 16-bit signed integers

def generate_sine_wave():
    for i in range(len(audio_buffer)):
        audio_buffer[i] = int(32767 * math.sin(2 * math.pi * 1000 * i / 16000))  # 1 kHz sine wave

while True:
    generate_sine_wave()
    usb_hid.send(audio_buffer)  # Send audio buffer over USB

