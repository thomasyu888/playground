import os

from locust import HttpUser, task, between

HOST = "https://schematic-dev.api.sagebionetworks.org/v1"
EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)

DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow_config/main/HTAN/dataflow_component.csv"

class VersionCheckUser(HttpUser):
    @task
    def get_version(self):
        self.client.get("/version")


class ManifestGeneratorUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 to 5 seconds between tasks

    def on_start(self):
        # Optionally authenticate or set up other necessary state here
        self.token = f"Bearer {os.environ['TOKEN']}"
        self.headers = {"Authorization": self.token}

    @task
    def generate_new_manifest_example_model_gsheet(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "title": "example",
            "data_type": "Patient",
            "use_annotations": False
        }

        with self.client.get("/manifest/generate", params=params, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print("Manifest (Google Sheet) generated successfully.")
            else:
                response.failure(f"Failed to generate manifest. Status code: {response.status_code}")

    @task
    def generate_new_manifest_example_model_excel(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "title": "example",
            "data_type": "Patient",
            "use_annotations": False,
            "output": "excel"
        }

        with self.client.get("/manifest/generate", params=params, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # TODO Add md5 check for manifest
                print("Manifest (Excel) generated successfully.")
            else:
                response.failure(f"Failed to generate manifest (Excel). Status code: {response.status_code}")

    @task
    def generate_new_manifest_HTAN_google_sheet(self):
        params = {
            "schema_url": HTAN_SCHEMA_URL,
            "title": "example",
            "data_type": "Patient",
            "use_annotations": False
        }

        with self.client.get("/manifest/generate", params=params, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # TODO Add md5 check for manifest
                print("HTAN manifest (Google Sheet) generated successfully.")
            else:
                response.failure(f"Failed to generate HTAN manifest. Status code: {response.status_code}")

    @task
    def generate_existing_manifest_google_sheet(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "title": "example",
            "data_type": "Patient",
            "use_annotations": False,
            "dataset_id": "syn51078367",
            "asset_view": "syn23643253"
        }

        with self.client.get("/manifest/generate", params=params, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # TODO Add md5 check for manifest
                print("Existing manifest (Google Sheet) generated successfully.")
            else:
                response.failure(f"Failed to generate existing manifest. Status code: {response.status_code}")



class AssetStorageUser(HttpUser):
    wait_time = between(1, 3)  # Simulate waiting between requests (in seconds)

    def on_start(self):
        # Optionally authenticate or set up other necessary state here
        self.token = f"Bearer {os.environ['TOKEN']}"
        self.headers = {"Authorization": self.token}

    @task
    def retrieve_asset_view_as_json(self):
        """
        Retrieve asset view table as a JSON.
        """
        asset_view = "syn23643253"
        params = {"asset_view": asset_view, "return_type": "json"}

        with self.client.get("/storage/assets/tables", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Retrieved asset view {asset_view} successfully.")
            else:
                response.failure(f"Failed to retrieve asset view {asset_view}. Status code: {response.status_code}")

    @task
    def retrieve_project_datasets(self):
        """
        Retrieve all datasets under a given example project.
        """
        asset_view = "syn23643253"
        project_id = "syn26251192"
        params = {"asset_view": asset_view, "project_id": project_id}

        with self.client.get("/storage/project/datasets", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Retrieved all datasets for project {project_id} successfully.")
            else:
                response.failure(f"Failed to retrieve datasets for project {project_id}. Status code: {response.status_code}")

    @task
    def retrieve_project_datasets_HTAN(self):
        """
        Retrieve all datasets under a given testing HTAN project.
        """
        asset_view = "syn20446927"  # HTAN asset view
        project_id = "syn32596076"  # HTAN center c
        params = {"asset_view": asset_view, "project_id": project_id}

        with self.client.get("/storage/project/datasets", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Retrieved all HTAN datasets for project {project_id} successfully.")
            else:
                response.failure(f"Failed to retrieve HTAN datasets for project {project_id}. Status code: {response.status_code}")