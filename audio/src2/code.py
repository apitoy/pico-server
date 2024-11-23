from machine import Pin, Timer

timer = Timer()
led = Pin(15, Pin.OUT)
led2 = Pin(3, Pin.OUT)
led3 = Pin(4, Pin.OUT)
led4 = Pin(5, Pin.OUT)
led.value(1)
led2.value(1)
led3.value(0)
led4.value(0)


def blink(timer):
    led.toggle()
    led2.toggle()


timer.init(freq=2, mode=Timer.PERIODIC, callback=blink)
