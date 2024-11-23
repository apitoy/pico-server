# !/usr/bin/env python3
import os
import sys
import time
import subprocess
import platform
import logging
from pathlib import Path
from typing import Dict, Optional
import shutil
import psutil


class PicoDiskAnalyzer:
    def __init__(self, debug: bool = True):
        # Konfiguracja loggera
        self.setup_logging(debug)
        self.system = platform.system()
        self.expected_size_range = (1_800_000, 140_000_000)  # ~2MB
        self.mount_point = None

    def setup_logging(self, debug: bool):
        """Konfiguracja szczegółowego logowania"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        if debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logging.basicConfig(
            level=level,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('pico_analysis.log')
            ]
        )
        self.logger = logging.getLogger('PicoAnalyzer')

    def analyze_disk(self, path: str) -> Dict:
        """Szczegółowa analiza znalezionego dysku"""
        self.mount_point = path
        analysis = {
            'path': path,
            'exists': False,
            'is_mounted': False,
            'is_writable': False,
            'size': None,
            'free_space': None,
            'filesystem': None,
            'device': None,
            'partition_info': None,
            'mount_details': None,
            'permissions': None,
            'errors': []
        }

        try:
            # 1. Sprawdź czy ścieżka istnieje
            if not os.path.exists(path):
                self.logger.error(f"Ścieżka {path} nie istnieje")
                analysis['errors'].append("Path does not exist")
                return analysis

            analysis['exists'] = True

            # 2. Sprawdź punkt montowania
            self._analyze_mount_point(path, analysis)

            # 3. Sprawdź uprawnienia
            self._analyze_permissions(path, analysis)

            # 4. Sprawdź system plików i urządzenie
            self._analyze_filesystem(path, analysis)

            # 5. Sprawdź rozmiar i wolne miejsce
            self._analyze_size(path, analysis)

            # 6. Szczegółowa weryfikacja
            self._verify_rp2_characteristics(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Błąd podczas analizy dysku: {str(e)}", exc_info=True)
            analysis['errors'].append(f"Analysis error: {str(e)}")
            return analysis

    def _analyze_mount_point(self, path: str, analysis: Dict):
        """Analiza punktu montowania"""
        try:
            if self.system == "Linux":
                # Sprawdź /proc/mounts
                with open('/proc/mounts', 'r') as f:
                    mounts = f.read()
                    for line in mounts.splitlines():
                        if path in line:
                            device, mount_point, fs_type, options, _, _ = line.split()
                            analysis['device'] = device
                            analysis['filesystem'] = fs_type
                            analysis['mount_details'] = options
                            analysis['is_mounted'] = True
                            self.logger.debug(f"Mount details: device={device}, fs={fs_type}, options={options}")

                # Użyj findmnt dla dodatkowych informacji
                try:
                    result = subprocess.run(['findmnt', '-J', path], capture_output=True, text=True)
                    if result.returncode == 0:
                        analysis['mount_details'] = result.stdout
                        self.logger.debug(f"Findmnt output: {result.stdout}")
                except Exception as e:
                    self.logger.warning(f"Findmnt error: {e}")

            elif self.system == "Windows":
                import win32api
                try:
                    drive_type = win32api.GetDriveType(path)
                    analysis['device_type'] = drive_type
                    analysis['is_mounted'] = True
                    self.logger.debug(f"Windows drive type: {drive_type}")
                except Exception as e:
                    self.logger.warning(f"Windows API error: {e}")

            elif self.system == "Darwin":  # macOS
                result = subprocess.run(['diskutil', 'info', path], capture_output=True, text=True)
                if result.returncode == 0:
                    analysis['mount_details'] = result.stdout
                    analysis['is_mounted'] = True
                    self.logger.debug(f"Diskutil info: {result.stdout}")

        except Exception as e:
            self.logger.error(f"Mount point analysis error: {e}", exc_info=True)
            analysis['errors'].append(f"Mount analysis failed: {str(e)}")

    def _analyze_permissions(self, path: str, analysis: Dict):
        """Analiza uprawnień dostępu"""
        try:
            stat_info = os.stat(path)
            analysis['permissions'] = {
                'mode': oct(stat_info.st_mode)[-3:],
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid,
                'user': self._get_username(stat_info.st_uid),
                'group': self._get_groupname(stat_info.st_gid)
            }

            # Sprawdź możliwość zapisu
            test_file = os.path.join(path, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                analysis['is_writable'] = True
                self.logger.debug("Write test successful")
            except Exception as e:
                analysis['is_writable'] = False
                analysis['errors'].append(f"Write test failed: {str(e)}")
                self.logger.warning(f"Write test failed: {e}")

        except Exception as e:
            self.logger.error(f"Permission analysis error: {e}", exc_info=True)
            analysis['errors'].append(f"Permission analysis failed: {str(e)}")

    def _analyze_filesystem(self, path: str, analysis: Dict):
        """Analiza systemu plików"""
        try:
            if self.system == "Linux":
                # Użyj df dla informacji o systemie plików
                result = subprocess.run(['df', '-T', path], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.splitlines()
                    if len(lines) > 1:
                        _, fs_type, _, _, _, _, _ = lines[1].split()
                        analysis['filesystem'] = fs_type
                        self.logger.debug(f"Filesystem type: {fs_type}")

                # Sprawdź partycje
                result = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,FSTYPE,MOUNTPOINT,LABEL'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    analysis['partition_info'] = result.stdout
                    self.logger.debug(f"Partition info: {result.stdout}")

            elif self.system == "Windows":
                import win32api
                try:
                    vol_info = win32api.GetVolumeInformation(path)
                    analysis['filesystem'] = vol_info[4]
                    self.logger.debug(f"Volume info: {vol_info}")
                except Exception as e:
                    self.logger.warning(f"Windows filesystem info error: {e}")

        except Exception as e:
            self.logger.error(f"Filesystem analysis error: {e}", exc_info=True)
            analysis['errors'].append(f"Filesystem analysis failed: {str(e)}")

    def _analyze_size(self, path: str, analysis: Dict):
        """Analiza rozmiaru i wolnego miejsca"""
        try:
            if self.system in ["Linux", "Darwin"]:
                st = os.statvfs(path)
                total = st.f_blocks * st.f_frsize
                free = st.f_bavail * st.f_frsize

                analysis['size'] = total
                analysis['free_space'] = free

                self.logger.debug(f"Size analysis: total={total}, free={free}")

                # Sprawdź czy rozmiar mieści się w oczekiwanym zakresie
                if not (self.expected_size_range[0] <= total <= self.expected_size_range[1]):
                    analysis['errors'].append(
                        f"Unexpected size: {total} bytes (expected {self.expected_size_range[0]}-{self.expected_size_range[1]})"
                    )

            elif self.system == "Windows":
                import win32api
                sectors_per_cluster, bytes_per_sector, free_clusters, total_clusters = \
                    win32api.GetDiskFreeSpace(path)

                total = total_clusters * sectors_per_cluster * bytes_per_sector
                free = free_clusters * sectors_per_cluster * bytes_per_sector

                analysis['size'] = total
                analysis['free_space'] = free

                self.logger.debug(f"Windows size analysis: total={total}, free={free}")

        except Exception as e:
            self.logger.error(f"Size analysis error: {e}", exc_info=True)
            analysis['errors'].append(f"Size analysis failed: {str(e)}")

    def _verify_rp2_characteristics(self, analysis: Dict):
        """Weryfikacja charakterystycznych cech RPI-RP2"""
        try:
            # 1. Sprawdź etykietę
            if self.system == "Linux":
                result = subprocess.run(['lsblk', '-no', 'LABEL', analysis['device']],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    label = result.stdout.strip()
                    # if label != "RPI-RP2":
                    #     analysis['errors'].append(f"Unexpected label: {label}")
                    #     self.logger.warning(f"Unexpected disk label: {label}")

            # 2. Sprawdź charakterystyczne pliki
            expected_files = [
                'INDEX.HTM',
                'INFO_UF2.TXT'
            ]

            for file in expected_files:
                file_path = os.path.join(analysis['path'], file)
                if not os.path.exists(file_path):
                    analysis['errors'].append(f"Missing characteristic file: {file}")
                    self.logger.warning(f"Missing file: {file}")

            # 3. Sprawdź zawartość INFO_UF2.TXT
            info_path = os.path.join(analysis['path'], 'INFO_UF2.TXT')
            if os.path.exists(info_path):
                try:
                    with open(info_path, 'r') as f:
                        content = f.read()
                        if "Raspberry Pi" not in content:
                            analysis['errors'].append("Invalid INFO_UF2.TXT content")
                            self.logger.warning("Invalid INFO_UF2.TXT content")
                except Exception as e:
                    analysis['errors'].append(f"Cannot read INFO_UF2.TXT: {str(e)}")
                    self.logger.error(f"Error reading INFO_UF2.TXT: {e}")

        except Exception as e:
            self.logger.error(f"RP2 verification error: {e}", exc_info=True)
            analysis['errors'].append(f"RP2 verification failed: {str(e)}")

    def print_analysis(self, analysis: Dict):
        """Wyświetl wyniki analizy"""
        print("\n=== Analiza dysku RPI-RP2 ===")
        print(f"\nŚcieżka: {analysis['path']}")
        print(f"Status montowania: {'Zamontowany' if analysis['is_mounted'] else 'Nie zamontowany'}")
        print(f"Możliwość zapisu: {'Tak' if analysis['is_writable'] else 'Nie'}")

        if analysis['size'] is not None:
            print(f"\nRozmiar całkowity: {analysis['size'] / 1024:.2f} KB")
        if analysis['free_space'] is not None:
            print(f"Wolne miejsce: {analysis['free_space'] / 1024:.2f} KB")

        print(f"\nSystem plików: {analysis['filesystem']}")
        print(f"Urządzenie: {analysis['device']}")

        if analysis['permissions']:
            print("\nUprawnienia:")
            for k, v in analysis['permissions'].items():
                print(f"  {k}: {v}")

        if analysis['errors']:
            print("\n⚠️ Znalezione problemy:")
            for error in analysis['errors']:
                print(f"  - {error}")

    def _get_username(self, uid: int) -> str:
        """Pobierz nazwę użytkownika na podstawie UID"""
        try:
            import pwd
            return pwd.getpwuid(uid).pw_name
        except:
            return str(uid)

    def _get_groupname(self, gid: int) -> str:
        """Pobierz nazwę grupy na podstawie GID"""
        try:
            import grp
            return grp.getgrgid(gid).gr_name
        except:
            return str(gid)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Narzędzie do analizy dysku RPI-RP2")
    parser.add_argument("path", help="Ścieżka do analizowanego dysku")
    parser.add_argument("--debug", action="store_true", help="Włącz tryb debug")

    args = parser.parse_args()

    analyzer = PicoDiskAnalyzer(debug=args.debug)
    analysis = analyzer.analyze_disk(args.path)
    analyzer.print_analysis(analysis)

    # Zapisz szczegółową analizę do pliku JSON
    import json
    with open('disk_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    sys.exit(len(analysis['errors']))


if __name__ == "__main__":
    main()
