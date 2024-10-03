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
EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"


@pytest.fixture(scope='module')
def setup_api():
    # Assuming the API is running locally
    url = f'{BASE_URL}/ui'
    response = requests.get(url)
    assert response.status_code == 200, f"Failed to connect to API: {response.text}"
    return BASE_URL


def test_validate_manifest_valid(setup_api):
    """https://sagebionetworks.jira.com/wiki/spaces/SCHEM/pages/3055779846/Schematic+API+test+plan#Manifest-validation
    Test that we can validate a simple manifest and expect no errors.

    Expected response:
    {
        "errors": [],
        "warnings": []
    }
    """
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': EXAMPLE_SCHEMA_URL,
        'data_type': 'Patient',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('example_patient_pass.csv', open('example_patient_pass.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    print(response.json())
    print(hashlib.md5(response.content).hexdigest())
    assert hashlib.md5(response.content).hexdigest() == "c534acf519060c048565ea9f1e8fa837"
    assert response.status_code == 200, "Should be 200 status code"


def test_validate_manifest_invalid_patient_manifest(setup_api):
    """
    https://sagebionetworks.jira.com/wiki/spaces/SCHEM/pages/3055779846/Schematic+API+test+plan#Manifest-validation
    Test that a manifest is invalid

    Errors:
    {
        "errors": [
            [
            "2",
            "Family History",
            "For attribute Family History in row 2 it does not appear as if you provided a comma delimited string. Please check your entry ('Random'') and try again.",
            "Random"
            ],
            [
            "2",
            "Family History",
            "'Random' is not one of ['Colorectal', 'Breast', 'Lung', 'Prostate', 'Skin', '']",
            "Random"
            ],
            [
            "2",
            "Cancer Type",
            "'Random' is not one of ['Colorectal', 'Breast', 'Lung', 'Prostate', 'Skin', '']",
            "Random"
            ]
        ],
        "warnings": []
    }

    Note: this list ['Colorectal', 'Breast', 'Lung', 'Prostate', 'Skin', ''] shuffles in order, which creates different md5 checksums
    """
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': EXAMPLE_SCHEMA_URL,
        'data_type': 'Patient',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('test_patient_manifest_invalid.csv', open('test_patient_manifest_invalid.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    assert response.status_code == 200, "Should be 200 status code"
    print(response.json())
    # assert response.content == b'{\n  "errors": [\n    [\n      "2",\n      "Family History",\n      "For attribute Family History in row 2 it does not appear as if you provided a comma delimited string. Please check your entry (\'Random\'\') and try again.",\n      "Random"\n    ],\n    [\n      "2",\n      "Family History",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ],\n    [\n      "2",\n      "Cancer Type",\n      "\'Random\' is not one of [\'Skin\', \'Breast\', \'Lung\', \'Colorectal\', \'Prostate\', \'\']",\n      "Random"\n    ]\n  ],\n  "warnings": []\n}\n'
    # HACK the returned text will have a list of values that may appear in random order.  Because of that, the
    # md5 of the string may 5 different values.
    print(hashlib.md5(response.content).hexdigest())
    assert hashlib.md5(response.content).hexdigest() in ["204b34c35f5f68707200fdc3baa3fde6", "2ceeb3acf2af972ea9e4e2b89e0a4242", "04b809242ab7ec9845b3b2fc023695ab"]


def test_validate_manifest_with_mock_component(setup_api, manifest_params):
    """Validate a manifest that triggers simple cross manifest validation rules
    https://sagebionetworks.jira.com/wiki/spaces/SCHEM/pages/3055779846/Schematic+API+test+plan#Extended-test-cases.1
    Expected results:
    {
        "errors": [],
        "warnings": [
            [None, "Check Recommended", "Column 'Check Recommended' is recommended but empty.", None],
            [None, "Check Match at Least", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match at Least' and validation rule 'matchAtLeastOne Patient.PatientID' set. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None],
            [None, "Check Match at Least values", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match at Least values' and validation rule 'matchAtLeastOne MockComponent.checkMatchatLeastvalues' value. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None],
            [None, "Check Match Exactly", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match Exactly' and validation rule 'matchExactlyOne MockComponent.checkMatchExactly' set. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None],
            [None, "Check Match Exactly values", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match Exactly values' and validation rule 'matchExactlyOne MockComponent.checkMatchExactlyvalues' value. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None],
            [None, "Check Match None", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match None' and validation rule 'matchNone MockComponent.checkMatchNone' set error. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None],
            [None, "Check Match None values", "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute 'Check Match None values' and validation rule 'matchNone MockComponent.checkMatchNonevalues' value error. It is assumed this is the first manifest in a series to be submitted, so validation will pass for now, and will run again when there are manifests uploaded to validate against.", None]
        ]
    }
    """
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    import synapseclient
    syn = synapseclient.login()
    # Make sure theres no manfiests in the asset store
    files_to_delete = syn.getChildren("syn63582792")
    for file_to_delete in files_to_delete:
        syn.delete(file_to_delete['id'])
    # HACK force index the fileview
    syn.tableQuery("select * from syn63596704")
    params = {
        'schema_url': EXAMPLE_SCHEMA_URL,
        'data_type': 'MockComponent',
        'data_model_labels': 'class_label',
        'restrict_rules': False,
        "asset_view": "syn63596704"
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('MockComponent-cross-manifest-1.csv', open('MockComponent-cross-manifest-1.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    assert response.status_code == 200, "Should be 200 status code"
    print(response.json())
    assert hashlib.md5(response.content).hexdigest() == "960e64f48af0c4204e8dc2b497bd8025"


def test_validate_manifest_with_cross_manifest_validation(setup_api, manifest_params):
    """Validate a manifest that triggers simple rule combination validation rules 
    https://sagebionetworks.jira.com/wiki/spaces/SCHEM/pages/3055779846/Schematic+API+test+plan#Extended-test-cases.1

    Current errors:
    {
        "errors": [
            [
            ["2"],
            "Check Match None",
            "Value(s) ['200'] from row(s) ['2'] for the attribute Check Match None in the source manifest are not unique. Manifest(s) ['syn63620104'] contain duplicate values.",
            ["200"]
            ],
            [
            ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
            "Check Match None values",
            "Value(s) ['200', '1', '3', '4', '5', '10', '100', '102', '104', '109', '110', '111', '120', '130'] from row(s) ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'] for the attribute Check Match None values in the source manifest are not unique.",
            ["200", "1", "3", "4", "5", "10", "100", "102", "104", "109", "110", "111", "120", "130"]
            ]
        ],
        "warnings": [
            [
            None,
            "Check Recommended",
            "Column Check Recommended is recommended but empty.",
            None
            ],
            [
            None,
            "Check Match at Least",
            "Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute: Check Match at Least, and validation rule: matchAtLeastOne Patient.PatientID set. It is assumed this is the first manifest in a series to be submitted, so validation will pass, for now, and will run again when there are manifests uploaded to validate against.",
            None
            ],
            [
            ["2", "4", "5", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
            "Check Match Exactly values",
            "Value(s) ['300', '300', '300', '300', '300', '300', '300', '300', '300', '300', '9000', '9000'] from row(s) ['2', '4', '5', '7', '8', '9', '10', '11', '12', '13', '14', '15'] of the attribute Check Match Exactly values in the source manifest are not present in only one other manifest.",
            ["300", "300", "300", "300", "300", "300", "300", "300", "300", "300", "9000", "9000"]
            ]
        ]
    }

    """
    # # Define the URL and query parameters
    # submit_url = f'{setup_api}/model/submit'
    # params = {
    #     'schema_url': EXAMPLE_SCHEMA_URL,
    #     'data_model_labels': 'class_label',
    #     'data_type': 'MockComponent',
    #     'dataset_id': 'syn63582792',
    #     'manifest_record_type': 'file_only',
    #     'restrict_rules': False,
    #     'hide_blanks': False,
    #     'asset_view': 'syn63596704',
    #     'table_column_names': 'class_label',
    #     'annotation_keys': 'class_label',
    #     'file_annotations_upload': True
    # }
    # files = {
    #     'file_name': ('MockComponent-cross-manifest-1.csv', open('MockComponent-cross-manifest-1.csv', 'rb'), 'text/csv')
    # }
    # response = requests.post(submit_url, headers=HEADERS, params=params, files=files)
    # print(response.content)
    # assert response.status_code == 200
    # print(response.json())
    # HACK Store the entitiy directly instead of using the submit endpoint, because it errors out
    import synapseclient
    syn = synapseclient.login()
    syn.store(synapseclient.File("synapse_storage_manifest_mockcomponent.csv", parent="syn63582792"))
    syn.tableQuery("select * from syn63596704")
    url = f'{setup_api}/model/validate'
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
    assert response.status_code == 200, "Should be 200 status code"
    print(response.json())
    print(hashlib.md5(response.content).hexdigest())
    # assert hashlib.md5(response.content).hexdigest() in ["15cde5667659947ef45c5f1ad7e958c6", "960139320d131ed76def14720c2dc734"]
    assert hashlib.md5(response.content).hexdigest() == "960139320d131ed76def14720c2dc734"

def test_validate_manifest_with_simple_rule_combos(setup_api, manifest_params):
    """Validate a manifest that triggers filename validation rules (should be sufficiently covered by integration test)
    https://sagebionetworks.jira.com/wiki/spaces/SCHEM/pages/3055779846/Schematic+API+test+plan#Extended-test-cases.1

    TODO This is known to error out on the July release
    """
    # Define the URL and query parameters
    url = f'{setup_api}/model/validate'
    params = {
        'schema_url': EXAMPLE_SCHEMA_URL,
        'data_type': 'MockComponent',
        'data_model_labels': 'class_label',
        'restrict_rules': False
    }
    # Define the file to be uploaded (using a mock file here)
    files = {'file_name': ('Mock_Component_rule_combination.csv', open('Mock_Component_rule_combination.csv', 'rb'), 'text/csv')}

    # Make the POST request with parameters, headers, and file
    response = requests.post(url, headers=HEADERS, params=params, files=files)
    print(response.content)
    assert response.status_code == 200, "Should be 200 status code"
    print(response.json())
