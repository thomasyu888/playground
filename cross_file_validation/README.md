# cross file validation

This is a PoC around cross file validation.  By specifying the synapse ids and the columns you want in the `validation.py` script
you can achieve cross file validation to ensure values in a column in a CSV are a subset of values in the reference file.

Termnology
* Reference file: The file that contains the values that you want to validate against.
* Reference column: The column in the reference file that contains the values that you want to validate against.
* Target file(s): The file(s) that you want to validate.
* Target column: The column in the target file that you want to validate.

> [!NOTE]
> This is a PoC, and may run into type issues. Due to the differences from pandas reading in dataframes with NA/blank values, this is most stable when comparing string columns currently.
> The script will also fail spectacularly if you specify a column that doesn't exist in any of the files or if you don't have access to the file.  The log file `validation_results.json` will be appended to so if you don't want that, you will need to delete it before running the script.

## Usage

### Using the CLI
By running this code, it will create a `validation_results.json` that will automatically log the validation results.
```
pip install synapseclient
python validation.py --target-synapse-ids syn52955031 specimenID syn58849847 specimenID --reference-synapse-id syn62661392 --reference-column individualID
```

### Using the library

This is a work in progress. If you have your own way of specifying the synapse ids and columns, you can use the library like this:

```
synapse_data = [
    ('syn52955031', 'specimenID'),
    ('syn58849847', 'specimenID'),
]
# Synapse ID of the reference file
reference_synapse_id = 'syn62661392'
reference_column = "individualID"

# Initialize SynapseValidator
validator = SynapseValidator(
    target_synapse_ids=target_synapse_ids,
    reference_synapse_id=reference_synapse_id,
    reference_column=reference_column,
    syn=syn
)

# Perform validation
results = validator.validate()
print("Validation Results:", results)
validation_results_df = parse_json_logs_to_dataframe("validation_results.json")
validation_results_df.to_csv("validation_results.csv", index=False)
```
