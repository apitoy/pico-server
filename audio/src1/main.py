import usb_audio
import board
import array
import time
import os
from micropython import const
import storage
import audiobusio
import audiocore
import usb_hid
from audiocore import WaveFile

# Stałe USB Audio Class
AUDIO_CONTROL_INTERFACE = const(0)
AUDIO_STREAMING_INTERFACE = const(1)
AUDIO_OUT_ENDPOINT = const(0x01)

from machine import Pin, Timer

timer = Timer()
led = Pin(15, Pin.OUT)
led2 = Pin(3, Pin.OUT)
led3 = Pin(4, Pin.OUT)
led4 = Pin(5, Pin.OUT)
led.value(1)
led2.value(1)
led3.value(0)
led4.value(0)


def blink(timer):
    led.toggle()
    led2.toggle()


timer.init(freq=2, mode=Timer.PERIODIC, callback=blink)



class USBAudioDevice:
    def __init__(self):
        # Konfiguracja USB Audio
        self.usb_audio = usb_audio.AudioOut()
        self.sample_rate = 44100
        self.channels = 1
        self.bits_per_sample = 16
        self.buffer_size = 1024

        # Bufor audio
        self.audio_buffer = array.array('H', [0] * self.buffer_size)

        # Storage na pliki WAV
        self.setup_storage()

        # Status odtwarzania
        self.playing = False
        self.current_file = None

    def setup_storage(self):
        """Konfiguracja pamięci wewnętrznej"""
        try:
            os.mkdir('/audio')
        except:
            pass

    def setup_usb_descriptor(self):
        """Konfiguracja deskryptora USB Audio"""
        self.audio_descriptor = bytes([
            # Standard USB device descriptor
            0x12,  # bLength
            0x01,  # bDescriptorType (Device)
            0x00, 0x02,  # bcdUSB
            0x00,  # bDeviceClass (per interface)
            0x00,  # bDeviceSubClass
            0x00,  # bDeviceProtocol
            0x40,  # bMaxPacketSize0
            0xC0, 0x16,  # idVendor
            0xDC, 0x05,  # idProduct
            0x01, 0x00,  # bcdDevice
            0x01,  # iManufacturer
            0x02,  # iProduct
            0x00,  # iSerialNumber
            0x01,  # bNumConfigurations

            # Audio Interface Collection
            0x09,  # bLength
            0x04,  # bDescriptorType (Interface)
            0x00,  # bInterfaceNumber
            0x00,  # bAlternateSetting
            0x00,  # bNumEndpoints
            0x01,  # bInterfaceClass (Audio)
            0x01,  # bInterfaceSubClass (Control)
            0x00,  # bInterfaceProtocol
            0x00,  # iInterface

            # Audio Control Interface
            0x09,  # bLength
            0x24,  # bDescriptorType (CS_INTERFACE)
            0x01,  # bDescriptorSubtype (HEADER)
            0x00, 0x01,  # bcdADC
            0x1E, 0x00,  # wTotalLength
            0x01,  # bInCollection
            0x01,  # baInterfaceNr

            # Audio Streaming Interface
            0x09,  # bLength
            0x04,  # bDescriptorType (Interface)
            0x01,  # bInterfaceNumber
            0x00,  # bAlternateSetting
            0x01,  # bNumEndpoints
            0x01,  # bInterfaceClass (Audio)
            0x02,  # bInterfaceSubClass (Streaming)
            0x00,  # bInterfaceProtocol
            0x00,  # iInterface
        ])

    def init_audio_interface(self):
        """Inicjalizacja interfejsu audio"""
        try:
            # Konfiguracja formatu audio
            self.usb_audio.sample_rate = self.sample_rate
            self.usb_audio.channels = self.channels
            self.usb_audio.bits_per_sample = self.bits_per_sample

            # Ustaw deskryptor USB
            self.setup_usb_descriptor()

            return True
        except Exception as e:
            print("Audio interface initialization error:", e)
            return False

    def play_wav_file(self, filename):
        """Odtwarzanie pliku WAV z pamięci wewnętrznej"""
        try:
            # Otwórz plik WAV
            wav_file = open(f'/audio/{filename}', 'rb')
            wave = WaveFile(wav_file)

            # Skonfiguruj audio
            self.usb_audio.play(wave)
            self.playing = True
            self.current_file = wave

            return True
        except Exception as e:
            print("Error playing WAV file:", e)
            return False

    def stop_playback(self):
        """Zatrzymanie odtwarzania"""
        if self.playing:
            self.usb_audio.stop()
            if self.current_file:
                self.current_file.close()
            self.playing = False
            self.current_file = None

    def copy_to_storage(self, filename, data):
        """Kopiowanie pliku WAV do pamięci wewnętrznej"""
        try:
            with open(f'/audio/{filename}', 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print("Error copying file:", e)
            return False


class AudioManager:
    def __init__(self):
        self.audio_device = USBAudioDevice()
        self.playlists = {}
        self.current_playlist = None

    def create_playlist(self, name):
        """Tworzenie nowej playlisty"""
        self.playlists[name] = []

    def add_to_playlist(self, playlist_name, filename):
        """Dodawanie pliku do playlisty"""
        if playlist_name in self.playlists:
            self.playlists[playlist_name].append(filename)

    def play_playlist(self, name):
        """Odtwarzanie playlisty"""
        if name in self.playlists:
            self.current_playlist = name
            self._play_next()

    def _play_next(self):
        """Odtwarzanie następnego utworu z playlisty"""
        if self.current_playlist and self.playlists[self.current_playlist]:
            next_file = self.playlists[self.current_playlist].pop(0)
            self.audio_device.play_wav_file(next_file)
            # Dodaj z powrotem na koniec listy
            self.playlists[self.current_playlist].append(next_file)

    def handle_usb_events(self):
        """Obsługa zdarzeń USB"""
        # Tu można dodać obsługę komend z hosta
        pass


# Przykład użycia
def main():
    # Inicjalizacja
    audio_manager = AudioManager()

    # Utworzenie playlisty
    audio_manager.create_playlist("main")

    # Dodanie przykładowego pliku WAV
    #example_wav = b'RIFF.....'  # Tu powinny być prawdziwe dane WAV
    #audio_manager.audio_device.copy_to_storage("test.wav", example_wav)
    audio_manager.add_to_playlist("main", "test.wav")

    # Główna pętla
    while True:
        try:
            # Obsługa zdarzeń USB
            audio_manager.handle_usb_events()

            # Można tu dodać więcej logiki
            time.sleep(0.001)

        except Exception as e:
            print("Main loop error:", e)
            time.sleep(1)


# Uruchomienie
if __name__ == "__main__":
    main()

