# code.py
import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


class KeyboardEmulator:
    def __init__(self):
        # Inicjalizacja klawiatury USB
        self.keyboard = Keyboard(usb_hid.devices)

        # LED do sygnalizacji
        self.led = digitalio.DigitalInOut(board.LED)
        self.led.direction = digitalio.Direction.OUTPUT

        # Domyślna sekwencja klawiszy
        self.sequence = [
            Keycode.ONE,
            Keycode.TWO,
            Keycode.THREE,
            Keycode.FOUR
        ]
        self.running = False
        self.delay = 1.0  # opóźnienie między klawiszami w sekundach

    def press_and_release(self, keycode):
        """Wciśnij i zwolnij klawisz"""
        try:
            self.keyboard.press(keycode)
            time.sleep(0.1)  # Krótkie opóźnienie
            self.keyboard.release(keycode)
            # Mignij LED-em
            self.led.value = True
            time.sleep(0.05)
            self.led.value = False
        except Exception as e:
            print(f"Błąd wysyłania klawisza: {e}")

    def start(self):
        """Rozpocznij emulację klawiatury"""
        print("Rozpoczynam emulację klawiatury...")
        self.running = True

        # Sygnalizacja startu
        for _ in range(3):
            self.led.value = True
            time.sleep(0.1)
            self.led.value = False
            time.sleep(0.1)

        try:
            while self.running:
                for key in self.sequence:
                    if not self.running:
                        break
                    # Wyślij klawisz
                    self.press_and_release(key)
                    # Wyświetl informację
                    key_name = str(key)
                    if hasattr(key, 'char'):
                        key_name = key.char
                    print(f"Wysłano klawisz: {key_name}")
                    # Czekaj zadany czas
                    time.sleep(self.delay)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Zatrzymaj emulację"""
        print("Zatrzymuję emulację klawiatury...")
        self.running = False
        self.keyboard.release_all()
        self.led.value = False

    def set_delay(self, delay):
        """Ustaw opóźnienie między klawiszami"""
        self.delay = max(0.1, delay)  # Minimum 0.1s
        print(f"Ustawiono opóźnienie: {self.delay}s")

    def set_sequence(self, sequence):
        """Ustaw nową sekwencję klawiszy"""
        # Mapowanie znaków na kody klawiszy
        key_mapping = {
            '1': Keycode.ONE,
            '2': Keycode.TWO,
            '3': Keycode.THREE,
            '4': Keycode.FOUR,
            '5': Keycode.FIVE,
            '6': Keycode.SIX,
            '7': Keycode.SEVEN,
            '8': Keycode.EIGHT,
            '9': Keycode.NINE,
            '0': Keycode.ZERO,
            'a': Keycode.A,
            'b': Keycode.B,
            'c': Keycode.C,
            # ... możesz dodać więcej klawiszy
        }

        new_sequence = []
        for char in sequence.lower():
            if char in key_mapping:
                new_sequence.append(key_mapping[char])

        if new_sequence:
            self.sequence = new_sequence
            print(f"Ustawiono nową sekwencję: {sequence}")
        else:
            print("Błąd: Nieprawidłowa sekwencja")

    def type_text(self, text):
        """Wpisz tekst"""
        print(f"Wpisuję tekst: {text}")
        try:
            for char in text:
                if not self.running:
                    break
                # Wyślij klawisz
                self.keyboard.write(char)
                # Mignij LED-em
                self.led.value = True
                time.sleep(0.05)
                self.led.value = False
                # Czekaj
                time.sleep(self.delay)
        except Exception as e:
            print(f"Błąd wpisywania tekstu: {e}")


# Utwórz instancję emulatora
emulator = KeyboardEmulator()

# Zdefiniuj kilka przydatnych sekwencji
SEQUENCES = {
    'numbers': '1234',
    'countdown': '54321',
    'test': 'test123',
}

print("\nEmulator klawiatury CircuitPython gotowy!")
print("\nDostępne komendy:")
print("emulator.start() - Rozpocznij emulację")
print("emulator.stop() - Zatrzymaj emulację")
print("emulator.set_delay(1.0) - Ustaw opóźnienie (w sekundach)")
print("emulator.set_sequence('1234') - Ustaw sekwencję klawiszy")
print("emulator.type_text('Hello') - Wpisz tekst")
print("\nGotowe sekwencje:")
for name, seq in SEQUENCES.items():
    print(f"emulator.set_sequence('{seq}') - {name}")

# Przykład użycia:
# emulator.start()  # Rozpocznie wysyłanie domyślnej sekwencji 1234
emulator.start()