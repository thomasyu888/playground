library(synapser)
synLogin()
entity = "syn4990358"


# Function to apply annotations to an entity
apply_annotations <- function(row) {
  entity_id <- as.character(row["entityId"])
  
  if (!is.na(entity_id) && entity_id != "") {
    try({
      # Retrieve the entity
      entity <- synGet(entity_id, downloadFile=F)
      old_annots = synGetAnnotations(entity)
      # Prepare annotations
      annotations <- list(
        specimenID = row["specimenID"],
        individualID = row["individualID"],
        assay = row["measurementTechnique"],
        species = row["species"],
        consortium = row["consortium"],
        studyKey = row["studyKey"],
        project = row["project"],
        grant = row["grant"],
        analysisType = row["analysisType"],
        isModelSystem = row["isModelSystem"],
        familyStudyParticipant = row["familyStudyParticipant"]
      )
      ent$annotations <- c(old_annots, annotations)
      synStore(ent)
      # Set annotations
      #synSetAnnotations(entity, annotations)
    }, silent = TRUE)
  } else {
    message(sprintf("Invalid entityId for row with entityId: %s", entity_id))
  }
}

individual_LC_mice <- read.csv("my/file/here")

apply(individual_LC_mice, 1, apply_annotations)
