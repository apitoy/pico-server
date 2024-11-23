#!/bin/bash

# Funkcja wykrywania dystrybucji Linux
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "redhat"
    else
        echo "unknown"
    fi
}

# Funkcja instalacji dla Debian/Ubuntu
install_debian() {
    echo "Installing for Debian/Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-dev \
        git \
        build-essential \
        libusb-1.0-0-dev \
        libudev-dev \
        cmake \
        ninja-build \
        pkg-config
}

# Funkcja instalacji dla Fedora
install_fedora() {
    echo "Installing for Fedora..."
    sudo dnf update -y
    sudo dnf install -y \
        python3-pip \
        python3-devel \
        git \
        gcc \
        gcc-c++ \
        make \
        libusb-devel \
        systemd-devel \
        cmake \
        ninja-build \
        pkg-config
}

# Funkcja instalacji dla openSUSE
install_opensuse() {
    echo "Installing for openSUSE..."
    sudo zypper refresh
    sudo zypper install -y \
        python3-pip \
        python3-devel \
        git \
        gcc \
        gcc-c++ \
        make \
        libusb-1_0-devel \
        systemd-devel \
        cmake \
        ninja \
        pkg-config
}

# Funkcja instalacji dla Arch Linux
install_arch() {
    echo "Installing for Arch Linux..."
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm \
        python-pip \
        python \
        git \
        base-devel \
        libusb \
        cmake \
        ninja \
        pkg-config
}

# Funkcja instalacji dla macOS
install_macos() {
    echo "Installing for macOS..."
    # Sprawdź czy Homebrew jest zainstalowany
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    brew update
    brew install \
        python3 \
        git \
        libusb \
        cmake \
        ninja \
        pkg-config

    # Instalacja Rosetta 2 dla M1/M2 Macs
    if [[ $(uname -m) == 'arm64' ]]; then
        softwareupdate --install-rosetta --agree-to-license
    fi
}

# Funkcja instalacji dla Windows
install_windows() {
    echo "Installing for Windows..."
    echo "Please ensure you have the following installed:"
    echo "1. Python 3.x (https://www.python.org/downloads/)"
    echo "2. Git (https://git-scm.com/download/win)"
    echo "3. Visual Studio Build Tools (https://visualstudio.microsoft.com/visual-cpp-build-tools/)"

    # Sprawdź czy Chocolatey jest zainstalowany
    if ! command -v choco &> /dev/null; then
        echo "Installing Chocolatey..."
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    fi

    # Instalacja wymaganych pakietów przez Chocolatey
    choco install -y `
        python3 `
        git `
        cmake `
        ninja `
        visualstudio2019buildtools `
        visualstudio2019-workload-vctools
}

# Funkcja konfiguracji udev rules dla Linux
setup_udev_rules() {
    echo "Setting up udev rules..."
    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="000a", MODE="0666"' | sudo tee /etc/udev/rules.d/99-pico.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
}

# Główna logika instalacji
echo "Detecting operating system..."

case "$OSTYPE" in
    linux-gnu*)
        # Wykryj dystrybucję Linux
        DISTRO=$(detect_linux_distro)
        case $DISTRO in
            ubuntu|debian|raspbian)
                install_debian
                ;;
            fedora)
                install_fedora
                ;;
            opensuse*)
                install_opensuse
                ;;
            arch|manjaro)
                install_arch
                ;;
            *)
                echo "Unsupported Linux distribution: $DISTRO"
                exit 1
                ;;
        esac
        setup_udev_rules
        ;;
    darwin*)
        install_macos
        ;;
    msys*|cygwin*|mingw*)
        install_windows
        ;;
    *)
        echo "Unsupported operating system: $OSTYPE"
        exit 1
        ;;
esac

# Instalacja wymagań Pythona
echo "Installing Python requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Pobieranie CircuitPython
echo "Downloading CircuitPython..."
CIRCUIT_PYTHON_VERSION="8.2.0"
CIRCUIT_PYTHON_URL="https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-${CIRCUIT_PYTHON_VERSION}.uf2"

if command -v curl &> /dev/null; then
    curl -L -o circuit_python.uf2 "$CIRCUIT_PYTHON_URL"
elif command -v wget &> /dev/null; then
    wget -O circuit_python.uf2 "$CIRCUIT_PYTHON_URL"
else
    echo "Please install curl or wget to download CircuitPython"
    exit 1
fi

# Konfiguracja środowiska
echo "Setting up development environment..."
mkdir -p src/lib
mkdir -p tests
mkdir -p docs

# Instrukcje końcowe
echo "Installation complete!"
echo "Please follow these steps to complete setup:"
echo "1. Connect your Pico while holding the BOOTSEL button"
echo "2. Copy circuit_python.uf2 to the RPI-RP2 drive"
echo "3. Wait for the device to restart"
echo "4. Copy the contents of the src directory to the CIRCUITPY drive"
echo ""
echo "For more information, see the README.md file."