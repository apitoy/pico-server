# Pico USB Audio Card

Emulator karty dźwiękowej USB na Raspberry Pi Pico.

## Wymagania sprzętowe:
- Raspberry Pi Pico
- Kabel USB
- (Opcjonalnie) Głośnik/słuchawki z wbudowanym wzmacniaczem

## Instalacja:

1. Przygotowanie Pico:
```bash
# Podłącz Pico z wciśniętym BOOTSEL
# Skopiuj plik .uf2 na dysk RPI-RP2
```

2. Instalacja wymagań:
```bash
./install.sh
pip install -r requirements.txt
```

3. Wgranie oprogramowania:
```bash
python -m rshell
cp main.py /pyboard/
```

## Struktura katalogów:
```
pico_audio_card/
├── src/
│   ├── main.py
│   ├── lib/
│   │   ├── audio.py
│   │   ├── storage.py
│   │   └── usb.py
│   └── config/
│       └── settings.json
├── tests/
│   ├── test_audio.py
│   └── test_usb.py
├── docs/
│   ├── API.md
│   └── HARDWARE.md
├── requirements.txt
├── setup.py
├── install.sh
└── README.md
```

## Konfiguracja:

1. Audio:
```json
{
    "sample_rate": 44100,
    "channels": 1,
    "bit_depth": 16
}
```

2. USB:
```json
{
    "vendor_id": "0x239A",
    "product_id": "0x80F0"
}
```

## Używanie:

1. Jako karta dźwiękowa:
```python
from audio_card import AudioManager
manager = AudioManager()
manager.start()
```

2. Odtwarzanie plików:
```python
manager.play_file("music.wav")
```

## Rozwiązywanie problemów:

1. Nie wykrywa urządzenia:
- Sprawdź połączenie USB
- Zresetuj Pico
- Sprawdź sterowniki

2. Problemy z dźwiękiem:
- Sprawdź format pliku (tylko WAV)
- Sprawdź parametry audio
- Zweryfikuj bufor

```bash
python disc.py
python disc_check.py /run/media/tom/RPI-RP2
python deploy.py ./src --type code
cat /run/media/tom/CIRCUITPY/boot_out.txt
pico-mount-fix.sh
pico_mount_repair.py
/run/media/tom/RPI-RP2


```