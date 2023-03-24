"""Sample script to get used to the Mixpanel event format."""
import gzip
import json
import time
import os

from dotenv import load_dotenv
import requests


load_dotenv()

PROJECT_ID = "2943651"  # mixpanel.com/project/<YOUR_PROJECT_ID>
USER = "testing.fe6ab4.mp-service-account"  # Service Account user
PASS = os.getenv("PASS")  # Service Account password


# int(time.time())
sample_events = [
    {
        "event": "release",
        "properties": {
            # These properties are required
            "time": 1672621200,
            "distinct_id": "GENIE",
            "$insert_id": "04ce0cf4-a633-4371-b665-9b45317b4976",
            # Any other properties are optional
            'name': "release_13",
            "number_of_samples": 167423,
            "number_of_variants": 1432225
        },
    },
    {
        "event": "release",
        "properties": {
            # These properties are required
            "time": 1664668800,
            "distinct_id": "GENIE",
            "$insert_id": "04ce0cf4-a633-4371-b665-9b45317b4976",
            # Any other properties are optional
            'name': "release_13",
            "number_of_samples": 153554,
            "number_of_variants": 1261267
        },
    },
]


print("Ingesting ", sample_events)

# Convert to ndJSON
payload = "\n".join([json.dumps(e) for e in sample_events])
head = {"Content-Type": "application/x-ndjson", "Content-Encoding": "gzip"}
resp = requests.post(
    "https://api.mixpanel.com/import",
    params={"strict": "1", "project_id": PROJECT_ID},
    auth=(USER, PASS),
    headers=head,
    data=gzip.compress(payload.encode("utf-8")),
)

print(resp.json())