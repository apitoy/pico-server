# CircuitPython basic example
import board
import digitalio
import time

# LED na płytce
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Główna pętla
while True:
    led.value = True    # LED włączony
    time.sleep(0.5)     # Czekaj 0.5s
    led.value = False   # LED wyłączony
    time.sleep(0.5)     # Czekaj 0.5s