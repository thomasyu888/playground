

import requests
import os
import json

import synapseclient
syn = synapseclient.login()


HTAN_SCHEMA_URL = "https://raw.githubusercontent.com/ncihtan/data-models/v24.7.1/HTAN.model.jsonld" 
AD_SCHEMA_URL = "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.jsonld"
NF_SCHEMA_URL = "https://raw.githubusercontent.com/nf-osi/nf-metadata-dictionary/v9.7.0/NF.jsonld"
BASE_URL = "https://schematic-dev.api.sagebionetworks.org/v1"
AUTH =  f"Bearer {os.environ['TOKEN']}"
HEADERS = {"Authorization": AUTH}


def execute_validate_manifest(params, file_path_manifest):
    """
    Simulate submitting a manifest with different parameters set by users and record latency
    """
    files = {
        'file_name': (os.path.basename(file_path_manifest), open(file_path_manifest, 'rb'), 'text/csv')
    }
    try:
        # Simulating the submission using a POST request
        response = requests.post(f"{BASE_URL}/model/validate", headers=HEADERS, params=params, files=files)

        # Check if the request was successful
        if response.status_code == 200:
            print("Response content:", response.content.decode('utf-8'))  # Decode content if necessary
            print(f"Manifest {params} from {file_path_manifest} submitted successfully.")
            return response.content.decode('utf-8')
        else:
            print(f"Submission failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def run_validation_on_manifests(asset_view: str, schema_url: str, program: str):
    """Execute validation on manifests created after 2024-08-01

    Args:
        asset_view: The asset view to query for manifests
        schema_url: Schema URL to validate against
    """
    manifests = syn.tableQuery(
        f"SELECT * FROM {asset_view} where name like 'synapse_storage_manifest%' and createdOn > '2024-08-01'"
    )

    manifests_df = manifests.asDataFrame()

    params = {
        "schema_url": schema_url,
        "restrict_rule": False,
        "data_model_labels": "class_label",
        "asset_view": asset_view
    }
    for _, row in manifests_df.iterrows():
        file = syn.get(row['id'])
        params["data_type"] = file.annotations.get('Component')
        if params['data_type'] is None:
            continue
        params["project_scope"] = row['projectId']
        response = execute_validate_manifest(
            params=params,
            file_path_manifest=file.path,
        )
        if response is not None:
            response_dict = json.loads(response)
            with open(f"{row['id']}_{file.modifiedOn}_validation_{program}_data_model.json", "w") as f:
                json.dump(response_dict, f)


run_validation_on_manifests("syn20446927", HTAN_SCHEMA_URL, "htan")
run_validation_on_manifests("syn51324810", AD_SCHEMA_URL, "ad")
run_validation_on_manifests("syn16858331", NF_SCHEMA_URL, "nf")
