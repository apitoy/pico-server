skrypt do wdrażania plików na Pico po znalezieniu dysku RPI-RP2:

Ten skrypt oferuje:

1. Automatyczne wykrywanie i weryfikację dysku RPI-RP2

2. Funkcje wdrażania:
- Zwykłe pliki (kod, konfiguracja)
- Pliki UF2 (firmware)
- Selektywne wdrażanie

3. Zabezpieczenia:
- Kopie zapasowe
- Weryfikacja sum kontrolnych
- Sprawdzanie miejsca
- Logi wdrożenia

Użycie:

1. Wdrożenie kodu:
```bash
python deploy.py ./src --type code
```

2. Wdrożenie UF2: [circuit_python.uf2](circuit_python.uf2)
```bash
python deploy.py circuit_python.uf2 --type uf2
```

3. Pełne wdrożenie:
```bash
python deploy.py ./project --type all
```

4. Bez weryfikacji/backupu:
```bash
python deploy.py ./src --no-verify --no-backup
```

Funkcje:
1. Automatyczne wykrywanie Pico
2. Kopie zapasowe przed wdrożeniem
3. Weryfikacja wdrożenia
4. Logi operacji

Możliwe rozszerzenia:
1. GUI do wdrażania
2. Wsparcie dla wielu Pico
3. Zdalne wdrażanie
4. System rollback

