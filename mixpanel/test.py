"""Sample script to get used to the Mixpanel event format."""
import gzip
import json
import time

import requests

PROJECT_ID = "2943651"  # mixpanel.com/project/<YOUR_PROJECT_ID>
USER = "testing.fe6ab4.mp-service-account"  # Service Account user
PASS = ""  # Service Account password

sample_events = [
    {
        "event": "workflow_run",
        "properties": {
            # These properties are required
            "time": int(time.time()),
            "distinct_id": "workflow_user",
            "$insert_id": "04ce0cf4-a633-4371-b665-9b45317b4976",
            # Any other properties are optional
            "city": "San Francisco",
            "status": "FAIL"
        }
    }
]

sample_events = [
    {
        "event": "my_test_event",
        "properties": {
            # These properties are required
            "time": int(time.time()),
            "distinct_id": "test_user",
            "$insert_id": "04ce0cf4-a633-4371-b665-9b45317b4976",
            # Any other properties are optional
            "city": "San Francisco",
        },
    },
    {
        "event": "another_event",
        "properties": {
            "time": int(time.time()),
            "distinct_id": "test_user_2",
            "$insert_id": "3b033b9a-6bc9-4b70-90c3-a53e11f6896e",
            "city": "Seattle",
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