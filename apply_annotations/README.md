# Apply annotations

This is to assist in applying annotations given a csv

## Prereq

Use service catalog to spin up a notebook so you can work in that environment.
The notebook should have synapser already installed.


### How to use this

Load the `apply_annotations` function, define the annotation keys and columns you
want to use from your csv file.

```
# Define column mappings
# exampleAnnotation is what will be on Synapse and
# example_annotation is what the column name in your csv
column_mappings <- list(
  exampleAnnotation = "example_annotation",
  example2Annotation = "example_2_annotation"
)

my_manifest_df = read.csv("my_example_manifest.csv")

# Apply annotations function to each row
apply(my_manifest_df, 1, function(row) apply_annotations(row, column_mappings))
```