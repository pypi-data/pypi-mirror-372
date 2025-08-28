"""Session management for DataForge SDK.

This module provides the Session class for managing DataForge SDK sessions,

Classes:
    CoreAPIError: Raised when a Core API call fails.
    VersionMismatchError: Raised when the SDK version does not match server expectation.
    Session: Main class for session management.
"""
import json
import re
import traceback
from typing import Optional, Literal
from pyspark.sql import SparkSession, DataFrame
import requests
import logging
from pyspark.dbutils import DBUtils
from pyspark.sql.functions import monotonically_increasing_id, lit
from pyspark.sql.types import LongType

from dataforge.process_record import ProcessRecord
from dataforge.system_configuration import SystemConfiguration
from dataforge.postgres_connection import PostgresConnection
from importlib.metadata import version

from .utils import _setup_logger


class CoreAPIError(Exception):
    """Exception raised when a Core API call fails."""
    pass

class VersionMismatchError(Exception):
    """Exception raised when the SDK version does not match server expectation."""
    pass

class _Session:
    """Base session class for DataForge SDK operations.
    Class should not be instantiated by user directly: use process-specific Session classes instead
    Manages Spark session, DBUtils, system configuration, Core API calls,
    logging, and process lifecycle.

    Attributes:
        spark (SparkSession): Spark session for data processing.
        dbutils (DBUtils): Databricks DBUtils instance.
        logger (logging.Logger): Logger instance for session logs.
        _systemConfiguration (SystemConfiguration): System configuration loaded from Postgres.
        _pg (PostgresConnection): Postgres connection to core API database.
        process (ProcessRecord): The current process record.
        version (str): DataForge SDK version.
    """
    _systemConfiguration: SystemConfiguration
    _pg: PostgresConnection
    spark: SparkSession
    dbutils: DBUtils
    logger: logging.Logger
    process: ProcessRecord
    version = version("dataforge-sdk")
    process_parameters: dict
    _is_open: bool = False

    def __init__(self):
        self.logger = _setup_logger(self.__class__.__name__)
        self.spark = SparkSession.builder.getOrCreate()
        self.dbutils = self._get_dbutils()
        pg_connection_string_read = self.dbutils.secrets.get("sparky", "pg_read")
        pg_read = PostgresConnection(f"{pg_connection_string_read}&application_name=sdk", self.logger)
        self._systemConfiguration = SystemConfiguration(pg_read)
        pg_connection_string: str = self._core_api_call("core/sparky-db-connection")["connection"]
        self._pg = PostgresConnection(f"{pg_connection_string}&application_name=sdk", self.logger)
        self._is_open = True
        self._check_version()
        self.process_parameters = {
            "version": self.version,
            "packageName": "dataforge-sdk"
        }
        try:
            self.process_parameters['process_id'] = int(self.dbutils.widgets.get("process_id"))
        except Exception as e:
            pass
        self.logger.info(f"Initialized base session for {self.__class__.__name__}")


    def _get_dbutils(self):
        return DBUtils(self.spark)

    def _core_api_call(self, route: str):
        """Make a GET request to the Core API.

        Args:
            route (str): API route to call, appended to core URI.

        Returns:
            dict: Parsed JSON response from Core API.

        Raises:
            CoreAPIError: If response status is not 200.
        """
        add_core =  "core/" if route.startswith("process-complete") and self._systemConfiguration.saas_flag else ""
        end_point = f"{self._systemConfiguration.coreUri}/{add_core}{route}"
        core_jwt_token = self.dbutils.secrets.get("sparky", "coreJWT")
        headers = {
            "Authorization": f"Bearer {core_jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.logger.debug(f"Executing core API call to {end_point}")
        response = requests.get(end_point, headers=headers)
        if response.status_code == 200:
            data = response.json() if response.content else None
            return data
        else:
            raise CoreAPIError(f"Core API call to {end_point} failed with status code {response.status_code}")

    def _check_version(self):
        """Checks that the SDK version is compatible with the server.

        Calls the database function to verify the SDK version. Raises
        VersionMismatchError if there is a version mismatch.
        """
        self.logger.info(f"Executing package dataforge-sdk version {self.version}")
        check_res = self._pg.sql("select sparky.sdk_check_version(%s,%s)", [self.version, "dataforge-sdk"])
        if check_res.get("error"):
            raise VersionMismatchError(check_res.get("error"))

    def log(self, message:str, severity: str = "I"):
        """Log a message to both the local logger and the process log in the database.

        Args:
            message (str): The log message.
            severity (str): Severity level, "I" for info, "E" for error. Defaults to "I".
        """
        match severity:
            case "I":
                self.logger.info(message)
            case "E":
                self.logger.error(message)
        payload = {"log_id": self.process.logId, "operation_type": self.process.operationType,
         "severity": severity, "message": message}
        self._pg.sql("SELECT sparky.write_log(%s)", [json.dumps(payload)], fetch=False)

    def connection_parameters(self):
        """Retrieve connection parameters for the current process.

        Returns:
            dict: Dictionary containing private and public connection parameters.
        """
        connection_id = self.process.connectionId
        self.log(f"Reading connection parameters of connection id {connection_id}")
        params = self._core_api_call(f"core/connection/{connection_id}").get("parameters")
        return {"private_connection_parameters": params.get("private_connection_parameters"),
          "public_connection_parameters": params.get("public_connection_parameters")}


    def _end_process(self, status_code: Literal['P', 'F', 'Z'] = 'P', parameters: Optional[dict] = None):
        """Private method. End the current process
        """
        payload = parameters if parameters else {}
        payload["process_id"] = self.process.processId
        payload["status_code"] = status_code
        self._pg.sql("select meta.prc_process_end(%s)", [json.dumps(payload)], fetch=False)
        self._core_api_call(f"process-complete/{self.process.processId}")
        if status_code in ('P','Z'):
            self.logger.info("Session completed successfully")
        else:
            self.logger.error("Process failed")
        self.close()

    def fail(self,message: str):
        """Fail current session and log the message.

        Args:
            message (str): The log message.
        """
        self.log(f"Process failed with error: {message}", "E")
        self._end_process("F")

    def _log_fail(self, e: Exception):
        """Log failure for the given exception.

        Args:
            e (Exception): The exception that caused the failure.
        """
        traceback.print_exception(e)
        self.log(f"Process failed with error: {e}", "E")

    def close(self):
        """Close the session."""
        self._pg.close()
        self.logger.info("Session closed")
        self._is_open = False

    def custom_parameters(self):
        """Retrieve custom parameters from the process.

        Returns:
            dict: The custom parameters dictionary from the process.
        """
        return self.process.parameters.get('custom_parameters')

    def _write_parsed_data(self, in_df: DataFrame, dest_file_path: str) -> tuple[int, int]:
        """Process input DataFrame, write to Parquet, and update metadata.

        Args:
            in_df (DataFrame): Input Spark DataFrame to process and write.
            dest_file_path (str): Destination path for saving Parquet file.

        Returns:
            tuple[int, int]: A tuple containing the total file size in bytes and the number of records written.

        Raises:
            Exception: If duplicate columns are detected or metadata update fails.
        """
        self.log("Data read successfully. Checking schema.")

        select_list = self._pg.sql("SELECT sparky.get_select_list(%s)", (self.process.sourceId,))
        df_sel = in_df.selectExpr(*select_list)
        self.log(f"Applied select list {select_list}")

        # Duplicate column check
        cols = df_sel.columns
        dup_columns = [col for col in set(cols) if cols.count(col) > 1]
        if dup_columns:
            raise Exception(f"Duplicate columns detected: {', '.join(dup_columns)}")

        # Cast binary/void to string
        binary_casts = [
            f"CAST(`{f.name}` AS STRING) `{f.name}`" if f.dataType.typeName() in ("binary", "void")
            else f"`{f.name}`"
            for f in df_sel.schema.fields
        ]
        df = df_sel.selectExpr(*binary_casts)

        # Schema as JSON array
        schema = []
        for f in df.schema.fields:
            field_name = f.name.lower() if self.process.forceCaseInsensitive else f.name
            name_normalized =  re.sub(r'\W+', '_', field_name)
            column_normalized = ("_" if field_name[0].isdigit() else "") + name_normalized # add leading underscore

            if f.dataType.simpleString().startswith("struct"):
                spark_type = "StructType"
            elif f.dataType.simpleString().startswith("array"):
                spark_type = "ArrayType"
            elif f.dataType.simpleString().startswith("decimal"):
                spark_type = "DecimalType"
            else:
                spark_type = type(f.dataType).__name__

            attr_schema = json.loads(f.dataType.json())
            self.logger.info(f"Column `{column_normalized}` schema: {attr_schema}")
            schema.append({
                "name": field_name,
                "column_normalized": column_normalized,
                "spark_type": spark_type,
                "schema": attr_schema
            })

        self.log("Schema read successfully. Updating source raw metadata.")

        metadata_update_json = {
            "source_id": self.process.sourceId,
            "input_id": self.process.inputId,
            "raw_attributes": schema,
            "ingestion_type": "sparky"
        }

        result = self._pg.sql("SELECT meta.prc_n_normalize_raw_attribute(%s)", [json.dumps(metadata_update_json)])
        if "error" in result:
            raise Exception(result["error"])

        normalize_attributes = result["normalized_metadata"]

        self.log("Source metadata updated. Renaming and upcasting attributes")

        cast_rename_expr = []
        for att in normalize_attributes:
            base_expr = att.get("upcastExpr") or att["raw_attribute_name"]
            if att["raw_attribute_name"] != att["column_alias"] or self.process.forceCaseInsensitive:
                base_expr += f" AS {att['column_alias']}"
            cast_rename_expr.append(base_expr)

        self.logger.info("Normalized SQL: " + ", ".join(cast_rename_expr))
        df_update = df.selectExpr(*cast_rename_expr)

        if self.process.parameters.get("generate_row_id", False):
            self.logger.info("Added s_row_id to data.")
            df_final = df_update.withColumn("s_row_id", monotonically_increasing_id())
        else:
            self.logger.info("generate_row_id = false, added null s_row_id.")
            df_final = df_update.withColumn("s_row_id", lit(None).cast(LongType()))

        self.log("Writing file")
        df_final.write.format("parquet").mode("overwrite").save(dest_file_path)
        self.log(f"Wrote file {dest_file_path}")

        row_count = self.spark.read.format("parquet").load(dest_file_path).count()
        self.log(f"{row_count} records counted")

        file_size = sum(f.size for f in self.dbutils.fs.ls(dest_file_path))
        return file_size, row_count

