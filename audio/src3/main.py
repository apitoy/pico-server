from machine import Pin, PWM, Timer
import time


class AudioPlayer:
    def __init__(self, pin_number=0):
        """Inicjalizacja audio na wybranym pinie"""
        self.pwm = PWM(Pin(pin_number))
        self.pwm.freq(44100)  # Częstotliwość próbkowania
        self.pwm.duty_u16(0)  # Startujemy z zerem

        self.led = Pin("LED", Pin.OUT)
        self.playing = False
        self.volume = 100

    def generate_tone(self, frequency, duration=1.0):
        """Generowanie tonu o zadanej częstotliwości"""
        if frequency <= 0:  # Cisza
            self.pwm.duty_u16(0)
            time.sleep(duration)
            return

        print(f"Generuję ton {frequency}Hz przez {duration}s")

        # Parametry
        sample_rate = 44100
        samples_per_cycle = sample_rate // frequency

        # Włącz LED na czas odtwarzania
        self.led.value(1)

        try:
            # Generuj i odtwarzaj ton
            self.playing = True
            start_time = time.ticks_ms()

            while self.playing and (time.ticks_ms() - start_time) < (duration * 1000):
                for i in range(samples_per_cycle):
                    if not self.playing:
                        break

                    # Generuj wartość PWM (trójkąt)
                    if i < samples_per_cycle // 2:
                        value = i * 65535 // (samples_per_cycle // 2)
                    else:
                        value = (samples_per_cycle - i) * 65535 // (samples_per_cycle // 2)

                    # Zastosuj głośność
                    value = value * self.volume // 100

                    # Wyślij na PWM
                    self.pwm.duty_u16(value)
                    time.sleep_us(10)

        finally:
            self.pwm.duty_u16(0)
            self.led.value(0)
            self.playing = False

    def rest(self, duration):
        """Pauza w muzyce"""
        self.pwm.duty_u16(0)
        time.sleep(duration)

    def play_sequence(self, sequence):
        """Odtwórz sekwencję dźwięków"""
        print("Odtwarzam sekwencję")
        for note in sequence:
            freq, duration = note
            if freq > 0:
                self.generate_tone(freq, duration)
            else:
                self.rest(duration)
            time.sleep(0.01)  # Małe opóźnienie między nutami

    def set_volume(self, volume):
        """Ustaw głośność (0-100)"""
        self.volume = max(0, min(100, volume))
        print(f"Głośność: {self.volume}%")

    def stop(self):
        """Zatrzymaj odtwarzanie"""
        self.playing = False
        self.pwm.duty_u16(0)


# Nuty dla Super Mario Bros (częstotliwość w Hz)
NOTE_C4 = 262
NOTE_CS4 = 277
NOTE_D4 = 294
NOTE_DS4 = 311
NOTE_E4 = 330
NOTE_F4 = 349
NOTE_FS4 = 370
NOTE_G4 = 392
NOTE_GS4 = 415
NOTE_A4 = 440
NOTE_AS4 = 466
NOTE_B4 = 494
NOTE_C5 = 523
NOTE_CS5 = 554
NOTE_D5 = 587
NOTE_DS5 = 622
NOTE_E5 = 659
NOTE_F5 = 698
NOTE_FS5 = 740
NOTE_G5 = 784
NOTE_GS5 = 831
NOTE_A5 = 880
NOTE_AS5 = 932
NOTE_B5 = 988
REST = 0

# Melodia Super Mario (uproszczona)
MARIO_THEME = [
    (NOTE_E5, 0.15), (NOTE_E5, 0.15), (REST, 0.15), (NOTE_E5, 0.15),
    (REST, 0.15), (NOTE_C5, 0.15), (NOTE_E5, 0.15), (REST, 0.15),
    (NOTE_G5, 0.15), (REST, 0.3), (NOTE_G4, 0.15), (REST, 0.3)
]

# Melodia Tetris (uproszczona)
TETRIS_THEME = [
    (NOTE_E5, 0.15), (NOTE_B4, 0.075), (NOTE_C5, 0.075), (NOTE_D5, 0.15),
    (NOTE_C5, 0.075), (NOTE_B4, 0.075), (NOTE_A4, 0.15), (NOTE_A4, 0.075),
    (NOTE_C5, 0.075), (NOTE_E5, 0.15), (NOTE_D5, 0.075), (NOTE_C5, 0.075),
    (NOTE_B4, 0.15), (REST, 0.075), (NOTE_C5, 0.075), (NOTE_D5, 0.15),
    (NOTE_E5, 0.15), (NOTE_C5, 0.15), (NOTE_A4, 0.15), (NOTE_A4, 0.15),
    (REST, 0.15)
]

# Jingle Bells (uproszczona)
JINGLE_BELLS = [
    (NOTE_E5, 0.2), (NOTE_E5, 0.2), (NOTE_E5, 0.4),
    (NOTE_E5, 0.2), (NOTE_E5, 0.2), (NOTE_E5, 0.4),
    (NOTE_E5, 0.2), (NOTE_G5, 0.2), (NOTE_C5, 0.2), (NOTE_D5, 0.2),
    (NOTE_E5, 0.8),
    (REST, 0.2)
]

# Utworzenie odtwarzacza
audio = AudioPlayer(0)  # GPIO 0

print("\nOdtwarzacz melodii gotowy!")
print("Dostępne melodie:")
print("1. audio.play_sequence(MARIO_THEME)")
print("2. audio.play_sequence(TETRIS_THEME)")
print("3. audio.play_sequence(JINGLE_BELLS)")
print("\nKontrola:")
print("- audio.set_volume(0-100) - głośność")
print("- audio.stop() - zatrzymaj")

# Przykład użycia:
# audio.play_sequence(MARIO_THEME)
