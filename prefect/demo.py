from datetime import timedelta
import random
import string

import pandas as pd
from prefect import task, Flow, Parameter
# from prefect.schedules import IntervalSchedule

# from prefect.executors import DaskExecutor
import synapseclient
from synapsemonitor import monitor

syn = synapseclient.login()


def download_file(synid):
    filepath = syn.get(synid).path
    filedf = pd.read_csv(filepath)
    if filedf.empty:
        return "".join([random.choice(string.ascii_lowercase)
                        for n in range(6)])
    return filedf.iloc[0, 0]


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def extract_all_data():
    print("fetching all data...")
    view = syn.tableQuery("select id from syn24187217")
    viewdf = view.asDataFrame()
    all_text = []
    for synid in viewdf['id']:
        filepath = syn.get(synid).path
        filedf = pd.read_csv(filepath)
        if filedf.empty:
            all_text.append("".join([random.choice(string.ascii_lowercase)
                                     for n in range(6)]))
        else:
            all_text.append(filedf.iloc[0, 0])
    # all_text = [download_file(syn, synid) ]
    return all_text


@task(max_retries=3, retry_delay=timedelta(seconds=1))
def extract_last_modified_data(days):
    print("fetching last modified data")
    modified_entities = monitor.find_modified_entities(syn, "syn24187217",
                                                       days=days)
    all_text = [download_file(synid)
                for synid in modified_entities['id']]

    return all_text


@task
def transform(all_data, modified_data):
    print("cleaning & transform modified data...")
    pick_one = random.choice(all_data)
    transformed = [f"{pick_one}--i" for i in modified_data]
    return transformed


@task
def load_all_data(all_data):
    print("saving all data...")
    syn.store(synapseclient.Table("syn25173704", all_data))


@task
def load_transformed_data(transformed_data):
    print("saving modified data...")
    syn.store(synapseclient.Table("syn25173708", transformed_data))


def main():

    # schedule = IntervalSchedule(
    #     start_date=datetime.utcnow() + timedelta(seconds=1),
    #     interval=timedelta(minutes=1),
    # )

    # with Flow("etl", schedule=schedule) as flow:
    with Flow("etl") as flow:
        days = Parameter("days", default=40)
        last_modified_data = extract_last_modified_data(days)
        all_data = extract_all_data()

        transformed_data = transform(all_data, last_modified_data)

        load_all_data(all_data)
        load_transformed_data(transformed_data)

    # flow.register(project_name="tutorial")
    flow.run()
#    flow.visualize()


if __name__ == "__main__":
    main()
