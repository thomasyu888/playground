from dataclasses import dataclass
from datetime import datetime
import logging

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


@dataclass
class DataFrameValidator:
    """
    A class to represent a dataframe and its corresponding column for validation.

    Attributes:
        dataframe (pd.DataFrame): The dataframe to validate.
        column (str): The column name in the dataframe to validate.
    """
    dataframe: pd.DataFrame
    column: str

    def __post_init__(self):
        if not isinstance(self.dataframe, pd.DataFrame):
            raise TypeError(f"Expected 'dataframe' to be a pandas DataFrame, got {type(self.dataframe).__name__} instead.")

    def validate(self, reference_df, reference_column):
        """
        Validates that all values in the specified column of the dataframe
        exist in the specified column of a reference dataframe.

        Args:
            reference_df (pd.DataFrame): The reference dataframe.
            reference_column (str): The column in the reference dataframe to check against.

        Returns:
            bool: True if all values in the dataframe's column exist in the reference column.
        """
        if reference_column not in reference_df.columns:
            raise ValueError(f"Reference column '{reference_column}' not found in reference dataframe.")
        
        if self.column not in self.dataframe.columns:
            return False  # Column not found

        reference_values = set(reference_df[reference_column])
        column_values = set(self.dataframe[self.column])
        return column_values.issubset(reference_values)


def validate_multiple_dataframes(reference_df: pd.DataFrame, reference_column: str, target_dataframes: list[DataFrameValidator]):
    """
    Validates multiple dataframes against a reference dataframe using the DataFrameValidator class.

    Parameters:
        reference_df (pd.DataFrame): The dataframe containing the reference column.
        reference_column (str): The column in the reference dataframe to check against.
        dataframe_validators (list of DataFrameValidator): A list of DataFrameValidator objects.

    Returns:
        dict: A dictionary where keys are indices of the validators and values are True (valid) or False (invalid).
    """
    results = {}
    for idx, validator in enumerate(target_dataframes):
        results[idx] = validator.validate(reference_df, reference_column)
    return results

@dataclass
class SynapseValidator:
    """
    A class to manage Synapse IDs and their paired columns for validation
    using DataFrameValidator via composition.

    Attributes:
        synapse_data (List[Tuple[str, str]]): A list of tuples containing Synapse IDs and their corresponding column names.
        reference_df (pd.DataFrame): The reference dataframe.
        reference_column (str): The column in the reference dataframe for validation.
    """
    target_synapse_ids: list[tuple[str, str]]
    reference_synapse_id: str
    reference_column: str
    syn: synapseclient.Synapse

    def __post_init__(self):
        self.reference_df = self.read_synapse_file(synapse_id=self.reference_synapse_id, column=self.reference_column)

    def read_synapse_file(self, synapse_id: str, column: str = None) -> pd.DataFrame:
        """
        Downloads a file from Synapse using its Synapse ID and loads it as a dataframe.

        Parameters:
            synapse_id (str): The Synapse ID of the file to download.

        Returns:
            pd.DataFrame: A dataframe created from the downloaded file.
        """
        try:
            entity = self.syn.get(synapse_id)
        except Exception as e:
            raise RuntimeError(f"Failed to download Synapse ID {synapse_id}: {e}")
        return pd.read_csv(entity.path, usecols=[column])

    def validate(self) -> dict:
        """
        Validates all Synapse files against the reference dataframe.

        Returns:
            dict: A dictionary mapping Synapse IDs to their validation results (True/False).
        """
        results = {}
        for synapse_id, validate_column in self.target_synapse_ids:
            print(f"Validating Synapse ID: {synapse_id} on column: {validate_column} against reference: {self.reference_synapse_id} on column: {self.reference_column}")
            try:
                # Download and create DataFrameValidator
                df = self.read_synapse_file(synapse_id=synapse_id, column=validate_column)
                validator = DataFrameValidator(df, validate_column)

                # Perform validation
                is_valid = validator.validate(self.reference_df, self.reference_column)
                results[synapse_id] = is_valid
                JSONLOGGER.info('Valid' if is_valid else 'Invalid', extra={"extra": {"target_synapse_id": synapse_id, "target_column": validate_column, "reference_synapse_id": self.reference_synapse_id, "reference_column": self.reference_column, "is_valid": is_valid}})
            except Exception as e:
                JSONLOGGER.error(f"Error validating Synapse ID {synapse_id}: {e}", extra={"extra": {"target_synapse_id": synapse_id, "target_column": validate_column, "reference_synapse_id": self.reference_synapse_id, "reference_column": self.reference_column, "is_valid": is_valid}})
                results[synapse_id] = False
        return results


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

def main():
    syn = synapseclient.login()
    # Example list of Synapse ID and column name pairs
    synapse_data = [
        ('syn52955031', 'specimenID'),
        ('syn58849847', 'specimenID'),
    ]

    # Synapse ID of the reference file
    reference_synapse_id = 'syn62661392'

    # Initialize SynapseValidator
    validator = SynapseValidator(
        target_synapse_ids=synapse_data,
        reference_synapse_id=reference_synapse_id,
        reference_column='individualID',
        syn=syn
    )

    # Perform validation
    results = validator.validate()
    print("Validation Results:", results)
    validation_results_df = parse_json_logs_to_dataframe("validation_results.json")
    validation_results_df.to_csv("validation_results.csv", index=False)


if __name__ == '__main__':
    main()
