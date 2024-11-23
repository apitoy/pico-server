Funkcja wykrywania dysku RPI-RP2 (tryb bootloader Pico) do skryptu


Skrypt zapewnia:

1. Wykrywanie dysku RPI-RP2:
- Windows (WMI, wmic, vol)
- Linux (/proc/mounts, lsblk, /media)
- macOS (/Volumes, diskutil)

2. Funkcje pomocnicze:
- Weryfikacja dysku
- Oczekiwanie na podłączenie
- Informacje o dysku

3. Obsługa błędów:
- Timeout przy oczekiwaniu
- Weryfikacja dostępu
- Sprawdzanie rozmiaru

Użycie:

```python
finder = PicoDiskFinder()

# Proste wyszukiwanie
path = finder.find_rp2_disk()

# Oczekiwanie na dysk
path = finder.wait_for_rp2(timeout=30)

# Weryfikacja
if finder.verify_rp2_disk(path):
    # Pobierz informacje
    info = finder.get_disk_info(path)
```

Możliwe rozszerzenia:
1. Automatyczne formatowanie
2. Monitor zmian na dysku
3. Wsparcie dla innych typów Pico
4. GUI do zarządzania

