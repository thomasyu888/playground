"""Test ETL pipeline with airflow + Synapse
Code pulled from ETL example provided by airflow"""
import json
from datetime import datetime

from airflow.decorators import dag, task
import synapseclient


# [START instantiate_dag]
@dag(schedule_interval=None, start_date=datetime(2021, 1, 1), catchup=False, tags=['synapse'])
def synapse_etl_test():
    """
    ### TaskFlow API Tutorial Documentation
    This is a simple ETL data pipeline example which demonstrates the use of
    the TaskFlow API using three simple tasks for Extract, Transform, and Load.
    Documentation that goes along with the Airflow TaskFlow API tutorial is
    located
    [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html)
    """
    # [END instantiate_dag]

    # [START extract]
    @task()
    def extract():
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """

        syn = synapseclient.Synapse(cache_root_dir="./")
        syn.login()

        ent = syn.get("syn26720118")
        with open(ent.path) as json_f:
            order_data_dict = json.load(json_f)

        # data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'
        # order_data_dict = json.loads(json_f)

        return order_data_dict

    # [END extract]

    # [START transform]
    @task(multiple_outputs=True)
    def transform(order_data_dict: dict):
        """
        #### Transform task
        A simple Transform task which takes in the collection of order data and
        computes the total order value.
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    # [END transform]

    # [START load]
    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple Load task which takes in the result of the Transform task and
        instead of saving it to end user review, just prints it out.
        """

        print(f"Total order value is: {total_order_value:.2f}")

    # [END load]

    # [START main_flow]
    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])
    # [END main_flow]


# [START dag_invocation]
synapse_etl_dag = synapse_etl_test()
# [END dag_invocation]
