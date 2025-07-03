import subprocess
import os
from padelpy import from_sdf  
import pandas as pd
from pypmml import Model  

# Ścieżki do plików
mol2_path = 'path_to_mol2_molecule' 
sdf_path = 'path_to_temp_sdf' 
pmml_path = 'path_to_model'

# 0. Konwersja MOL2 → SDF
result = subprocess.run(
    ['obabel', '-imol2', mol2_path, '-osdf', '-O', sdf_path],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Błąd konwersji pliku mol2 na sdf:")
    print(result.stderr)
    exit(1)

# 1. Wczytanie deskryptorów z pliku SDF
data = from_sdf(sdf_path, descriptors=True, fingerprints=False)
df = pd.DataFrame(data)

# 2. Mapowanie nazw na te, których wymaga model PMML
rename_map = {
    'ndO': 'descriptors/ndO',
    'XLogP': 'descriptors/XlogP',   # zgodnie z PMML
    'ATSC4p': 'descriptors/ATSC4p',
    'ATS8m': 'descriptors/ATS8m',
    'VE3_Dzi': 'descriptors/Ve3_Dzi'  # zgodnie z PMML
}

# Przygotuj dane wejściowe — podaj 0.0 jeśli brak deskryptora
input_data = {}
for short_name, pmml_name in rename_map.items():
    value = df[short_name].values[0] if short_name in df.columns else 0.0
    input_data[pmml_name] = [value]

input_df = pd.DataFrame(input_data)

# Wypisanie deskryptorów (bez prefixu)
for short_name in rename_map.keys():
    value = df[short_name].values[0] if short_name in df.columns else None
    if value is not None:
        print(f"{short_name}: {value}")
    else:
        print(f"{short_name}: brak wartości")

# 3. Załaduj model PMML
if not os.path.exists(pmml_path):
    raise FileNotFoundError(f"Brak pliku PMML: {pmml_path}")

try:
    model = Model.load(pmml_path)
except Exception as e:
    print(f"Błąd podczas ładowania modelu PMML: {e}")
    exit(1)

# 4. Predykcja
predictions = model.predict(input_df)

# 5. Wypisz wynik predykcji (szukamy kolumny zaczynającej się od 'predicted_')
print()
for col in predictions.columns:
    print("Wyniki predykcji:", predictions[col].values[0])
