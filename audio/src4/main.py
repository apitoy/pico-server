from machine import Pin, Timer
import time

# LED do sygnalizacji
led = Pin("LED", Pin.OUT)

# Kody klawiszy
KEY_1 = 0x1E
KEY_2 = 0x1F
KEY_3 = 0x20
KEY_4 = 0x21


# Raporty HID dla klawiszy
def get_key_report(key_code):
    """
    Tworzy raport HID dla klawisza
    0x00 - modyfikatory (shift, ctrl, etc.)
    0x00 - reserved
    następne bajty - kody klawiszy (max 6)
    """
    return bytes([0x00, 0x00, key_code, 0x00, 0x00, 0x00, 0x00, 0x00])


class KeyboardEmulator:
    def __init__(self):
        # Sekwencja klawiszy do wysłania
        self.keys = [KEY_1, KEY_2, KEY_3, KEY_4]
        self.current_index = 0

        # Inicjalizacja timera
        self.timer = Timer()
        self.running = False

        # Status LED
        self.led = Pin("LED", Pin.OUT)

    def send_key(self, key_code):
        """Wysyła pojedynczy klawisz"""
        try:
            # Wyślij wciśnięcie klawisza
            report = get_key_report(key_code)
            self.send_hid_report(report)
            time.sleep_ms(50)  # Krótkie opóźnienie

            # Wyślij zwolnienie klawisza (pusty raport)
            report = get_key_report(0x00)
            self.send_hid_report(report)
            time.sleep_ms(50)

            # Mignij LED-em
            self.led.toggle()

        except Exception as e:
            print("Błąd wysyłania klawisza:", e)

    def send_hid_report(self, report):
        """Wysyła raport HID przez USB"""
        # W MicroPython musimy użyć surowego dostępu do USB
        try:
            import usb_hid
            keyboard = usb_hid.Device(0, 0)  # Device ID dla klawiatury
            keyboard.send_report(report)
        except ImportError:
            # Jeśli nie ma usb_hid, symulujemy wysyłanie
            key = report[2] if len(report) > 2 else 0
            if key:
                print(f"Symulacja: Klawisz {chr(key + ord('0') - 0x1E)}")

    def timer_callback(self, timer):
        """Callback dla timera - wysyła kolejny klawisz"""
        if self.running:
            # Wyślij aktualny klawisz
            self.send_key(self.keys[self.current_index])

            # Przejdź do następnego klawisza
            self.current_index = (self.current_index + 1) % len(self.keys)

    def start(self):
        """Rozpocznij emulację klawiatury"""
        self.running = True
        # Timer na 1 sekundę
        self.timer.init(freq=1, mode=Timer.PERIODIC, callback=self.timer_callback)
        print("Rozpoczęto emulację klawiatury")

    def stop(self):
        """Zatrzymaj emulację"""
        self.running = False
        self.timer.deinit()
        self.led.value(0)
        print("Zatrzymano emulację klawiatury")

    def set_keys(self, keys):
        """Ustaw nową sekwencję klawiszy"""
        # Konwertuj znaki na kody klawiszy
        self.keys = []
        for key in keys:
            if key.isdigit():
                # Dla cyfr 0-9
                self.keys.append(0x1E + int(key) - 1)
        print(f"Ustawiono nową sekwencję: {keys}")


# Utworzenie emulatora
keyboard = KeyboardEmulator()

print("\nEmulator klawiatury gotowy!")
print("Dostępne komendy:")
print("keyboard.start() - rozpocznij wysyłanie klawiszy")
print("keyboard.stop() - zatrzymaj wysyłanie")
print("keyboard.set_keys('1234') - zmień sekwencję klawiszy")


# Alternatywna wersja bez USB HID
class KeyboardSimulator:
    def __init__(self):
        self.led = Pin("LED", Pin.OUT)
        self.timer = Timer()
        self.running = False
        self.current_key = 0

    def timer_callback(self, timer):
        """Symuluje wciśnięcie klawisza co sekundę"""
        if self.running:
            # Wciśnij kolejny klawisz (1-4)
            key = self.current_key + 1
            print(f"Symulacja: Klawisz {key}")

            # Mignij LED-em
            self.led.toggle()

            # Przejdź do następnego klawisza
            self.current_key = (self.current_key + 1) % 4

    def start(self):
        """Rozpocznij symulację"""
        self.running = True
        self.timer.init(freq=1, mode=Timer.PERIODIC, callback=self.timer_callback)
        print("Rozpoczęto symulację klawiatury")

    def stop(self):
        """Zatrzymaj symulację"""
        self.running = False
        self.timer.deinit()
        self.led.value(0)
        print("Zatrzymano symulację klawiatury")


# Użyj tej wersji jeśli nie ma dostępu do USB HID
sim = KeyboardSimulator()

print("\nSymulator klawiatury gotowy!")
print("Dostępne komendy:")
print("sim.start() - rozpocznij symulację")
print("sim.stop() - zatrzymaj symulację")

# Przykład użycia:
# sim.start()  # Rozpocznij symulację
