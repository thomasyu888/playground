import argparse
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Optional

import pandas as pd
import synapseclient
import json

class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging.
    """
    def format(self, record):
        # Convert log record to a dictionary
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add custom fields from `extra` if they exist
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        return json.dumps(log_record, ensure_ascii=False)

def setup_custom_json_logger(name: str, log_file: str = None, level: int = logging.INFO):
    """
    Sets up a logger that outputs logs in JSON format.

    Parameters:
        name (str): The name of the logger.
        log_file (str, optional): Path to the log file. If None, logs are sent to the console.
        level (logging.Level): The logging level. Default is logging.INFO.

    Returns:
        logging.Logger: Configured custom JSON logger.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a handler
    if log_file:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    # Set the custom JSON formatter
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger

JSONLOGGER = setup_custom_json_logger(name="custom_json_logger", log_file="validation_results.json")


def _cross_validate_dataframe(dataframe: pd.DataFrame, column: str, reference_df: pd.DataFrame, reference_column: str) -> bool:
    """
    Validates that all values in the specified column of a dataframe
    exist in the specified column of a reference dataframe.

    Parameters:
        dataframe (pd.DataFrame): The dataframe to validate.
        column (str): The column in the dataframe to validate.
        reference_df (pd.DataFrame): The reference dataframe.
        reference_column (str): The column in the reference dataframe to validate against.

    Returns:
        bool: True if all values in the dataframe's column exist in the reference column; otherwise, False.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected 'dataframe' to be a pandas DataFrame, got {type(self.dataframe).__name__} instead.")
    if not isinstance(reference_df, pd.DataFrame):
        raise TypeError(f"Expected 'reference_df' to be a pandas DataFrame, got {type(self.dataframe).__name__} instead.")
    if reference_column not in reference_df.columns:
        raise ValueError(f"Reference column '{reference_column}' not found in reference_df.")
    if column not in dataframe.columns:
        raise ValueError(f"column '{column}' not found in dataframe.")

    reference_values = set(reference_df[reference_column])
    column_values = set(dataframe[column])
    return column_values.issubset(reference_values)


def parse_json_logs_to_dataframe(log_file_path: str) -> pd.DataFrame:
    """
    Parses a log file where each line is a JSON-formatted log entry
    and converts it into a Pandas DataFrame.

    Args:
        log_file_path (str): Path to the log file.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed log entries.
    """
    log_entries = []
    with open(log_file_path, 'r') as file:
        for line in file:
            try:
                log_entry = json.loads(line.strip())
                log_entries.append(log_entry)
            except json.JSONDecodeError as e:
                print(f"Failed to parse line: {line.strip()} - {e}")

    # Convert the list of dictionaries into a DataFrame
    return pd.DataFrame(log_entries)


def parse_arguments():
    """
    Parses command-line arguments for Synapse validation script.

    Returns:
        argparse.Namespace: Parsed arguments containing Synapse data, reference Synapse ID, and reference column.
    """
    parser = argparse.ArgumentParser(
        description="Validate Synapse data against a reference file."
    )

    # Add arguments
    parser.add_argument(
        "--target-synapse-ids",
        required=True,
        nargs="+",
        metavar=("SYNAPSE_ID", "COLUMN"),
        help=(
            "Pairs of Synapse IDs and their corresponding columns. "
            "Provide in the format: SYNAPSE_ID COLUMN. "
            "Example: --synapse-data syn52955031 specimenID syn58849847 specimenID"
        ),
    )
    parser.add_argument(
        "--reference-synapse-id",
        required=True,
        type=str,
        help="The Synapse ID of the reference file. Example: 'syn62661392'.",
    )
    parser.add_argument(
        "--reference-column",
        required=True,
        type=str,
        help="The column in the reference file to validate against. Example: 'individualID'.",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Convert the synapse-data pairs into a list of tuples
    if len(args.target_synapse_ids) % 2 != 0:
        parser.error("--synapse-data must be provided as pairs of SYNAPSE_ID and COLUMN.")

    args.target_synapse_ids = [
        (args.target_synapse_ids[i], args.target_synapse_ids[i + 1])
        for i in range(0, len(args.target_synapse_ids), 2)
    ]

    return args


@dataclass
class DataReader:
    path_or_identifier: str
    # TODO create a client class that abstracts the implementation details of S3 or any getter
    client: Optional[synapseclient.Synapse] = None
    dataframe: Optional[pd.DataFrame] = None

    def read_data(self):
        """
        Downloads the required files and prepares dataframes.
        """
        data = self.client.get(self.path_or_identifier)
        self.dataframe = pd.read_csv(data.path)


def cross_validation(client, source, source_column, reference, reference_column):
    source_reader = DataReader(path_or_identifier=source, client=client)
    source_reader.read_data()
    reference_reader = DataReader(path_or_identifier=reference, client=client)
    reference_reader.read_data()
    return _cross_validate_dataframe(source_reader.dataframe, source_column, reference_reader.dataframe, reference_column)


def main():
    args = parse_arguments()
    syn = synapseclient.login()
    # Example list of Synapse ID and column name pairs
    # synapse_data = [
    #     ('syn52955031', 'specimenID'),
    #     ('syn58849847', 'specimenID'),
    # ]
    # Synapse ID of the reference file
    # reference_synapse_id = 'syn62661392'
    # reference_column = "individualID"

    target_synapse_ids = args.target_synapse_ids
    reference_synapse_id = args.reference_synapse_id
    reference_column = args.reference_column

    for synapse_id, validate_column in target_synapse_ids:
        print(f"Validating Synapse ID: {synapse_id} on column: {validate_column} against reference: {reference_synapse_id} on column: {reference_column}")
        results = cross_validation(client=syn, source=synapse_id, source_column=validate_column, reference=reference_synapse_id, reference_column=reference_column)
        print("Validation Results:", results)
    validation_results_df = parse_json_logs_to_dataframe("validation_results.json")
    validation_results_df.to_csv("validation_results.csv", index=False)


if __name__ == '__main__':
    main()
