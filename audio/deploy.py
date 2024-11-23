# !/usr/bin/env python3
import os
import sys
import time
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import json
from disc import PicoDiskFinder

class PicoRP2Deployer:
    def __init__(self):
        self.finder = PicoDiskFinder()  # z poprzedniego kodu
        self.rp2_path = None
        self.deployment_log = []
        self.config = {
            'timeout': 30,
            'verify_checksum': True,
            'make_backup': True,
            'allowed_extensions': ['.py', '.txt', '.json', '.uf2'],
            'backup_dir': 'pico_backups',
            'ignore_patterns': ['__pycache__', '*.pyc', '.git', '.vscode'],
        }

    def prepare_deployment(self) -> bool:
        """Przygotowanie do wdrożenia"""
        print("🔍 Szukam dysku RPI-RP2...")

        try:
            self.rp2_path = self.finder.wait_for_rp2(timeout=self.config['timeout'])
            if not self.rp2_path:
                print("❌ Nie znaleziono dysku RPI-RP2!")
                return False

            print(f"✅ Znaleziono dysk RPI-RP2: {self.rp2_path}")

            if not self.finder.verify_rp2_disk(self.rp2_path):
                print("❌ Weryfikacja dysku nie powiodła się!")
                return False

            if self.config['make_backup']:
                self.create_backup()

            return True

        except Exception as e:
            print(f"❌ Błąd podczas przygotowania: {e}")
            return False

    def create_backup(self):
        """Tworzenie kopii zapasowej zawartości Pico"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(self.config['backup_dir']) / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)

            print(f"📂 Tworzenie kopii zapasowej w: {backup_dir}")

            # Kopiowanie plików
            for item in Path(self.rp2_path).iterdir():
                if item.is_file():
                    shutil.copy2(item, backup_dir)
                else:
                    shutil.copytree(item, backup_dir / item.name)

            # Zapisz metadane
            metadata = {
                'timestamp': timestamp,
                'source': str(self.rp2_path),
                'files': [str(f.relative_to(backup_dir)) for f in backup_dir.rglob('*') if f.is_file()]
            }

            with open(backup_dir / 'backup_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"✅ Kopia zapasowa utworzona: {len(metadata['files'])} plików")

        except Exception as e:
            print(f"⚠️ Błąd podczas tworzenia kopii zapasowej: {e}")

    def calculate_checksum(self, file_path: Path) -> str:
        """Obliczanie sumy kontrolnej pliku"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def verify_deployment(self, source_files: Dict[str, str], deployed_path: Path) -> bool:
        """Weryfikacja poprawności wdrożenia"""
        print("🔍 Weryfikacja wdrożenia...")
        errors = []

        for rel_path, checksum in source_files.items():
            deployed_file = deployed_path / rel_path
            if not deployed_file.exists():
                errors.append(f"Brak pliku: {rel_path}")
                continue

            deployed_checksum = self.calculate_checksum(deployed_file)
            if deployed_checksum != checksum:
                errors.append(f"Niezgodność sumy kontrolnej: {rel_path}")

        if errors:
            print("❌ Znaleziono błędy podczas weryfikacji:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("✅ Weryfikacja zakończona sukcesem")
        return True

    def deploy(self, source_path: str or Path, deploy_type: str = 'all') -> bool:
        """Wdrożenie plików na Pico"""
        source_path = Path(source_path)
        if not source_path.exists():
            print(f"❌ Ścieżka źródłowa nie istnieje: {source_path}")
            return False

        try:
            # Przygotowanie
            if not self.prepare_deployment():
                return False

            print(f"\n📤 Rozpoczynam wdrażanie z: {source_path}")
            self.deployment_log.append(f"Rozpoczęcie wdrażania: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Zbierz pliki do wdrożenia
            files_to_deploy = {}
            total_size = 0

            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # Sprawdź czy plik powinien być pominięty
                    if any(pattern in str(file_path) for pattern in self.config['ignore_patterns']):
                        continue

                    # Sprawdź rozszerzenie
                    if deploy_type != 'all' and file_path.suffix not in self.config['allowed_extensions']:
                        continue

                    rel_path = file_path.relative_to(source_path)
                    files_to_deploy[str(rel_path)] = self.calculate_checksum(file_path)
                    total_size += file_path.stat().st_size

            # Sprawdź dostępne miejsce
            disk_info = self.finder.get_disk_info(self.rp2_path)
            if total_size > disk_info['free_space']:
                print(
                    f"❌ Za mało miejsca na dysku! Potrzebne: {total_size / 1024:.1f}KB, Dostępne: {disk_info['free_space'] / 1024:.1f}KB")
                return False

            print(f"\n📦 Znaleziono {len(files_to_deploy)} plików do wdrożenia ({total_size / 1024:.1f}KB)")

            # Wdrażanie plików
            for rel_path, checksum in files_to_deploy.items():
                source_file = source_path / rel_path
                target_file = Path(self.rp2_path) / rel_path

                # Utwórz katalogi jeśli nie istnieją
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Kopiuj plik
                print(f"📄 Kopiowanie: {rel_path}")
                shutil.copy2(source_file, target_file)
                self.deployment_log.append(f"Skopiowano: {rel_path}")

            # Weryfikacja
            if self.config['verify_checksum']:
                if not self.verify_deployment(files_to_deploy, Path(self.rp2_path)):
                    return False

            print("\n✅ Wdrożenie zakończone sukcesem!")
            self.save_deployment_log()
            return True

        except Exception as e:
            print(f"❌ Błąd podczas wdrażania: {e}")
            self.deployment_log.append(f"Błąd: {str(e)}")
            self.save_deployment_log()
            return False

    def save_deployment_log(self):
        """Zapisywanie logu wdrożenia"""
        log_dir = Path('deployment_logs')
        log_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"deploy_log_{timestamp}.txt"

        with open(log_file, 'w') as f:
            for entry in self.deployment_log:
                f.write(f"{entry}\n")

    def deploy_uf2(self, uf2_path: str or Path) -> bool:
        """Wdrożenie pliku UF2"""
        uf2_path = Path(uf2_path)
        if not uf2_path.exists() or uf2_path.suffix != '.uf2':
            print("❌ Nieprawidłowy plik UF2")
            return False

        try:
            if not self.prepare_deployment():
                return False

            print(f"\n📤 Wdrażanie pliku UF2: {uf2_path.name}")

            # Kopiuj plik UF2
            target_path = Path(self.rp2_path) / uf2_path.name
            shutil.copy2(uf2_path, target_path)

            print("✅ Plik UF2 skopiowany. Pico powinno się zrestartować.")
            return True

        except Exception as e:
            print(f"❌ Błąd podczas wdrażania UF2: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Narzędzie do wdrażania na Raspberry Pi Pico (RPI-RP2)")
    parser.add_argument("source", help="Ścieżka źródłowa do wdrożenia")
    parser.add_argument("--type", choices=['all', 'code', 'uf2'], default='all',
                        help="Typ wdrożenia (domyślnie: all)")
    parser.add_argument("--no-backup", action="store_true",
                        help="Wyłącz tworzenie kopii zapasowej")
    parser.add_argument("--no-verify", action="store_true",
                        help="Wyłącz weryfikację wdrożenia")

    args = parser.parse_args()

    deployer = PicoRP2Deployer()

    # Konfiguracja na podstawie argumentów
    deployer.config['make_backup'] = not args.no_backup
    deployer.config['verify_checksum'] = not args.no_verify

    # Wdrożenie
    if args.type == 'uf2':
        success = deployer.deploy_uf2(args.source)
    else:
        success = deployer.deploy(args.source, args.type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
