# boot.py - wykonywany przy starcie
import machine
# machine.freq()          # get the current frequency of the CPU
machine.freq(240000000) # set the CPU frequency to 240 MHz and keep

# boot.py - konfiguracja urządzenia
import storage
import usb_cdc
import usb_hid

# Wyłącz dostęp do pamięci masowej USB
storage.disable_usb_drive()
# Wyłącz konsolę szeregową
usb_cdc.disable()
# Włącz HID (mysz i klawiatura)
usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE))
