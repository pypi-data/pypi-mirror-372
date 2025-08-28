"""IngestionSession management for DataForge SDK.

This module provides the IngestionSession class
that manages custom data ingestion process, including initialization, data writing,
metadata updates, and failure handling.

Classes:
    IngestionSession: Manages the custom ingestion process lifecycle.
"""
import json
from datetime import datetime
from typing import Optional, Callable
from pyspark.sql import DataFrame
from .process_record import ProcessRecord
from ._session import _Session


class IngestionSession(_Session):

    """Session class to manage custom ingestion process lifecycle.

    Initializes an ingestion process record and provides methods to ingest
    data frames and handle failures, updating metadata and notifying the Core API.
    """
    def __init__(self, source_name: Optional[str] = None, project_name: Optional[str] = None):
        """Initialize ingestion session and start a new ingestion process.

        Args:
            source_name (Optional[str]): Optional name of the data source being ingested.
                Used for interactive testing. Leave blank for production use.
            project_name (Optional[str]): Optional project context name. Used for interactive testing.
                Leave blank for production use.
        """
        super().__init__()
        # initialize process
        self.process_parameters["start_process_flag"] = True
        if source_name is not None:
            self.process_parameters["source_name"] = source_name
        if project_name is not None:
            self.process_parameters["project_name"] = project_name

        process = self._pg.sql("select sparky.sdk_new_ingestion(%s)", (json.dumps(self.process_parameters),))
        self.process = ProcessRecord(process)


    def latest_tracking_fields(self):
        """Get the latest tracking fields from the ingestion process record.

        Returns:
            dict: The latest tracking data from the process record, or None if not available.
        """
        return self.process.process.get("tracking")

    def ingest(self,df: DataFrame | Callable[[], DataFrame] | None = None):
        """Ingest the provided DataFrame into the DataForge and update input record.

        Writes the DataFrame to raw Parquet file,
        updates the input record with status, file size, record count, and notifies
        the Core API of process completion. On failure, updates logs and flags the input and process
        records as failed.

        Args:
            df (Callable[[], DataFrame] | DataFrame): parameterless def that you defined, returning the Spark DataFrame to ingest (recommended),
                or spark DataFrame
        """
        try:
            if not self._is_open:
                raise Exception("Session is closed")
            if df is None:
                status = "Z"
                row_count = 0
                file_size = 0
            else:
                if callable(df):
                    result_df = df()  # call it to get the DataFrame
                else:
                    result_df = df
                dest_file_path = f"{self._systemConfiguration.datalakePath}/source_{self.process.sourceId}/parsed/parsed_input_{self.process.inputId}"
                file_size, row_count = self._write_parsed_data(result_df, dest_file_path)
                status = "P" if row_count > 0 else "Z"
            input_update_json = {
                "ingestion_status_code": status,
                "extract_datetime": datetime.now().isoformat(),
                "file_size": file_size,
                "process_id": self.process.processId,
                "input_id": self.process.inputId,
                "record_counts": {"Total": row_count}
            }

            self._pg.sql("SELECT meta.prc_iw_in_update_input_record(%s)",
                         (json.dumps(input_update_json),), fetch=False)
            self.logger.info("Ingestion completed successfully")

        except Exception as e:
            self._log_fail(e)
            failure_update_json = {
                "process_id": self.process.processId,
                "ingestion_status_code": "F"
            }
            self._pg.sql("SELECT meta.prc_iw_in_update_input_record(%s)",
                         (json.dumps(failure_update_json),), fetch=False)
        finally:
            self._core_api_call(f"process-complete/{self.process.processId}")
            self.close()


    def fail(self, message: str):
        """Mark the ingestion as failed with a custom message.

        Logs the provided error message, updates the input and process record to failure status,
        and notifies the Core API of process completion.

        Args:
            message (str): Custom error message explaining the failure.
        """
        self.log(f"Custom Ingestion failed with error: {message}", "E")
        self._pg.sql("select meta.prc_iw_in_update_input_record(%s)",
                     [json.dumps({"process_id": self.process.processId, "ingestion_status_code" : "F"})], fetch=False)
        self._core_api_call(f"process-complete/{self.process.processId}")