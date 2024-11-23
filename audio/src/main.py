from machine import Pin, Timer

tim = Timer()
led = Pin(15, Pin.OUT)
led.value(1)


def blink():
    led.toggle()


tim.init(freq=6, mode=Timer.PERIODIC, callback=blink)

