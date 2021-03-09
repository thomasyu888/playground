#!/usr/bin/env python
import json
import os
import subprocess
import tempfile
import zipfile

import chevron
import pika
import synapseclient


def transform_docker_submission():
    pass


def map_docker_workflow_files(workflow_dir_path):
    """Must contain run_docker.cwl.mustache, workflow.cwl.mustache
    and other tools that are required by workflow.cwl.mustache"""
    workflow_files = os.listdir(workflow_dir_path)
    # workflow_map = {}
    workflow_map = {workflow_file: os.path.abspath(workflow_file)
                    for workflow_file in workflow_files
                    if workflow_file.endswith((".mustache", ".cwl"))}
    required_templates = ["run_docker.cwl.mustache", "workflow.cwl.mustache"]

    for template in required_templates:
        if template not in workflow_map:
            raise ValueError(f"{template} must be part of zip file")

    return workflow_map


def unzip_workflow_files(workflow_zip, tempdir):
    """Unzip workflow file"""
    with zipfile.ZipFile(workflow_zip, 'r') as zip_ref:
        zip_ref.extractall(tempdir)
        workflow_map = map_docker_workflow_files(tempdir)
    return workflow_map


def _get_docker_runjob_inputs(sub, workflow_zip, workflow_input) -> dict:
    """Get run_job inputs for a docker submission.
    Create cwl tool with correct docker hint (via mustache) - subid.cwl.
    Create workflow that uses custom tool - subid_workflow.cwl.
    Create custom queue with submission id, configure it to run
    subid_workflow.cwl.
    Args:
        sub: Submission
    Returns:
        dict: queue_id: Queue id
              wf_jsonyaml: workflow inputs
    """
    # workflow_zip = "./"
    workflow_dir = tempfile.TemporaryDirectory()
    workflow_files = unzip_workflow_files(workflow_zip, workflow_dir.name)
    run_docker_template = workflow_files['run_docker.cwl.mustache']
    workflow_template = workflow_files['workflow.cwl.mustache']

    repo_name = f"{sub.dockerRepositoryName}@{sub.dockerDigest}"
    # mustache template
    # Create docker tool with right docker hint
    cwl_input = {'docker_repository': repo_name,
                 'training': False,
                 'scratch': False}

    with open(run_docker_template, 'r') as mus_f:
        template = chevron.render(mus_f, cwl_input)
    docker_tool_path = os.path.join(workflow_dir.name, f"{sub.id}.cwl")
    with open(docker_tool_path, "w") as sub_f:
        sub_f.write(template)

    # Create workflow with correct run docker step
    workflow_input = {'run_docker_tool': docker_tool_path}
    with open(workflow_template, 'r') as mus_f:
        template = chevron.render(mus_f, workflow_input)
    workflow_path = os.path.join(workflow_dir.name, f"{sub.id}_workflow.cwl")
    with open(workflow_path, "w") as sub_f:
        sub_f.write(template)

    # TODO: This is a dummy value, The input can also be passed in.
    input_dict = {
        "data": {
            "class": "Directory",
            "location": "/Users/tyu/sandbox"
        },
        "output_filename": "prediction.csv"
    }
    # Imagine the workfow + input scenario
    workflow_input_path = os.path.join(workflow_dir.name, f"{sub.id}.json")
    with open(workflow_input_path, "w") as input_f:
        json.dump(input_dict, input_f)



    # This is to ensure validate_and_score.cwl lives in
    # home directory of CWL
    # shutil.copy(VALIDATE_AND_SCORE, ".")
    # attachments = ["file://" + os.path.abspath("validate_and_score.cwl"),
    #                "file://" + os.path.abspath(f"{sub.id}.cwl")]
    process_cmd = ['cwltool', workflow_path, workflow_input_path]
    subprocess.check_call(process_cmd)

    workflow_dir.cleanup()

def fib(n):
    syn = synapseclient.login()
    sub = syn.getSubmission(n)
    sub_status = syn.getSubmissionStatus(n)
    sub_status.status = "EVALUATION_IN_PROGRESS"
    syn.store(sub_status)
    return sub.name


def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(
        exchange='', routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))

    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()


if __name__ == "__main__":
    main()
