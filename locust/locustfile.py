import os
import uuid

from locust import HttpUser, task, between

HOST = "https://schematic-dev.api.sagebionetworks.org/v1"
EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)

DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow_config/main/HTAN/dataflow_component.csv"

class VersionCheckUser(HttpUser):
    fixed_count = 1
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

class ManifestSubmissionUser(HttpUser):
    wait_time = between(1, 5)  # Users will wait between 1 and 5 seconds between tasks
    fixed_count = 5

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


# class ManifestGenerateAndValidateWorkflowUser(HttpUser):

#     def _generate_errors(self, manifest: pd.DataFrame) -> pd.DataFrame:
#         # generate 50% of each type of filename error
#         manifest.iloc[::2,1]=manifest.iloc[::2,1].map(lambda x: f"err {x}")
#         manifest.iloc[1::2,2]=manifest.iloc[1::2,2].map(lambda x: x[:-1:])
#         return manifest

#     def _save_manifest(self, manifest: pd.DataFrame) -> None:
#         self.manifest_path = f"APITests/test_manifests/filename_{self.num_files}_manifest_{uuid.uuid4()}.csv"
#         manifest.to_csv(self.manifest_path,index=False)
#         return

#     def generate_manifest(self) -> pd.DataFrame:
#         # generate manifest as excel file because generating as dataframe is for existing manifests only
#         params = {
#             "schema_url": self.url,
#             "data_type": "MockFilename",
#             "dataset_id": self.dataset_id,
#             "asset_view": self.asset_view_id,
#             "output_format": "excel"
#         }
#         with self.client.get("/manifest/generate", params=params, headers=self.headers, catch_response=True) as response:
#             if response.status_code == 200:
#                 response.success()
#                 # TODO Add md5 check for manifest
#                 print("Manifest (Excel) generated successfully.")
#                 # response from api when generating a manifest as an excel file is a bytes string
#                 exel_data = BytesIO(response.content)
#                 # openpyxl was best suited to process data of this type
#                 workbook = openpyxl.load_workbook(exel_data)
#                 manifest_sheet = workbook["Sheet1"]

#                 # taken from openpyxl documentation on how to process a worksheet with headers and indices into a dataframe
#                 data =        cols = next(data)[1:]
#                 data = list(data)
#                 idx = [r[0] for r in data]
#                 data = (islice(r, 1, None) for r in data)
#                 manifest = pd.DataFrame(data, index=idx, columns=cols)
#                 manifest = manifest.dropna(axis=1,how='all').dropna(axis=0,how="all")
#                 manifest.reset_index(drop=False,names='Component',inplace=True)

#                 manifest = self._generate_errors(manifest)
#                 self._save_manifest(manifest)
#             else:
#                 response.failure(f"Failed to generate manifest (Excel). Status code: {response.status_code}")

