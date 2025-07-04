import subprocess
import os
import tempfile
from padelpy import from_sdf  # type: ignore
import pandas as pd
from pypmml import Model  # type: ignore

# === SETTINGS ===
mol2_dir = 'path_to_molecules'  # folder z wieloma .mol2
pmml_path = 'path_to_model'
output_csv = 'path_to_output'

# === LOAD PMML MODEL ONCE ===
if not os.path.exists(pmml_path):
    raise FileNotFoundError(f"PMML file not found: {pmml_path}")

try:
    model = Model.load(pmml_path)
except Exception as e:
    print(f"Error loading PMML model: {e}")
    exit(1)

# === DESCRIPTOR MAP ===
rename_map = {
    'ndO': 'descriptors/ndO',
    'XLogP': 'descriptors/XlogP',
    'ATSC4p': 'descriptors/ATSC4p',
    'ATS8m': 'descriptors/ATS8m',
    'VE3_Dzi': 'descriptors/Ve3_Dzi'
}

# === STORAGE FOR RESULTS ===
results = []

# === LOOP OVER MOL2 FILES ===
for filename in sorted(os.listdir(mol2_dir)):
    if not filename.lower().endswith('.mol2'):
        continue

    mol2_path = os.path.join(mol2_dir, filename)
    print(f"\nProcessing: {mol2_path}")

    # --- 0. Convert MOL2 → SDF in temp file ---
    with tempfile.NamedTemporaryFile(suffix=".sdf", delete=False) as tmp_sdf:
        sdf_path = tmp_sdf.name

    result = subprocess.run(
        ['obabel', '-imol2', mol2_path, '-osdf', '-O', sdf_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error converting {filename}:")
        print(result.stderr)
        continue

    # --- 1. Extract descriptors from SDF ---
    try:
        data = from_sdf(sdf_path, descriptors=True, fingerprints=False)
        df = pd.DataFrame(data)
    except Exception as e:
        print(f"Error extracting descriptors from {filename}: {e}")
        continue

    # --- 2. Prepare input for PMML model ---
    input_data = {}
    for short_name, pmml_name in rename_map.items():
        value = df[short_name].values[0] if short_name in df.columns else 0.0
        input_data[pmml_name] = [value]

    input_df = pd.DataFrame(input_data)

    # --- 3. Predict ---
    try:
        prediction = model.predict(input_df)
    except Exception as e:
        print(f"Prediction error for {filename}: {e}")
        continue

    # --- 4. Store result ---
    result_row = {
        "molecule": filename
    }

    # Store descriptors
    for short_name in rename_map.keys():
        result_row[short_name] = df[short_name].values[0] if short_name in df.columns else None

    # Store prediction columns
    for col in prediction.columns:
        result_row[col] = prediction[col].values[0]

    results.append(result_row)

    # --- Cleanup temp file ---
    os.remove(sdf_path)

# === SAVE ALL RESULTS TO CSV ===
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False)
    print(f"\n Saved all predictions to: {output_csv}")
else:
    print("\n No predictions were generated.")
