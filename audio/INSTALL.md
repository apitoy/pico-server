Skrypt instalacyjny o więcej dystrybucji Linux i szczegółowe instrukcje dla Windows:


Ten rozszerzony skrypt:

1. Obsługuje więcej dystrybucji Linux:
- Debian/Ubuntu
- Fedora
- openSUSE
- Arch Linux
- Manjaro

2. Dodaje szczegółową obsługę Windows:
- Instalacja przez Chocolatey
- Automatyczna instalacja Visual Studio Build Tools
- Konfiguracja środowiska

3. Ulepszona obsługa macOS:
- Wsparcie dla M1/M2 (ARM)
- Automatyczna instalacja Homebrew
- Instalacja Rosetta 2 jeśli potrzebna

4. Dodatkowe funkcje:
- Automatyczna konfiguracja udev rules
- Wykrywanie dystrybucji Linux
- Tworzenie struktury katalogów
- Pobieranie CircuitPython

5. Wymagania systemowe:
```bash
# Debian/Ubuntu
build-essential
libusb-1.0-0-dev
libudev-dev

# Fedora
gcc-c++
libusb-devel
systemd-devel

# openSUSE
gcc-c++
libusb-1_0-devel
systemd-devel

# Arch
base-devel
libusb

# macOS
libusb
cmake
ninja

# Windows
Visual Studio Build Tools
cmake
ninja
```
