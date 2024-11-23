import os
import shutil
from pathlib import Path


class PicoSetup:
    def __init__(self, mount_path: str = '/run/media/tom/CIRCUITPY'):
        self.mount_path = Path(mount_path)

    def setup_basic_files(self):
        """Tworzenie podstawowych plików systemowych"""

        # Podstawowy kod dla code.py
        code_content = """# CircuitPython basic example
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
"""

        # Konfiguracja w settings.toml
        settings_content = """# CircuitPython settings
CIRCUITPY_WIFI_SSID = ""
CIRCUITPY_WIFI_PASSWORD = ""
CIRCUITPY_WEB_API_PORT = 80
CIRCUITPY_WEB_API_PASSWORD = ""
"""

        try:
            # Usuń stare pliki (zachowując boot_out.txt)
            for item in self.mount_path.iterdir():
                if item.name != 'boot_out.txt':
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

            # Utwórz nową strukturę
            files_to_create = {
                'code.py': code_content,
                'settings.toml': settings_content,
                '.metadata_never_index': '',  # Pusty plik
            }

            # Utwórz katalogi
            (self.mount_path / 'lib').mkdir(exist_ok=True)

            # Utwórz pliki
            for filename, content in files_to_create.items():
                file_path = self.mount_path / filename
                with open(file_path, 'w') as f:
                    f.write(content)

            # Ustaw uprawnienia
            for item in self.mount_path.rglob('*'):
                os.chmod(item, 0o644 if item.is_file() else 0o755)

            return True

        except Exception as e:
            print(f"Błąd podczas tworzenia plików: {e}")
            return False

    def verify_setup(self) -> dict:
        """Weryfikacja struktury plików"""
        results = {
            'files_exist': True,
            'permissions_ok': True,
            'sizes_ok': True,
            'errors': []
        }

        # Wymagane pliki i ich minimalne rozmiary
        required_files = {
            'code.py': 100,  # Min 100 bajtów
            'settings.toml': 10,  # Min 10 bajtów
            'boot_out.txt': 50,  # Min 50 bajtów
            '.metadata_never_index': 0  # Może być pusty
        }

        # Sprawdź każdy plik
        for filename, min_size in required_files.items():
            file_path = self.mount_path / filename

            if not file_path.exists():
                results['files_exist'] = False
                results['errors'].append(f"Brak pliku: {filename}")
                continue

            # Sprawdź rozmiar
            if file_path.stat().st_size < min_size:
                results['sizes_ok'] = False
                results['errors'].append(
                    f"Plik {filename} jest za mały: "
                    f"{file_path.stat().st_size} < {min_size} bajtów"
                )

            # Sprawdź uprawnienia
            try:
                with open(file_path, 'r') as f:
                    f.read(1)
            except:
                results['permissions_ok'] = False
                results['errors'].append(f"Problem z uprawnieniami: {filename}")

        # Sprawdź katalog lib
        lib_path = self.mount_path / 'lib'
        if not lib_path.exists() or not lib_path.is_dir():
            results['files_exist'] = False
            results['errors'].append("Brak katalogu lib/")

        return results


def main():
    pico = PicoSetup('/run/media/tom/RPI-RP2')

    print("🔄 Tworzenie podstawowej struktury plików...")
    if pico.setup_basic_files():
        print("✅ Struktura plików utworzona")
    else:
        print("❌ Błąd podczas tworzenia struktury")
        return

    print("\n🔍 Weryfikacja struktury...")
    results = pico.verify_setup()

    if results['errors']:
        print("\n⚠️ Znalezione problemy:")
        for error in results['errors']:
            print(f"  - {error}")
    else:
        print("✅ Wszystko wygląda dobrze!")

    print("\n📝 Status:")
    print(f"  Pliki: {'✅' if results['files_exist'] else '❌'}")
    print(f"  Uprawnienia: {'✅' if results['permissions_ok'] else '❌'}")
    print(f"  Rozmiary: {'✅' if results['sizes_ok'] else '❌'}")


if __name__ == "__main__":
    main()
