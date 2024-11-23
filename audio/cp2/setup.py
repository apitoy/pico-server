from machine import Pin
import time


class MouseSetup:
    def __init__(self):
        # LED do sygnalizacji
        self.led = Pin("LED", Pin.OUT)

    def check_requirements(self):
        """Sprawdź wymagane moduły"""
        required = {
            'machine': False,
            'time': False,
            'usb_hid': False
        }

        print("Sprawdzanie modułów:")

        # Sprawdź każdy moduł
        try:
            import machine
            required['machine'] = True
            print("✓ machine - OK")
        except ImportError:
            print("✗ machine - BRAK")

        try:
            import time
            required['time'] = True
            print("✓ time - OK")
        except ImportError:
            print("✗ time - BRAK")

        try:
            import usb_hid
            required['usb_hid'] = True
            print("✓ usb_hid - OK")
        except ImportError:
            print("✗ usb_hid - BRAK")

        return all(required.values())

    def blink(self, times=1):
        """Mignij LED"""
        for _ in range(times):
            self.led.value(1)
            time.sleep(0.1)
            self.led.value(0)
            time.sleep(0.1)

    def create_boot_py(self):
        """Stwórz plik boot.py"""
        boot_content = """
import usb_hid
import board

# Konfiguracja USB HID
usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE))
"""
        try:
            with open('boot.py', 'w') as f:
                f.write(boot_content)
            print("✓ Utworzono boot.py")
            return True
        except:
            print("✗ Błąd tworzenia boot.py")
            return False

    def create_main_py(self):
        """Stwórz plik code.py"""
        main_content = """
from machine import Pin
import time

# LED do sygnalizacji
led = Pin("LED", Pin.OUT)

# Symulowany raport myszy: [przyciski, x, y, wheel]
mouse_report = bytearray(4)

def move_mouse(x, y):
    """
        Ruch
        myszy
        """
    mouse_report[0] = 0  # Przyciski
    mouse_report[1] = x & 0xFF  # Ruch X
    mouse_report[2] = y & 0xFF  # Ruch Y
    mouse_report[3] = 0  # Scroll

    # Sygnalizacja LED
    led.value(1)
    time.sleep(0.1)
    led.value(0)

    # Wyślij raport
    try:
        usb_hid.report(mouse_report)
    except:
        pass

# Test - ruch w kwadrat
def test_mouse():
    moves = [
        (10, 0),   # Prawo
        (0, 10),   # Dół
        (-10, 0),  # Lewo
        (0, -10)   # Góra
    ]

    while True:
        for x, y in moves:
            move_mouse(x, y)
            time.sleep(0.5)

# Uruchom test
test_mouse()
"""
        try:
            with open('code.py', 'w') as f:
                f.write(main_content)
            print("✓ Utworzono code.py")
            return True
        except:
            print("✗ Błąd tworzenia code.py")
            return False

    def setup(self):
        """Przeprowadź pełną konfigurację"""
        print("\nKonfiguracja Pico Mouse Controller")
        print("=" * 35)

        # Sprawdź wymagania
        if not self.check_requirements():
            print("\n❌ Brak wymaganych modułów!")
            print("Zainstaluj najpierw MicroPython na Pico")
            return False

        # Utwórz pliki
        print("\nTworzenie plików:")
        if not self.create_boot_py() or not self.create_main_py():
            print("\n❌ Błąd tworzenia plików!")
            return False

        # Sygnalizacja sukcesu
        print("\n✅ Konfiguracja zakończona!")
        print("\nAby uruchomić:")
        print("1. Zresetuj Pico")
        print("2. Mysz powinna zacząć się poruszać w kwadrat")

        self.blink(3)
        return True


# Funkcja główna
def main():
    setup = MouseSetup()
    if setup.setup():
        print("\nMożesz teraz zresetować Pico")
    else:
        print("\nKonfiguracja nie powiodła się!")


if __name__ == "__main__":
    main()
