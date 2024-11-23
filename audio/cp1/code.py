# code.py
import time
import board
import digitalio
import usb_hid


# Klasy do emulacji klawiatury
class Keycode:
    """Kody klawiszy USB HID"""
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D
    ONE = 0x1E
    TWO = 0x1F
    THREE = 0x20
    FOUR = 0x21
    FIVE = 0x22
    SIX = 0x23
    SEVEN = 0x24
    EIGHT = 0x25
    NINE = 0x26
    ZERO = 0x27
    ENTER = 0x28
    ESCAPE = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACEBAR = 0x2C
    PERIOD = 0x37
    COMMA = 0x36


class Keyboard:
    """Prosta implementacja klawiatury USB HID"""

    def __init__(self):
        self.keyboard_device = usb_hid.devices[0]
        self._report = bytearray(8)

    def _send(self):
        """Wyślij raport HID"""
        self.keyboard_device.send_report(self._report)

    def press(self, keycode):
        """Wciśnij klawisz"""
        self._report[2] = keycode
        self._send()

    def release(self, keycode):
        """Zwolnij klawisz"""
        self._report[2] = 0
        self._send()

    def release_all(self):
        """Zwolnij wszystkie klawisze"""
        for i in range(8):
            self._report[i] = 0
        self._send()


class KeyboardEmulator:
    def __init__(self):
        # LED do sygnalizacji
        self.led = digitalio.DigitalInOut(board.LED)
        self.led.direction = digitalio.Direction.OUTPUT

        # Inicjalizacja klawiatury
        self.keyboard = Keyboard()

        # Domyślne opóźnienie między klawiszami (w sekundach)
        self.delay = 1.0

        # Status działania
        self.running = False

        print("Emulator klawiatury zainicjalizowany")

    def press_key(self, keycode, duration=0.1):
        """Wciśnij i zwolnij klawisz"""
        try:
            # Włącz LED
            self.led.value = True

            # Wciśnij klawisz
            self.keyboard.press(keycode)
            time.sleep(duration)

            # Zwolnij klawisz
            self.keyboard.release(keycode)

            # Wyłącz LED
            self.led.value = False

            # Pokaż informację
            print(f"Wciśnięto klawisz: {hex(keycode)}")

        except Exception as e:
            print(f"Błąd wysyłania klawisza: {e}")
            self.led.value = False

    def type_sequence(self, sequence=None):
        """Wpisz sekwencję klawiszy"""
        if sequence is None:
            # Domyślna sekwencja 1234
            sequence = [Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR]

        self.running = True
        print("Rozpoczynam wpisywanie sekwencji...")

        try:
            while self.running:
                for key in sequence:
                    if not self.running:
                        break
                    self.press_key(key)
                    time.sleep(self.delay)

        except Exception as e:
            print(f"Błąd podczas wpisywania: {e}")
        finally:
            self.keyboard.release_all()
            self.led.value = False

    def stop(self):
        """Zatrzymaj emulację"""
        self.running = False
        self.keyboard.release_all()
        self.led.value = False
        print("Zatrzymano emulację")

    def set_delay(self, delay):
        """Ustaw opóźnienie między klawiszami"""
        self.delay = max(0.1, float(delay))
        print(f"Ustawiono opóźnienie: {self.delay}s")

    def test(self):
        """Test podstawowych funkcji"""
        print("Test klawiatury - sekwencja 1234")
        # Mignij LED 3 razy
        for _ in range(3):
            self.led.value = True
            time.sleep(0.1)
            self.led.value = False
            time.sleep(0.1)

        # Wciśnij klawisze 1-4
        test_keys = [Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR]
        for key in test_keys:
            self.press_key(key)
            time.sleep(1)


# Utwórz instancję emulatora
print("Inicjalizacja emulatora klawiatury...")
emulator = KeyboardEmulator()

print("\nDostępne komendy:")
print("emulator.test() - test klawiatury")
print("emulator.type_sequence() - rozpocznij sekwencję 1234")
print("emulator.stop() - zatrzymaj sekwencję")
print("emulator.set_delay(1.0) - ustaw opóźnienie")

# Przykład użycia:
# emulator.test()
