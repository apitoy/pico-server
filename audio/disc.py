# !/usr/bin/env python3
import os
import sys
import time
import platform
import subprocess
from pathlib import Path
from typing import Optional, List


class PicoDiskFinder:
    def __init__(self):
        self.system = platform.system()

    def find_rp2_disk(self) -> Optional[str]:
        """Znajdź dysk RPI-RP2 w zależności od systemu operacyjnego"""
        if self.system == "Windows":
            return self._find_windows()
        elif self.system == "Linux":
            return self._find_linux()
        elif self.system == "Darwin":  # macOS
            return self._find_macos()
        else:
            raise NotImplementedError(f"System {self.system} nie jest wspierany")

    def _find_windows(self) -> Optional[str]:
        """Znajdź RPI-RP2 w Windows używając WMI"""
        try:
            import wmi
            c = wmi.WMI()

            for drive in c.Win32_LogicalDisk():
                if drive.VolumeName == "RPI-RP2":
                    return drive.DeviceID

            # Alternatywna metoda używając subprocess
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'caption,volumename'],
                                    capture_output=True, text=True)

            for line in result.stdout.split('\n'):
                if "RPI-RP2" in line:
                    return line.split()[0]

        except ImportError:
            # Jeśli WMI nie jest dostępne, użyj listdir
            for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:"
                try:
                    if os.path.exists(drive):
                        volume_name = subprocess.check_output(
                            ['vol', drive], stderr=subprocess.PIPE
                        ).decode()
                        if "RPI-RP2" in volume_name:
                            return drive
                except:
                    continue

        return None

    def _find_linux(self) -> Optional[str]:
        """Znajdź RPI-RP2 w Linux"""
        try:
            # Metoda 1: Sprawdź /proc/mounts
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    if "RPI-RP2" in line:
                        return line.split()[1]

            # Metoda 2: Sprawdź /media
            for user_dir in os.listdir('/media'):
                user_path = Path('/media') / user_dir
                if user_path.is_dir():
                    for mount in user_path.iterdir():
                        if mount.name == "RPI-RP2":
                            return str(mount)

            # Metoda 3: Użyj lsblk
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,LABEL,MOUNTPOINT'],
                capture_output=True, text=True
            )

            for line in result.stdout.split('\n'):
                if "RPI-RP2" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]

            # Metoda 4: Sprawdź /run/media
            run_media = Path('/run/media')
            if run_media.exists():
                for user_dir in run_media.iterdir():
                    for mount in user_dir.iterdir():
                        if mount.name == "RPI-RP2":
                            return str(mount)

        except Exception as e:
            print(f"Błąd podczas szukania w Linux: {e}")

        return None

    def _find_macos(self) -> Optional[str]:
        """Znajdź RPI-RP2 w macOS"""
        try:
            # Metoda 1: Sprawdź /Volumes
            volumes_path = Path('/Volumes')
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.name == "RPI-RP2":
                        return str(volume)

            # Metoda 2: Użyj diskutil
            result = subprocess.run(
                ['diskutil', 'list'],
                capture_output=True, text=True
            )

            for line in result.stdout.split('\n'):
                if "RPI-RP2" in line:
                    disk_id = line.split()[0]
                    info = subprocess.run(
                        ['diskutil', 'info', disk_id],
                        capture_output=True, text=True
                    )
                    for info_line in info.stdout.split('\n'):
                        if "Mount Point" in info_line:
                            return info_line.split(':')[1].strip()

        except Exception as e:
            print(f"Błąd podczas szukania w macOS: {e}")

        return None

    def wait_for_rp2(self, timeout: int = 30) -> Optional[str]:
        """Czekaj na pojawienie się dysku RPI-RP2"""
        print(f"Czekam na pojawienie się dysku RPI-RP2 (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            path = self.find_rp2_disk()
            if path:
                print(f"Znaleziono RPI-RP2 na: {path}")
                return path
            time.sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()

        print("\nNie znaleziono dysku RPI-RP2!")
        return None

    def verify_rp2_disk(self, path: str) -> bool:
        """Weryfikuj czy znaleziony dysk to na pewno RPI-RP2"""
        try:
            # if not os.path.exists(path):
            #     return False

            # Sprawdź dostęp do zapisu
            test_file = os.path.join(path, '.test_write')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except:
                return False

            # Sprawdź rozmiar dysku (Pico ma około 2MB w trybie bootloader)
            if self.system == "Windows":
                import win32api
                sectors, bytes_per_sector = win32api.GetDiskFreeSpace(path)
                total_size = sectors * bytes_per_sector
            else:
                st = os.statvfs(path)
                total_size = st.f_blocks * st.f_frsize

            # Pico powinno mieć około 2MB
            return 1_000_000 < total_size < 140_000_000

        except Exception as e:
            print(f"Błąd podczas weryfikacji dysku: {e}")
            return False

    def get_disk_info(self, path: str) -> dict:
        """Pobierz informacje o dysku"""
        info = {
            'path': path,
            'size': 0,
            'free_space': 0,
            'filesystem': None,
            'writable': False
        }

        try:
            if self.system == "Windows":
                import win32api
                sectors, bytes_per_sector = win32api.GetDiskFreeSpace(path)
                info['size'] = sectors * bytes_per_sector
                info['free_space'] = win32api.GetDiskFreeSpaceEx(path)[0]
            else:
                st = os.statvfs(path)
                info['size'] = st.f_blocks * st.f_frsize
                info['free_space'] = st.f_bavail * st.f_frsize

            # Sprawdź system plików
            if self.system == "Linux":
                result = subprocess.run(
                    ['df', '-T', path],
                    capture_output=True, text=True
                )
                if result.stdout:
                    info['filesystem'] = result.stdout.split('\n')[1].split()[1]

            # Sprawdź możliwość zapisu
            test_file = os.path.join(path, '.test_write')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                info['writable'] = True
            except:
                info['writable'] = False

        except Exception as e:
            print(f"Błąd podczas pobierania informacji o dysku: {e}")

        return info


def main():
    finder = PicoDiskFinder()

    print("Szukam dysku RPI-RP2...")
    disk_path = finder.wait_for_rp2(timeout=30)

    if disk_path:
        print(f"\nZnaleziono dysk RPI-RP2 na: {disk_path}")

        if finder.verify_rp2_disk(disk_path):
            print("Weryfikacja dysku powiodła się!")

            info = finder.get_disk_info(disk_path)
            print("\nInformacje o dysku:")
            print(f"Ścieżka: {info['path']}")
            print(f"Rozmiar całkowity: {info['size'] / 1024 / 1024:.2f} MB")
            print(f"Wolne miejsce: {info['free_space'] / 1024 / 1024:.2f} MB")
            print(f"System plików: {info['filesystem']}")
            print(f"Możliwość zapisu: {'Tak' if info['writable'] else 'Nie'}")
        else:
            print("Weryfikacja dysku nie powiodła się!")
    else:
        print("\nNie znaleziono dysku RPI-RP2!")


if __name__ == "__main__":
    main()
