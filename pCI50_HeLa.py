import subprocess
import os
from padelpy import from_sdf  
import pandas as pd
from pypmml import Model  

# File paths
mol2_path = 'path_to_mol2_molecule' 
sdf_path = 'path_to_temp_sdf' 
pmml_path = 'path_to_model'

# 0. Conversion MOL2 → SDF
result = subprocess.run(
    ['obabel', '-imol2', mol2_path, '-osdf', '-O', sdf_path],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("Error converting mol2 file to sdf:")
    print(result.stderr)
    exit(1)

# 1. Load descriptors from SDF file
data = from_sdf(sdf_path, descriptors=True, fingerprints=False)
df = pd.DataFrame(data)

# 2. Map names to those required by the PMML model
rename_map = {
    'ndO': 'descriptors/ndO',
    'XLogP': 'descriptors/XlogP',   # as required by PMML
    'ATSC4p': 'descriptors/ATSC4p',
    'ATS8m': 'descriptors/ATS8m',
    'VE3_Dzi': 'descriptors/Ve3_Dzi'  # as required by PMML
}

# Prepare input data — set to 0.0 if descriptor is missing
input_data = {}
for short_name, pmml_name in rename_map.items():
    value = df[short_name].values[0] if short_name in df.columns else 0.0
    input_data[pmml_name] = [value]

input_df = pd.DataFrame(input_data)

# Print descriptors (without prefix)
for short_name in rename_map.keys():
    value = df[short_name].values[0] if short_name in df.columns else None
    if value is not None:
        print(f"{short_name}: {value}")
    else:
        print(f"{short_name}: value missing")

# 3. Load the PMML model
if not os.path.exists(pmml_path):
    raise FileNotFoundError(f"PMML file not found: {pmml_path}")

try:
    model = Model.load(pmml_path)
except Exception as e:
    print(f"Error loading PMML model: {e}")
    exit(1)

# 4. Prediction
predictions = model.predict(input_df)

# 5. Print prediction result (look for column starting with 'predicted_')
print()
for col in predictions.columns:
    if col.startswith('predicted_'):
        print(f"{col}: {predictions[col].values[0]}")
