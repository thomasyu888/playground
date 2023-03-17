import os

import great_expectations as ge
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import (
    DataContextConfig,
    DatasourceConfig,
    FilesystemStoreBackendDefaults,
)
from great_expectations.data_context.types.resource_identifiers import (
    ExpectationSuiteIdentifier,
)
import pandas as pd

# Build context
context = ge.get_context()
# create datasource configuration
datasource_config = {
    "name": "example_datasource",
    "class_name": "Datasource",
    "module_name": "great_expectations.datasource",
    "execution_engine": {
        "module_name": "great_expectations.execution_engine",
        "class_name": "PandasExecutionEngine",
    },
    "data_connectors": {
        "default_runtime_data_connector_name": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
    },
}

# create data context configuration
data_context_config = DataContextConfig(
    datasources={
        "pandas": DatasourceConfig(
            class_name="Datasource",
            execution_engine={"class_name": "PandasExecutionEngine"},
            data_connectors={
                "default_runtime_data_connector_name": {
                    "class_name": "RuntimeDataConnector",
                    "batch_identifiers": ["default_identifier_name"],
                }
            },
        )
    },
    store_backend_defaults=FilesystemStoreBackendDefaults(
        root_directory=os.path.join(os.getcwd(), "great_expectations")
    ),
)

# build context and add data source
context = BaseDataContext(project_config=data_context_config)
# context.test_yaml_config(yaml.dump(datasource_config))
context.add_datasource(**datasource_config)

# Create expectation suite (this is your suite of tests)
expectation_suite_name = "Testing"
suite = context.create_expectation_suite(
    expectation_suite_name=expectation_suite_name, overwrite_existing=True
)
# Build expectation suite
expectation_configuration = ExpectationConfiguration(
    # Name of expectation type being added
    expectation_type="expect_table_columns_to_match_ordered_list",
    # These are the arguments of the expectation
    # The keys allowed in the dictionary are Parameters and
    # Keyword Arguments of this Expectation Type
    kwargs={
        "column_list": [
            "account_id",
            "user_id",
            "transaction_id",
            "transaction_type",
            "transaction_amt_usd",
        ]
    },
    # This is how you can optionally add a comment about this expectation.
    # It will be rendered in Data Docs.
    # See this guide for details:
    # `How to add comments to Expectations and display them in Data Docs`.
    meta={
        "notes": {
            "format": "markdown",
            "content": "Some clever comment about this expectation. **Markdown** `Supported`",
        }
    },
)
# Add the Expectation to the suite
suite.add_expectation(expectation_configuration=expectation_configuration)

# Extra expectations per column
expectation_configuration = ExpectationConfiguration(
    expectation_type="expect_column_values_to_be_in_set",
    kwargs={
        "column": "transaction_type",
        "value_set": ["purchase", "refund", "upgrade"],
    },
    # Note optional comments omitted
)
suite.add_expectation(expectation_configuration=expectation_configuration)

# Extra expectations
expectation_configuration = ExpectationConfiguration(
    expectation_type="expect_column_values_to_not_be_null",
    kwargs={
        "column": "account_id",
        "mostly": 1.0,
    },
    meta={
        "notes": {
            "format": "markdown",
            "content": "Some clever comment about this expectation. **Markdown** `Supported`",
        }
    },
)
suite.add_expectation(expectation_configuration=expectation_configuration)

context.save_expectation_suite(
    expectation_suite=suite, expectation_suite_name=expectation_suite_name
)

suite_identifier = ExpectationSuiteIdentifier(
    expectation_suite_name=expectation_suite_name
)

context.build_data_docs(resource_identifiers=[suite_identifier])
##Webpage DataDocs opened here:
context.open_data_docs(resource_identifier=suite_identifier)


# Set up and run a Simple Checkpoint for ad hoc validation of our data
checkpoint_name = "manifest_checkpoint"
checkpoint_config = {
    "name": checkpoint_name,
    "config_version": 1,
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": {
                "datasource_name": "example_datasource",
                "data_connector_name": "default_runtime_data_connector_name",
                "data_asset_name": "Manifest",
            },
            "expectation_suite_name": expectation_suite_name,
        }
    ],
}
context.add_checkpoint(**checkpoint_config)


manifest = pd.read_csv("test.csv")
batch_request = {
    "runtime_parameters": {"batch_data": manifest},
    "batch_identifiers": {"default_identifier_name": "manifestID"},
}

results = context.run_checkpoint(
    checkpoint_name=checkpoint_name,
    batch_request={
        "runtime_parameters": {"batch_data": manifest},
        "batch_identifiers": {"default_identifier_name": "manifestID"},
    },
    result_format={"result_format": "COMPLETE"},
)

# Build Data Docs
context.build_data_docs()
# This shows the results of the execution
context.open_data_docs(resource_identifier=suite_identifier)
# This shows the expectations
context.open_data_docs()
