import os

from locust import HttpUser, task, between

HOST = "https://schematic-dev.api.sagebionetworks.org/v1"
EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)
HTAN_SCHEMA_URL = "https://raw.githubusercontent.com/ncihtan/data-models/v24.7.1/HTAN.model.jsonld" 
DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow_config/main/HTAN/dataflow_component.csv"
AD_SCHEMA_URL = "https://raw.githubusercontent.com/adknowledgeportal/data-models/refs/heads/xman-testing/AD.test.model.jsonld"
# class VersionCheckUser(HttpUser):
#     fixed_count = 1
#     @task
#     def get_version(self):
#         self.client.get("/version")


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

    @task
    def populate_manifest(self):
        """
        Task to populate the manifest by uploading a CSV file
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "data_model_labels": "class_label",
            "data_type": "Patient",
            "title": "Example",
            "return_excel": False
        }
        # File to be uploaded
        file_path_manifest = "test_manifests/synapse_storage_manifest_patient.csv"
        files = {
            'csv_file': (os.path.basename(file_path_manifest), open(file_path_manifest, 'rb'), 'text/csv')
        }
        # Sending POST request to the API
        with self.client.post("/manifest/populate", params=params, headers=self.headers, files=files, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code {response.status_code}")


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


class ManifestSubmissionUser(HttpUser):
    wait_time = between(1, 5)  # Users will wait between 1 and 5 seconds between tasks

    def on_start(self):
        # Optionally authenticate or set up other necessary state here
        self.token = f"Bearer {os.environ['TOKEN']}"
        self.headers = {"Authorization": self.token}

    def execute_manifest_submission(self, data_type_lst, record_type_lst, params, description, file_path_manifest):
        """
        Simulate submitting a manifest with different parameters set by users and record latency
        """
        combined_list = []
        files = {
            'file_name': (os.path.basename(file_path_manifest), open(file_path_manifest, 'rb'), 'text/csv')
        }
        for opt in data_type_lst:
            for record_type in record_type_lst:
                params["data_type"] = opt
                params["manifest_record_type"] = record_type

                # Simulating the submission using a POST request
                with self.client.post("/model/submit", headers=self.headers, params=params, files=files, catch_response=True) as response:
                    if response.status_code == 200:
                        response.success()
                        print(f"Manifest {record_type} {file_path_manifest} submitted successfully.")
                    else:
                        response.failure(f"Failed to submit manifest {record_type} {file_path_manifest}. Status code: {response.status_code}")

        return combined_list

    @task
    def submit_example_manifest_patient(self):
        """
        Submitting an example data manifest as a patient
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "dataset_id": "syn51376664",
            "asset_view": "syn51376649",
            "restrict_rules": True,
            # "use_schema_label": True,
            "data_model_labels": "class_label",
            "table_manipulation": "replace",
        }

        data_type_lst = [None]
        record_type_lst = ["table_and_file", "file_only"]
        description = "Submitting an example manifest as"

        self.execute_manifest_submission(
            data_type_lst,
            record_type_lst,
            params,
            description,
            file_path_manifest="test_manifests/synapse_storage_manifest_patient.csv"
        )

    @task
    def submit_dataflow_manifest(self):
        """
        Submitting a dataflow manifest for HTAN as file only
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "dataset_id": "syn51376664",
            "asset_view": "syn51376649",
            "restrict_rules": True,
            "data_model_labels": "class_label",
            "table_manipulation": "replace",
        }

        data_type_lst = [None]
        record_type_lst = ["file_only"]
        description = "Submitting a dataflow manifest for HTAN as"

        self.execute_manifest_submission(
            data_type_lst,
            record_type_lst,
            params,
            description,
            file_path_manifest="test_manifests/synapse_storage_manifest_dataflow.csv"
        )


class ManifestValidateUser(HttpUser):
    """
    Locust User for manifest validation tasks
    """
    wait_time = between(1, 3)  # Wait time between tasks

    def on_start(self):
        # Optionally authenticate or set up other necessary state here
        self.token = f"Bearer {os.environ['TOKEN']}"
        self.headers = {"Authorization": self.token}

    def execute_validate_manifest(self, params, file_path_manifest):
        """
        Simulate submitting a manifest with different parameters set by users and record latency
        """
        files = {
            'file_name': (os.path.basename(file_path_manifest), open(file_path_manifest, 'rb'), 'text/csv')
        }
        # Simulating the submission using a POST request
        with self.client.post("/model/validate", headers=self.headers, params=params, files=files, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Manifest {params} {file_path_manifest} submitted successfully.")
            else:
                response.failure(f"Failed to submit manifest {params} {file_path_manifest}. Status code: {response.status_code}")

    @task
    def validate_patient_manifest(self):
        """
        Task to validate patient manifest with different restrict rules
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "data_type": "Patient",
        }
        # Validate with restrict rules True and False
        for restrict_rule in [True, False]:
            params['restrict_rules'] = restrict_rule
            self.execute_validate_manifest(
                params=params,
                file_path_manifest="test_manifests/synapse_storage_manifest_patient.csv",
            )
    @task
    def validate_biospecimen_manifest(self):
        """
        Task to validate HTAN manifest with Biospecimen data type
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "data_type": "Biospecimen",
            "restrict_rules": False
        }
        self.execute_validate_manifest(
            params=params,
            file_path_manifest="test_manifests/synapse_storage_manifest_HTAN_HMS.csv",
        )

    @task
    def validate_patient_manifest(self):
        """
        Task to validate patient manifest with different restrict rules
        """
        params = {
            "schema_url": AD_SCHEMA_URL,
            "data_type": "BiospecimenMetadataTemplate",
            "restrict_rule": False,
            "project_scope": "syn58705738",
            "data_model_labels": "class_label",
            "asset_view": "syn58711351"
        }
        response = self.execute_validate_manifest(
            params=params,
            file_path_manifest="test_manifests/biospecimen_filled_fail_1.csv",
        )
        if response is not None:
            import json
            decoded_data_new = response.decode('utf-8')
            response = json.loads(decoded_data_new)

            # Define expected output for assertion
            expected_data_new = {
                "errors": [
                    [
                        ["2", "3", "4"],
                        "individualID",
                        "Value(s) ['R1234567', 'R1234567', 'wrong_id'] from row(s) ['2', '3', '4'] of the attribute individualID in the source manifest are not present in only one other manifest. ",
                    ["R1234567", "R1234567", "wrong_id"]
                    ],
                    [
                        ["2", "3", "4"],
                        "specimenID",
                        "Value(s) ['AD_DLPFC_007', 'R1234567_DLPFC_01', 'R1234567_TCX_01'] from row(s) ['2', '3', '4'] of the attribute specimenID in the source manifest are not present in only one other manifest. ",
                        ["AD_DLPFC_007", "R1234567_DLPFC_01", "R1234567_TCX_01"]
                    ]
                ],
                "warnings": []
            }

            # Perform assertion
            assert response == expected_data_new, "The response data does not match the expected data."
    
    @task
    def validate_biospecimen_manifest(self):
        """
        Task to validate HTAN manifest with Biospecimen data type
        """
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "data_type": "Biospecimen",
            "restrict_rules": False
        }
        self.execute_validate_manifest(
            params=params,
            file_path_manifest="test_manifests/synapse_storage_manifest_HTAN_HMS.csv",
        )


class VisualizeUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Optionally authenticate or set up other necessary state here
        self.token = f"Bearer {os.environ['TOKEN']}"
        self.headers = {"Authorization": self.token}

    @task
    def get_attributes(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "data_model_labels": "class_label"
        }
        with self.client.get("/visualize/attributes", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Attributes fetched successfully with params: {params}.")
            else:
                response.failure(f"Failed to fetch attributes. Status code: {response.status_code}, Params: {params}")

    @task
    def get_component(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "component": "Patient",
            "include_index": "false",
            "data_model_labels": "class_label"
        }
        with self.client.get("/visualize/component", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Component fetched successfully with params: {params}.")
            else:
                response.failure(f"Failed to fetch component. Status code: {response.status_code}, Params: {params}")

    @task
    def get_tangled_tree_layers(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "figure_type": "component",
            "data_model_labels": "class_label"
        }
        with self.client.get("/visualize/tangled_tree/layers", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Tangled tree layers fetched successfully with params: {params}.")
            else:
                response.failure(f"Failed to fetch tangled tree layers. Status code: {response.status_code}, Params: {params}")

    @task
    def get_tangled_tree_text(self):
        params = {
            "schema_url": EXAMPLE_SCHEMA_URL,
            "figure_type": "component",
            "text_format": "plain",
            "data_model_labels": "class_label"
        }
        with self.client.get("/visualize/tangled_tree/text", headers=self.headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"Tangled tree text fetched successfully with params: {params}.")
            else:
                response.failure(f"Failed to fetch tangled tree text. Status code: {response.status_code}, Params: {params}")
