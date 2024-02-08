import os

from dotenv import dotenv_values
import snowflake.connector
from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer

# 1. log into snowflake
config = dotenv_values(os.path.expanduser("~/.snowsql/.env"))

ctx = snowflake.connector.connect(
    user=config['user'],
    password=config['password'],
    account=config['snowflake_account'],
    database="synapse_data_warehouse",
    schema="synapse",
    role="SYSADMIN",
    warehouse="compute_xsmall"
)

cur = ctx.cursor()

# 1. Extract public data from snowflake
cur.execute(
    """
    SELECT
        node_latest.NAME,
        node_latest.CREATED_ON,
        node_latest.ID,
        userprofile_latest.USER_NAME
    FROM
        synapse_data_warehouse.synapse.node_latest
    join
        synapse_data_warehouse.synapse.userprofile_latest
    on
        node_latest.created_by = userprofile_latest.id
    where
        is_public and NODE_TYPE = 'project'
    """
)

df = cur.fetch_pandas_all()

documents = [
    {
        "name": row['NAME'],
        "id": row['ID'],
        'author': row['USER_NAME'],
        'year': str(row['CREATED_ON'])
    }
    for _, row in df.iterrows()
]

# 2. Create Qdrant vector database in memory
qdrant = QdrantClient(":memory:")
# qdrant_client = QdrantClient("http://localhost:6333")

# 3. Leverage model to create embeddings
encoder = SentenceTransformer("all-MiniLM-L6-v2")

qdrant.recreate_collection(
    collection_name="synapse_public_entities",
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
        distance=models.Distance.COSINE,
    ),
)
# 4. upload embeddings into vector database along with metadata
qdrant.upload_points(
    collection_name="synapse_public_entities",
    points=[
        models.Record(
            id=idx, vector=encoder.encode(doc["name"]).tolist(), payload=doc
        )
        for idx, doc in enumerate(documents)
    ],
)
# embeddings = encoder.encode(df['NAME'], batch_size=128, show_progress_bar=True)

# 5. perform a search
hits = qdrant.search(
    collection_name="synapse_public_entities",
    query_vector=encoder.encode("AACR GENIE").tolist(),
    limit=50,
)
for hit in hits:
    print(hit.payload, "score:", hit.score)
