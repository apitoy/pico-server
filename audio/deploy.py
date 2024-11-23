# !/usr/bin/env python3
import os
import sys
import time
import shutil
import argparse
from pathlib import Path
from typing import Optional, List


class PicoCustomDeployer:
    def __init__(self):
        self.find_mount_point()

    def find_mount_point(self):
        """Znajdź punkt montowania RPI-RP2"""
        possible_paths = [
            '/run/media/*/RPI-RP2',  # Linux
            '/Volumes/RPI-RP2',  # macOS
            'D:/RPI-RP2',  # Windows
            'E:/RPI-RP2'
        ]

        for path in possible_paths:
            if '*' in path:
                from glob import glob
                paths = glob(path)
                if paths:
                    self.mount_point = paths[0]
                    return
            elif os.path.exists(path):
                self.mount_point = path
                return

        self.mount_point = None

    def deploy_code(self, source_path: str or Path, main_file: str = 'main.py'):
        """Wdróż kod na Pico"""
        source_path = Path(source_path)

        if not self.mount_point:
            print("❌ Nie znaleziono punktu montowania RPI-RP2")
            print("Podłącz Pico w trybie bootloader (trzymając BOOTSEL)")
            return False

        try:
            print(f"\n📂 Wdrażanie kodu z: {source_path}")

            # Jeśli source_path jest plikiem
            if source_path.is_file():
                print(f"📄 Kopiowanie pliku {source_path.name} jako {main_file}")
                shutil.copy2(source_path, os.path.join(self.mount_point, main_file))
                return True

            # Jeśli source_path jest katalogiem
            if source_path.is_dir():
                print("📁 Kopiowanie zawartości katalogu...")
                files_copied = 0

                # Lista plików do pominięcia
                ignore_patterns = ['__pycache__', '*.pyc', '.git', '.vscode']

                for item in source_path.rglob('*'):
                    # Pomiń pliki/katalogi zgodne z ignore_patterns
                    if any(pattern in str(item) for pattern in ignore_patterns):
                        continue

                    # Ścieżka względna
                    rel_path = item.relative_to(source_path)
                    target_path = Path(self.mount_point) / rel_path

                    if item.is_file():
                        # Utwórz katalogi docelowe jeśli nie istnieją
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
                        print(f"  ✓ {rel_path}")
                        files_copied += 1

                print(f"\n✅ Skopiowano {files_copied} plików")
                return True

        except Exception as e:
            print(f"❌ Błąd podczas wdrażania kodu: {e}")
            return False

    def verify_deployment(self, source_path: Path) -> bool:
        """Weryfikuj wdrożenie"""
        try:
            print("\n🔍 Weryfikacja wdrożenia...")

            if source_path.is_file():
                # Sprawdź pojedynczy plik
                target_file = Path(self.mount_point) / source_path.name
                if not target_file.exists():
                    print(f"❌ Brak pliku: {source_path.name}")
                    return False

                # Sprawdź rozmiar
                if target_file.stat().st_size != source_path.stat().st_size:
                    print(f"❌ Niezgodność rozmiaru pliku: {source_path.name}")
                    return False

            else:
                # Sprawdź wszystkie pliki
                for source_file in source_path.rglob('*'):
                    if source_file.is_file():
                        rel_path = source_file.relative_to(source_path)
                        target_file = Path(self.mount_point) / rel_path

                        if not target_file.exists():
                            print(f"❌ Brak pliku: {rel_path}")
                            return False

                        if target_file.stat().st_size != source_file.stat().st_size:
                            print(f"❌ Niezgodność rozmiaru pliku: {rel_path}")
                            return False

            print("✅ Weryfikacja zakończona pomyślnie")
            return True

        except Exception as e:
            print(f"❌ Błąd podczas weryfikacji: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Narzędzie do wdrażania kodu na Raspberry Pi Pico')
    parser.add_argument('source', help='Ścieżka do pliku lub katalogu z kodem')
    parser.add_argument('--main', default='main.py', help='Nazwa głównego pliku (domyślnie: main.py)')
    parser.add_argument('--verify', action='store_true', help='Weryfikuj wdrożenie')

    args = parser.parse_args()

    deployer = PicoCustomDeployer()
    result = deployer.deploy_code(args.source, args.main)

    if result and args.verify:
        deployer.verify_deployment(Path(args.source))


if __name__ == "__main__":
    main()
