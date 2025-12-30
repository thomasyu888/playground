import os
import tempfile

import synapseclient
import synapseutils as synu

def _write_test_file(file_path: str) -> None:
    """write mock test files"""
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("test is a test file")

def create_local_test_files(num_test_files: int) -> None:
    """create local test files"""
    test_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(test_dir, "test_folder"))
    index = 0
    while index < num_test_files:    
        sample_file = f"{test_dir}/test_folder/sample_file_{index}.txt"
        _write_test_file(sample_file)
        index += 1
    return test_dir


if __name__ == "__main__":
    syn = synapseclient.login()
    project = synapseclient.Project("tyu schematic test")
    project_ent = syn.store(project)
    path_to_manifest_file = "manifest-for-upload.tsv"

    test_dir = create_local_test_files(num_test_files=3000)

    synu.generate_sync_manifest(
        syn=syn,
        directory_path=test_dir,
        parent_id=project_ent.id,
        manifest_path=path_to_manifest_file,
    )
    synu.syncToSynapse(
        syn=syn, manifestFile=path_to_manifest_file, sendMessages=False
    )
