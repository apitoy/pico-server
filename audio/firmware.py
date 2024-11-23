import os
import sys
import time
import shutil
import requests
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import json

SRC='src2'

class PicoDeployer:
    def __init__(self):
        self.system_type = None
        self.firmware_urls = {
            'micropython': 'https://micropython.org/resources/firmware/RPI_PICO_W-20241025-v1.24.0.uf2',
            'circuitpython': 'https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-8.2.0.uf2',
            'arduino': 'https://github.com/earlephilhower/arduino-pico/releases/download/global/index.json'
        }
        self.sdk_path = Path('pico-sdk')
        self.mount_point = None
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

    def setup_micropython(self):
        """Konfiguracja MicroPython"""
        print("📦 Konfiguracja MicroPython...")

        # Pobierz firmware
        firmware_path = self.download_firmware('micropython')
        if not firmware_path:
            return False

        # Skopiuj firmware
        if not self.flash_firmware(firmware_path):
            return False

        # Przygotuj podstawowe pliki

        try:
            if self.mount_point:
                self.copy_file(os.path.join(SRC, 'boot.py'))
                self.copy_file(os.path.join(SRC, 'main.py'))
                self.copy_file(os.path.join(SRC, 'requirements.txt'))
            return True
        except Exception as e:
            print(f"❌ Błąd podczas kopiowania plików: {e}")
            return False

    def setup_arduino(self):
        """Konfiguracja Arduino"""
        print("🔧 Konfiguracja Arduino...")

        # Arduino wymaga instalacji Arduino IDE i board manager
        arduino_code = """
// Arduino code for Pico
const int LED_PIN = 25;

void setup() {
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
}
"""

        try:
            # Utwórz katalog projektu
            project_dir = Path('pico_arduino')
            project_dir.mkdir(exist_ok=True)

            # Utwórz plik .ino
            with open(project_dir / 'pico_arduino.ino', 'w') as f:
                f.write(arduino_code)

            print("""
🔔 Aby skompilować i wgrać kod Arduino:
1. Otwórz Arduino IDE
2. Zainstaluj wsparcie dla Pico:
   - Otwórz Boards Manager
   - Wyszukaj "raspberry pi pico"
   - Zainstaluj "Raspberry Pi Pico/RP2040"
3. Wybierz płytkę: Tools -> Board -> Raspberry Pi Pico
4. Otwórz utworzony plik i wgraj kod
""")
            return True

        except Exception as e:
            print(f"❌ Błąd podczas konfiguracji Arduino: {e}")
            return False

    def setup_c_sdk(self):
        """Konfiguracja C/C++ SDK"""
        print("🛠️ Konfiguracja C/C++ SDK...")

        # Sklonuj SDK jeśli nie istnieje
        if not self.sdk_path.exists():
            try:
                subprocess.run([
                    'git', 'clone',
                    'https://github.com/raspberrypi/pico-sdk.git',
                    str(self.sdk_path)
                ], check=True)

                # Inicjalizacja submodułów
                subprocess.run([
                    'git', 'submodule', 'update', '--init'
                ], cwd=str(self.sdk_path), check=True)
            except Exception as e:
                print(f"❌ Błąd podczas pobierania SDK: {e}")
                return False

        # Przygotuj przykładowy projekt
        project_dir = Path('pico_c_project')
        project_dir.mkdir(exist_ok=True)

        # CMakeLists.txt
        cmake_content = """
cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(pico_project)

pico_sdk_init()

add_executable(main
    main.c
)

target_link_libraries(main pico_stdlib)
pico_add_extra_outputs(main)
"""

        # main.c
        c_code = """
#include "pico/stdlib.h"

int main() {
    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    while (true) {
        gpio_put(LED_PIN, 1);
        sleep_ms(500);
        gpio_put(LED_PIN, 0);
        sleep_ms(500);
    }
}
"""

        try:
            # Zapisz pliki projektu
            with open(project_dir / 'CMakeLists.txt', 'w') as f:
                f.write(cmake_content)
            with open(project_dir / 'main.c', 'w') as f:
                f.write(c_code)

            # Skopiuj pico_sdk_import.cmake
            shutil.copy(
                self.sdk_path / 'external' / 'pico_sdk_import.cmake',
                project_dir / 'pico_sdk_import.cmake'
            )

            print("""
🔔 Aby skompilować projekt C/C++:
1. Przejdź do katalogu projektu
2. Utwórz i przejdź do katalogu build:
   mkdir build
   cd build
3. Uruchom cmake:
   cmake ..
4. Skompiluj:
   make
5. Wgraj plik .uf2 na Pico w trybie bootloader
""")
            return True

        except Exception as e:
            print(f"❌ Błąd podczas konfiguracji C/C++ SDK: {e}")
            return False

    def download_firmware(self, firmware_type: str) -> Optional[Path]:
        """Pobierz firmware wybranego typu"""
        if firmware_type not in self.firmware_urls:
            print(f"❌ Nieznany typ firmware: {firmware_type}")
            return None

        url = self.firmware_urls[firmware_type]
        filename = f"{firmware_type}_firmware.uf2"

        try:
            print(f"📥 Pobieranie firmware {firmware_type}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return Path(filename)

        except Exception as e:
            print(f"❌ Błąd podczas pobierania firmware: {e}")
            return None

    def flash_firmware(self, firmware_path: Path) -> bool:
        """Wgraj firmware na Pico"""
        if not self.mount_point:
            print("❌ Nie znaleziono punktu montowania RPI-RP2")
            print("Podłącz Pico w trybie bootloader (trzymając BOOTSEL)")
            return False

        try:
            print(f"📤 Wgrywanie firmware...")
            shutil.copy2(firmware_path, self.mount_point)
            print("✅ Firmware wgrany pomyślnie")
            return True

        except Exception as e:
            print(f"❌ Błąd podczas wgrywania firmware: {e}")
            return False

    def copy_file(self, code_path: Path) -> bool:
        """Wgraj firmware na Pico"""
        if not self.mount_point:
            print("❌ Nie znaleziono punktu montowania RPI-RP2")
            print("Podłącz Pico w trybie bootloader (trzymając BOOTSEL)")
            return False

        try:
            print(f"📤 Wgrywanie kodu, requirements, ...")
            shutil.copy2(code_path, self.mount_point)
            print("✅ ")
            return True

        except Exception as e:
            print(f"❌ {e}")
            return False

    def deploy(self, system_type: str):
        """Główna metoda wdrażania"""
        self.system_type = system_type

        print(f"🚀 Rozpoczynam wdrażanie systemu: {system_type}")

        if system_type == "micropython":
            return self.setup_micropython()
        elif system_type == "arduino":
            return self.setup_arduino()
        elif system_type == "c_sdk":
            return self.setup_c_sdk()
        else:
            print(f"❌ Nieobsługiwany typ systemu: {system_type}")
            return False


def main():
    deployer = PicoDeployer()

    print("Wybierz system do wdrożenia:")
    print("1. MicroPython")
    print("2. Arduino")
    print("3. C/C++ SDK")

    choice = input("Wybór (1-3): ")

    if choice == "1":
        deployer.deploy("micropython")
    elif choice == "2":
        deployer.deploy("arduino")
    elif choice == "3":
        deployer.deploy("c_sdk")
    else:
        print("❌ Nieprawidłowy wybór")


if __name__ == "__main__":
    main()
