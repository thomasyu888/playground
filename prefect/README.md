## Prefect

Easiest way to automate your data: [prefect.io](https://www.prefect.io/).  Followed [tutorial](https://docs.prefect.io/core/tutorial/01-etl-before-prefect.html)

As a test, I am going to string together `synapsemonitor` and `prefect` to create a very small ETL pipeline.

1. Install packages
    ```
    conda create -n prefect python=3.7
    pip install -r requirements.txt
    ```
1. Synapse monitor
    ```
    synapsemonitor view syn24187217 --days 40
    ```
1. Stringing together `synapsemonitor` with `prefect`
    ```
    python demo.py
    ```
1. Showing dashboard
    ```
    prefect backend server
    prefect server start
    # visit http://localhost:8080/default
    prefect agent local start
    ```