from machine import Pin, Timer, I2S
import time
import os


# Podstawowa konfiguracja audio dla MicroPython
class AudioController:
    def __init__(self):
        # Konfiguracja I2S dla audio
        self.audio_out = I2S(
            0,  # I2S nr
            sck=Pin(18),  # Serial Clock
            ws=Pin(19),  # Word Select
            sd=Pin(20),  # Serial Data
            mode=I2S.TX,  # Tryb transmisji
            bits=16,  # Rozdzielczość
            format=I2S.STEREO,  # Format
            rate=44100,  # Częstotliwość próbkowania
            ibuf=40000  # Rozmiar bufora
        )
        self.buffer_size = 1024
        self.led = Pin("LED", Pin.OUT)  # LED dla sygnalizacji

    def play_wav(self, filename):
        try:
            with open(filename, 'rb') as file:
                # Pomiń nagłówek WAV (44 bajty)
                file.seek(44)

                # Czytaj i odtwarzaj dane
                while True:
                    audio_data = file.read(self.buffer_size)
                    if not audio_data:
                        break
                    self.audio_out.write(audio_data)

                self.audio_out.deinit()
                return True
        except Exception as e:
            print("Błąd odtwarzania:", e)
            return False


# Instalacja zależności
def install_dependencies():
    """
    Instalacja wymaganych pakietów przez upip
    Wymaga połączenia WiFi
    """
    import network
    import upip

    def connect_wifi(ssid, password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('Łączenie z WiFi...')
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
        print('Połączono z WiFi:', wlan.ifconfig())

    # Połącz z WiFi (uzupełnij swoje dane)
    connect_wifi('YOUR_SSID', 'YOUR_PASSWORD')

    # Lista wymaganych pakietów
    required_packages = [
        'micropython-machine',
        'micropython-time',
        'micropython-os'
    ]

    # Instalacja pakietów
    for package in required_packages:
        try:
            upip.install(package)
            print(f"Zainstalowano {package}")
        except Exception as e:
            print(f"Błąd instalacji {package}: {e}")


# Przykład użycia
def main():
    audio = AudioController()

    # Test LED
    for _ in range(3):
        audio.led.on()
        time.sleep(0.1)
        audio.led.off()
        time.sleep(0.1)

    # Odtwórz plik WAV (jeśli istnieje)
    if os.path.exists('test.wav'):
        audio.play_wav('test.wav')


if __name__ == "__main__":
    # Najpierw zainstaluj zależności
    try:
        install_dependencies()
    except Exception as e:
        print("Błąd instalacji zależności:", e)

    # Uruchom główny program
    main()
