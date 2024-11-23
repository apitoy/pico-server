import os
import shutil
from pathlib import Path
import time


class PicoFSRepair:
    def __init__(self, mount_path: str):
        self.mount_path = Path(mount_path)
        self.backup_path = Path('pico_backup')

    def backup_current_fs(self):
        """Backup aktualnego systemu plików"""
        print("📦 Tworzenie kopii zapasowej...")
        self.backup_path.mkdir(exist_ok=True)

        for item in self.mount_path.iterdir():
            try:
                if item.is_file():
                    shutil.copy2(item, self.backup_path)
                else:
                    shutil.copytree(item, self.backup_path / item.name)
            except Exception as e:
                print(f"⚠️ Błąd podczas kopiowania {item}: {e}")

    def create_basic_structure(self):
        """Tworzenie podstawowej struktury plików"""
        print("🔨 Tworzenie podstawowej struktury...")

        # Podstawowy kod
        code_content = """# CircuitPython podstawowy kod
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = not led.value
    time.sleep(1)
"""

        # Settings
        settings_content = """# CircuitPython settings
CIRCUITPY_WIFI_SSID="twoje_wifi"
CIRCUITPY_WIFI_PASSWORD="twoje_haslo"
"""

        try:
            # Tworzenie plików
            with open(self.mount_path / 'code.py', 'w') as f:
                f.write(code_content)

            with open(self.mount_path / 'settings.toml', 'w') as f:
                f.write(settings_content)

            # Tworzenie katalogów
            (self.mount_path / 'lib').mkdir(exist_ok=True)

        except Exception as e:
            print(f"⚠️ Błąd podczas tworzenia plików: {e}")

    def verify_files(self) -> bool:
        """Weryfikacja plików systemowych"""
        print("🔍 Weryfikacja plików...")

        required_files = [
            'code.py',
            'settings.toml',
            'boot_out.txt'
        ]

        required_dirs = [
            'lib'
        ]

        all_ok = True

        # Sprawdź pliki
        for file in required_files:
            path = self.mount_path / file
            if not path.exists():
                print(f"❌ Brak pliku: {file}")
                all_ok = False
            elif path.stat().st_size == 0:
                print(f"⚠️ Pusty plik: {file}")
                all_ok = False

        # Sprawdź katalogi
        for dir in required_dirs:
            path = self.mount_path / dir
            if not path.exists() or not path.is_dir():
                print(f"❌ Brak katalogu: {dir}")
                all_ok = False

        return all_ok

    def fix_permissions(self):
        """Naprawa uprawnień"""
        print("🔧 Naprawianie uprawnień...")

        try:
            for item in self.mount_path.rglob('*'):
                os.chmod(item, 0o644 if item.is_file() else 0o755)
        except Exception as e:
            print(f"⚠️ Błąd podczas naprawy uprawnień: {e}")

    def repair(self):
        """Główna procedura naprawcza"""
        print("🚀 Rozpoczynam naprawę systemu plików...")

        # 1. Backup
        self.backup_current_fs()

        # 2. Sprawdź aktualny stan
        if not self.verify_files():
            print("🔄 Tworzę nową strukturę plików...")
            self.create_basic_structure()

        # 3. Napraw uprawnienia
        self.fix_permissions()

        # 4. Końcowa weryfikacja
        if self.verify_files():
            print("✅ Naprawa zakończona sukcesem!")
        else:
            print("❌ Niektóre problemy nie zostały rozwiązane.")
            print("   Spróbuj zresetować Pico do ustawień fabrycznych.")


# Użycie
if __name__ == "__main__":
    repairer = PicoFSRepair('/run/media/tom/CIRCUITPY')
    repairer.repair()
