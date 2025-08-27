from .postgres_connection import PostgresConnection


class SystemConfiguration:
    datalakePath: str
    databricksDbName: str
    targetParquetFileSize: int
    # etlURI: str
    architecture:str
    coreUri: str
    saas_flag: bool

    def __init__(self, pg: PostgresConnection):
        conf = pg.sql("SELECT meta.prc_get_system_configuration('sparky')")
        self.datalakePath = conf['data-lake-path'].replace("s3://", "s3a://")
        self.databricksDbName = conf['databricks-db-name']
        self.targetParquetFileSize = conf['target-parquet-file-size']
        # self.etlURL = conf['etl-url']
        self.architecture = conf['architecture']
        self.saas_flag = self.architecture == "saas"
        self.coreUri = f"https://{conf['api-url']}" if self.saas_flag else f"http://{conf['etl-url']}:7131"

