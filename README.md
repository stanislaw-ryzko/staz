This repository contains a small script (`pCI50_HeLa.py`) for predicting activity against the HeLa cell line from molecular descriptors. The PMML model and example molecule file are stored in the `examples` directory.

The applicability domain of the model covers **xanthene derivatives**.
## Requirements
The script depends on the following Python packages and external tools:
- `padelpy`
- `pandas`
- `pypmml`
- `Open Babel` (provides the `obabel` command used for MOL2 to SDF conversion)

Install the Python packages via `pip`:

```bash
pip install padelpy pandas pypmml
```
Install Open Babel according to your platform (e.g. `apt-get install openbabel`).

## Paths configuration

At the top of `pCI50_HeLa.py` there are three variables that must be set before running the script:

```python
mol2_path = 'path_to_mol2_molecule'   # path to your input MOL2 file
sdf_path = 'path_to_temp_sdf'         # path where a temporary SDF file will be written
pmml_path = 'path_to_model'           # path to the PMML model file
```

Edit these values to point to your molecule file, a location for the intermediate SDF, and the PMML model.

## Example usage

After configuring the paths, run the script with Python:

```bash
python pCI50_HeLa.py
```
The script will convert the molecule file, generate descriptors and output the predicted activity.
