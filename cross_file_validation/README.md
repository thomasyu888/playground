## cross file validation

This is a PoC around cross file validation.  By replacing the synapse ids and the columns you want in the `validation.py` script
you can achieve cross file validation to ensure values in a column in a CSV are a subset of values in the reference file.

Termnology
* Reference file: The file that contains the values that you want to validate against.
* Reference column: The column in the reference file that contains the values that you want to validate against.
* Target file(s): The file(s) that you want to validate.
* Target column: The column in the target file that you want to validate.

### Usage

By running this code, it will create a `validation_results.json` that will automatically log the validation results.
```
pip install synapseclient
python validation.py
```
