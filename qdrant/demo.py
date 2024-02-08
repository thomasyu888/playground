import os

from dotenv import dotenv_values
import snowflake.connector
from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer

import pandas as pd

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
# Extract public data
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
        is_public
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
    for index, row in df.iterrows()
]

qdrant = QdrantClient(":memory:")

encoder = SentenceTransformer("all-MiniLM-L6-v2")

qdrant.recreate_collection(
    collection_name="synapse_public_entities",
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
        distance=models.Distance.COSINE,
    ),
)

qdrant.upload_points(
    collection_name="synapse_public_entities",
    points=[
        models.Record(
            id=idx, vector=encoder.encode(doc["name"]).tolist(), payload=doc
        )
        for idx, doc in enumerate(documents)
    ],
)

hits = qdrant.search(
    collection_name="synapse_public_entities",
    query_vector=encoder.encode("AACR GENIE").tolist(),
    limit=3,
)
for hit in hits:
    print(hit.payload, "score:", hit.score)



hits = qdrant.search(
    collection_name="synapse_public_entities",
    query_vector=encoder.encode("alien invasion").tolist(),
    query_filter=models.Filter(
        must=[models.FieldCondition(key="year", range=models.Range(gte=2000))]
    ),
    limit=1,
)
for hit in hits:
    print(hit.payload, "score:", hit.score)