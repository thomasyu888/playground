
library(synapser)
synLogin()

# Put in a personal project id here
project_id = "syn64097735"

# build a synapse table just to get the schema constraints, you can delete this after
mock_table = synBuildTable("Test table foo", parent = project_id, values = "my_example_manifest.csv")
mock_table = synStore(mock_table)

# Create a mock entity view just to do the annotation
# Add the scope of a fileview here
scopes = c("syn64097735")
entity_view = EntityViewSchema(
  "mock project view",
  columns=mock_table$schema$properties$columnIds,
  parent=project_id,
  scopes=,
  addAnnotationColumns=FALSE,
  includeEntityTypes=c(EntityViewType$FILE)
)
entity_view_ent = synStore(entity_view)

# Get the view
# You need the fileview to do the annotation
table_view = synTableQuery(
  sprintf("select * from %s", entity_view_ent$properties$id)
)
table_view_df = as.data.frame(table_view)

# read your manifest
my_manifest_df = read.csv("my_example_manifest.csv")

# Don't include your manifest columns
table_view_filtered <- table_view_df[, !(colnames(table_view_df) %in% colnames(my_manifest_df))]

# Merge the blank values from your fileview
final_view = merge.data.frame(
  my_manifest_df,
  table_view_filtered,
  by.x="entityId",
  by.y="id",
)

# Remove name and entityId since you may not need to annotate these
my_manifest_df$name <- NULL
my_manifest_df$entityId <- NULL

# You need the first 4 columns to annotate
cols = c('ROW_ID', 'ROW_VERSION', 'ROW_ETAG', 'id', colnames(my_manifest_df))

ent_table = Table(entity_view_ent$properties$id, final_view[, cols])
synStore(ent_table)
