import requests
import os
import json

import synapseclient
syn = synapseclient.login()


HTAN_SCHEMA_URL = "https://raw.githubusercontent.com/ncihtan/data-models/v24.7.1/HTAN.model.jsonld" 
AD_SCHEMA_URL = "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.jsonld"
NF_SCHEMA_URL = "https://raw.githubusercontent.com/nf-osi/nf-metadata-dictionary/v9.7.0/NF.jsonld"
BASE_URL = "https://schematic-staging.api.sagebionetworks.org/v1"
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

import glob

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
        if not glob.glob(f"{row['id']}_*"):
            continue
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


def run_validation_on_all_manifests_htan(asset_view: str, schema_url: str, program: str):
    """Execute validation on manifests created after 2024-08-01

    Args:
        asset_view: The asset view to query for manifests
        schema_url: Schema URL to validate against
    """
    manifests = syn.tableQuery(
        f"SELECT * FROM {asset_view} where name like 'synapse_storage_manifest%' and projectId not in ('syn32596076')"
    )

    manifests_df = manifests.asDataFrame()

    params = {
        "schema_url": schema_url,
        "restrict_rule": False,
        "data_model_labels": "class_label",
        "asset_view": asset_view
    }
    for _, row in manifests_df.iterrows():
        if glob.glob(f"{row['id']}_*"):
            continue
        file = syn.get(row['id'])
        params["data_type"] = file.annotations.get('Component')
        if params['data_type'] is None:
            continue
        params["project_scope"] = row['projectId']
        response = execute_validate_manifest(
            params=params,
            file_path_manifest=file.path,
        )
        print(row['id'])
        if response is not None:
            response_dict = json.loads(response)
            with open(f"{row['id']}_{file.modifiedOn}_validation_{program}_data_model.json", "w") as f:
                json.dump(response_dict, f)

run_validation_on_all_manifests_htan("syn20446927", HTAN_SCHEMA_URL, "htan")

# failed: syn39123262


# class AdManifestValidateUser(HttpUser):
#     """
#     Locust User for manifest validation tasks
#     """
#     wait_time = between(1, 3)  # Wait time between tasks

#     def on_start(self):
#         # Optionally authenticate or set up other necessary state here
#         self.token = f"Bearer {os.environ['TOKEN']}"
#         self.headers = {"Authorization": self.token}

#     def execute_validate_manifest(self, params, file_path_manifest):
#         """
#         Simulate submitting a manifest with different parameters set by users and record latency
#         """
#         files = {
#             'file_name': (os.path.basename(file_path_manifest), open(file_path_manifest, 'rb'), 'text/csv')
#         }
#         # Simulating the submission using a POST request
#         with self.client.post("/model/validate", headers=self.headers, params=params, files=files, catch_response=True) as response:
#             if response.status_code == 200:
#                 response.success()
#                 print(f"Manifest {params} {file_path_manifest} submitted successfully.")
#                 return response.content
#             else:
#                 response.failure(f"Failed to submit manifest {params} {file_path_manifest}. Status code: {response.status_code}")
#         return None



manifests = syn.tableQuery(
    "SELECT id, projectId, name, Component, modifiedOn FROM syn20446927 where name like 'synapse_storage_manifest%' and projectId not in ('syn32596076') ORDER BY modifiedOn DESC"
)
manifests_df = manifests.asDataFrame()
manifests_df['modifiedOn'] = pd.to_datetime(manifests_df['modifiedOn'], unit='ms')
manifests_df.to_csv("htan_manifests.csv", index=False)