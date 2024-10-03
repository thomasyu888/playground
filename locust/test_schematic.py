import pytest
import requests
import os
import hashlib
import pandas as pd
from openpyxl import load_workbook
import requests
import pytest


# Base URL for API
BASE_URL = 'https://schematic-dev.api.sagebionetworks.org/v1'
TOKEN = f"Bearer {os.environ['TOKEN']}"
HEADERS = {"Authorization": TOKEN}

@pytest.fixture(scope='module')
def setup_api():
    # Assuming the API is running locally
    url = f'{BASE_URL}/ui'
    response = requests.get(url)
    assert response.status_code == 200, f"Failed to connect to API: {response.text}"
    return BASE_URL


@pytest.fixture
def manifest_params():
    return {
        "schema_url": "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld",
        "title": "Example",
        "data_type": "Patient",
        "use_annotations": False,
        "dataset_id": None,
        "asset_view": None,
        "output_format": "excel",
        "strict_validation": True
    }


def calculate_md5(file_path):
    md5_hash = hashlib.md5()

    # Open the file in binary mode and read in chunks
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)

    # Get the hexadecimal MD5 hash
    return md5_hash.hexdigest()


# def test_submit_file_manifest(setup_api):
#     url = f'{setup_api}/model/submit'
#     params = {
#         'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
#         'data_model_labels': 'class_label',
#         'manifest_record_type': 'file_only',
#         'dataset_id': 'syn63561474',
#         'asset_view': 'syn63561606'
#     }
    
#     files = {'file_name': open('Example_Biospecimen.csv', 'rb')}  # Mock file

#     response = requests.post(url, params=params, files=files, headers=HEADERS)
    
#     assert response.status_code == 200, f"Failed to submit manifest: {response.text}"
#     assert 'synapse_id' in response.json(), "Manifest submission did not return synapse ID"

# def test_submit_annotated_manifest(setup_api):
#     url = f'{setup_api}/model/submit'
#     params = {
#         'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
#         'data_model_labels': 'class_label',
#         'file_annotations_upload': True,
#         'manifest_record_type': 'table_and_file',
#         'dataset_id': 'syn63561911',
#         'asset_view': 'syn63561920'
#     }

#     files = {'file_name': open('Annotated_BulkRNA_manifest.csv', 'rb')}  # Mock file

#     response = requests.post(url, params=params, files=files, headers=HEADERS)
    
#     assert response.status_code == 200, f"Failed to submit annotated manifest: {response.text}"
#     assert 'synapse_id' in response.json(), "Manifest submission did not return synapse ID"


# def test_validate_manifest(setup_api):
#     url = f'{setup_api}/model/validate'
#     params = {
#         'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
#         'data_type': 'Patient'
#     }

#     files = {'file_name': open('Valid_Patient_Manifest.csv', 'rb')}  # Mock file

#     response = requests.post(url, params=params, files=files, headers=HEADERS)
    
#     assert response.status_code == 200, f"Manifest validation failed: {response.text}"
#     assert 'warnings' not in response.json(), "Unexpected warnings during validation"
#     assert 'errors' not in response.json(), "Validation errors found"


# def test_validate_invalid_manifest(setup_api):
#     url = f'{setup_api}/model/validate'
#     params = {
#         'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
#         'data_type': 'Patient'
#     }

#     files = {'file_name': open('Invalid_Patient_Manifest.csv', 'rb')}  # Mock invalid file

#     response = requests.post(url, params=params, files=files)
    
#     assert response.status_code == 200, f"Manifest validation failed: {response.text}"
#     assert 'errors' in response.json(), "Expected validation errors"

def test_validate_manifest_valid(setup_api, manifest_params):
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
        'data_type': 'Patient',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('example_patient_pass.csv', open('example_patient_pass.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    # assert response.content == b'{\n  "errors": [\n    [\n      "2",\n      "Family History",\n      "For attribute Family History in row 2 it does not appear as if you provided a comma delimited string. Please check your entry (\'Random\'\') and try again.",\n      "Random"\n    ],\n    [\n      "2",\n      "Family History",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ],\n    [\n      "2",\n      "Cancer Type",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ]\n  ],\n  "warnings": []\n}\n'
    # HACK the returned text will have a list of values that may appear in random order.  Because of that, the
    # md5 of the string may 5 different values.
    print(hashlib.md5(response.content).hexdigest())
    assert hashlib.md5(response.content).hexdigest() == "c534acf519060c048565ea9f1e8fa837"
    assert response.status_code == 200, "Should be 200 status code"


def test_validate_manifest_invalid_patient_manifest(setup_api, manifest_params):
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
        'data_type': 'Patient',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('test_patient_manifest_invalid.csv', open('test_patient_manifest_invalid.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    # assert response.content == b'{\n  "errors": [\n    [\n      "2",\n      "Family History",\n      "For attribute Family History in row 2 it does not appear as if you provided a comma delimited string. Please check your entry (\'Random\'\') and try again.",\n      "Random"\n    ],\n    [\n      "2",\n      "Family History",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ],\n    [\n      "2",\n      "Cancer Type",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ]\n  ],\n  "warnings": []\n}\n'
    # HACK the returned text will have a list of values that may appear in random order.  Because of that, the
    # md5 of the string may 5 different values.
    print(hashlib.md5(response.content).hexdigest())
    assert hashlib.md5(response.content).hexdigest() in ["204b34c35f5f68707200fdc3baa3fde6", "2ceeb3acf2af972ea9e4e2b89e0a4242", "04b809242ab7ec9845b3b2fc023695ab"]
    assert response.status_code == 200, "Should be 200 status code"


def test_validate_manifest_with_mock_component(setup_api, manifest_params):
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    import synapseclient
    syn = synapseclient.login()
    # Make sure theres no manfiests in the asset store
    files_to_delete = syn.getChildren("syn63582792")
    for file_to_delete in files_to_delete:
        syn.delete(file_to_delete['id'])

    params = {
        'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
        'data_type': 'MockComponent',
        'data_model_labels': 'class_label',
        'restrict_rules': False,
        "asset_view": "syn63596704"
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('MockComponent-cross-manifest-1.csv', open('MockComponent-cross-manifest-1.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    assert hashlib.md5(response.content).hexdigest() == "960e64f48af0c4204e8dc2b497bd8025"
    assert response.status_code == 200, "Should be 200 status code"


# TODO add the submit to this...
# curl -X 'POST' \
#   'https://schematic-dev.api.sagebionetworks.org/v1/model/submit?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&data_model_labels=class_label&data_type=MockComponent&dataset_id=syn63582792&manifest_record_type=file_only&restrict_rules=false&hide_blanks=false&asset_view=syn63596704&table_column_names=class_label&annotation_keys=class_label&file_annotations_upload=true' \
#   -H 'accept: application/json' \
#   -H 'Authorization: Bearer ..----LdhMRDA' \
#   -H 'Content-Type: multipart/form-data' \
#   -F 'file_name=@MockComponent-cross-manifest-1.csv;type=text/csv'
# TODO look into this...
def test_validate_manifest_with_cross_manifest_validation(setup_api, manifest_params):
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    # TODO: add submit first...
    params = {
        'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
        'data_type': 'MockComponent',
        'data_model_labels': 'class_label',
        'restrict_rules': False,
        "asset_view": "syn63596704",
        "project_scope": "syn63582791"
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('MockComponent-cross-manifest-1.csv', open('MockComponent-cross-manifest-1.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    print(hashlib.md5(response.content).hexdigest())
    assert hashlib.md5(response.content).hexdigest() == "15cde5667659947ef45c5f1ad7e958c6"
    assert response.status_code == 200, "Should be 200 status code"


def test_validate_manifest_with_simple_rule_combos(setup_api, manifest_params):
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': 'https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld',
        'data_type': 'MockComponent',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('Mock_Component_rule_combination.csv', open('Mock_Component_rule_combination.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    print(response.status_code)
