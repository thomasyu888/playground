library(synapser)
synLogin()

# Function to apply annotations to an entity
apply_annotations <- function(row, columns) {
  entity_id <- as.character(row['entityId'])
  
  if (!is.na(entity_id) && entity_id != "") {
    message(sprintf("annotating %s", entity_id))
    tryCatch({
      # It's important to set downloadFile=F or you'll be downloading the file.
      entity <- synGet(entity_id, downloadFile = FALSE)
      old_annots <- synGetAnnotations(entity)
      
      # Prepare annotations dynamically based on provided columns
      annotations <- lapply(columns, function(col) row[col])
      names(annotations) <- names(columns)
      
      # Merge old and new annotations, resolve duplicates
      merged_annotations <- c(old_annots, annotations)
      entity$annotations <- merged_annotations[!duplicated(names(merged_annotations), fromLast = TRUE)]
      
      # Store updated entity
      # Set this to be to NOT increment the version
      synStore(entity, forceVersion=F)
      
    }, error = function(e) {
      # Print a useful error message
      message(sprintf(
        "Error annotating entityId '%s': %s", 
        entity_id, 
        e$message
      ))
    })
  } else {
    message(sprintf("Invalid entityId for row with entityId: %s", entity_id))
  }
}


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
