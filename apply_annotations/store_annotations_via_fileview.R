
library(synapser)
synLogin()

project_id = "syn64097735"
# build a synapse table just to get the columns
mock_table = synBuildTable("Test table foo", parent = project_id, values = "my_example_manifest.csv")
mock_table = synStore(mock_table)

# Create a mock entity view just to do the annotation
entity_view = EntityViewSchema(
  "mock project view",
  columns=mock_table$schema$properties$columnIds,
  parent=project_id,
  scopes=c(project_id),
  addAnnotationColumns=FALSE,
  includeEntityTypes=c(EntityViewType$FILE)
)
entity_view_ent = synStore(entity_view)

# Get the view
table_view = synTableQuery(sprintf("select * from %s", entity_view_ent$properties$id))
# You need the fileview to do the annotation
table_view_df = as.data.frame(table_view)

my_manifest_df = read.csv("my_example_manifest.csv")
table_view_filtered <- table_view_df[, !(colnames(table_view_df) %in% colnames(my_manifest_df))]


final_view = merge.data.frame(
  table_view_filtered,
  my_manifest_df,
  by.x="id",
  by.y="entityId",
)

my_manifest_df$name <- NULL
my_manifest_df$entityId <- NULL

cols = c('ROW_ID', 'ROW_VERSION', 'ROW_ETAG', 'id', colnames(my_manifest_df))

ent_table = Table(entity_view_ent$properties$id, final_view[, cols])
synStore(ent_table)
