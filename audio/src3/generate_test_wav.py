# main.py
from machine import Pin, PWM
import time
import struct


class WavGenerator:
    def __init__(self):
        """Inicjalizacja generatora WAV"""
        # Parametry WAV
        self.sample_rate = 44100
        self.bits_per_sample = 16
        self.channels = 1

    def create_wav_header(self, data_size):
        """Tworzenie nagłówka WAV"""
        header = bytearray()
        # RIFF chunk descriptor
        header.extend(b'RIFF')
        header.extend(struct.pack('<I', data_size + 36))  # Rozmiar całego pliku - 8
        header.extend(b'WAVE')

        # Format chunk
        header.extend(b'fmt ')
        header.extend(struct.pack('<I', 16))  # Rozmiar chunka format (16 dla PCM)
        header.extend(struct.pack('<H', 1))  # Format audio (1 dla PCM)
        header.extend(struct.pack('<H', self.channels))  # Liczba kanałów
        header.extend(struct.pack('<I', self.sample_rate))  # Częstotliwość próbkowania
        bytes_per_second = self.sample_rate * self.channels * self.bits_per_sample // 8
        header.extend(struct.pack('<I', bytes_per_second))  # Bajty na sekundę
        block_align = self.channels * self.bits_per_sample // 8
        header.extend(struct.pack('<H', block_align))  # Block align
        header.extend(struct.pack('<H', self.bits_per_sample))  # Bity na próbkę

        # Data chunk
        header.extend(b'data')
        header.extend(struct.pack('<I', data_size))  # Rozmiar danych

        return header

    def generate_test_file(self, filename="test.wav", duration=1, frequency=440):
        """Generowanie pliku testowego WAV"""
        # Oblicz parametry
        num_samples = int(self.sample_rate * duration)
        amplitude = 32767  # Maksymalna amplituda dla 16-bit

        try:
            with open(filename, 'wb') as file:
                # Zapisz tymczasowy nagłówek
                data_size = num_samples * 2  # 2 bajty na próbkę
                header = self.create_wav_header(data_size)
                file.write(header)

                # Generuj i zapisz dane
                for i in range(num_samples):
                    # Uproszczona generacja sinusoidy
                    t = i / self.sample_rate
                    value = int(amplitude * ((t * frequency) % 2 - 1))
                    file.write(struct.pack('<h', value))

            print(f"Wygenerowano plik: {filename}")
            return True

        except Exception as e:
            print(f"Błąd podczas generowania pliku: {e}")
            return False


class AudioPlayer:
    def __init__(self, PORT=1):
        # PWM dla audio
        self.audio_out = PWM(Pin(PORT))  # GP0
        self.audio_out.freq(44100)
        self.audio_out.duty_u16(0)

        # LED do sygnalizacji
        self.led = Pin("LED", Pin.OUT)
        self.show_ready()

    def show_ready(self):
        """Sygnalizacja gotowości"""
        for _ in range(3):
            self.led.toggle()
            time.sleep(0.1)
            self.led.toggle()
            time.sleep(0.1)

    def play(self, filename="test.wav"):
        """Odtwórz plik WAV"""
        try:
            with open(filename, 'rb') as f:
                # Pomiń nagłówek WAV
                f.seek(44)

                print("Rozpoczynam odtwarzanie...")
                self.led.value(1)

                while True:
                    # Czytaj próbkę 16-bit
                    sample = f.read(2)
                    if not sample or len(sample) != 2:
                        break

                    # Konwertuj na wartość 16-bit
                    value = sample[0] | (sample[1] << 8)
                    # Przeskaluj na zakres PWM
                    pwm_value = value + 32768  # Przesuń z -32768..32767 na 0..65535

                    # Wyślij na PWM
                    self.audio_out.duty_u16(pwm_value)
                    time.sleep_us(20)  # Małe opóźnienie dla stabilności

                print("Zakończono odtwarzanie")
                self.led.value(0)
                self.audio_out.duty_u16(0)

        except OSError as e:
            print(f"Nie znaleziono pliku {filename}")
            self.show_error()
        except Exception as e:
            print("Błąd:", e)
            self.show_error()

    def show_error(self):
        """Sygnalizacja błędu"""
        for _ in range(5):
            self.led.toggle()
            time.sleep(0.05)
            self.led.toggle()
            time.sleep(0.05)


# Utworzenie instancji
generator = WavGenerator()
player = AudioPlayer(1)

# Wygeneruj plik testowy
generator.generate_test_file(frequency=440)  # 440 Hz (dźwięk A4)
player.play("test.wav")

print("\nSystem gotowy!")
print("Dostępne komendy:")
print("player.play() - odtwórz dźwięk")
print("generator.generate_test_file(frequency=440) - generuj nowy plik")
