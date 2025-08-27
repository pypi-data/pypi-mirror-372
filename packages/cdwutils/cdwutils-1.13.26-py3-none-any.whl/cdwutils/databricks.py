import json
import logging
from typing import Any, Dict, List

from delta import DeltaTable
import IPython
from py4j.protocol import Py4JJavaError
from pyspark.sql import DataFrame, SparkSession, functions as F

from .misc import get_str_format_fields, OnlyOnceList, render_value_literal
from .exceptions import CircularReferenceError
from .spark_extensions import get_spark_setting_value, tmp_spark_setting

DATABRICKS_HOST_URL = "https://dbc-ab43a297-4b7e.cloud.databricks.com"


def get_dbutils():
    """Return dbutils module."""
    return IPython.get_ipython().user_ns["dbutils"]


def get_spark_session():
    """Returns active spark session"""
    return SparkSession.builder.getOrCreate()


def get_job_input(param_name, default_value=None, allow_defaults=True):
    """
    Fetch job input parameter or return provided default values

    The function takes in a string and the corresponding default value.
    If it fails to retrieve the parameter as a job input it will return the default value.

    Example:

        foo = get_job_input(param_name = 'bar', default_value = 'val')

    Parameters:
        param_name: String name of variable to fetch.

        default_value: String value to return if the parameter is not found.

        allow_defaults: Boolean value if the function should set default values
    Returns:
        Fetched or default value for input parameter
    """
    dbutils = get_dbutils()

    try:
        value = dbutils.widgets.get(param_name)
    except Py4JJavaError as error:
        if f"No input widget named {param_name} is defined" in str(error) and allow_defaults:
            value = default_value
        else:
            raise error

    return value


def get_job_inputs(param_dict: dict = None, *, allow_defaults: bool = True, **params: Any) -> dict:
    """
    Fetch job input parameters or return provided default values.

    The function takes in a dictionary of parameter names mapped to default values or
    String templates supported. You can refer to a value of another param e.g.
    >>> get_job_inputs(param1="some_value", param2="{param1}_2")
    {'param1': 'some_value', 'param2': 'some_value_2'}

    Parameters:
        param_dict: Dictionary of key-value pairs showing the parameter to fetch and the desired default value
        allow_defaults: Boolean value if the function should set default values
        params: same as param_dict but in **kwargs format
    Returns:
        dict: maps the param name to the value input value if passed into the job (or default otherwise)

    Examples:
    >>> get_job_inputs({"env": "dev", "db": "cdw_{env}_raw"})
    {'env': 'dev', 'db': 'cdw_dev_raw'}
    >>> get_job_inputs(env="dev", db="cdw_{env}_raw")
    {'env': 'dev', 'db': 'cdw_dev_raw'}
    >>> get_job_inputs(env="dev", db="cdw_{env}_raw", db_table="{db}.tbl")
    {'env': 'dev', 'db': 'cdw_dev_raw', 'db_table': 'cdw_dev_raw.tbl'}
    >>> get_job_inputs(env="dev", db="cdw_{env}_raw", db_table="{db}.tbl")
    {'env': 'dev', 'db': 'cdw_dev_raw', 'db_table': 'cdw_dev_raw.tbl'}
    >>> get_job_inputs(env="dev", db="cdw_{env}_raw", table="tbl", db_table="{db}.{table}")
    {'table': 'tbl', 'env': 'dev', 'db': 'cdw_dev_raw', 'db_table': 'cdw_dev_raw.tbl'}
    >>> get_job_inputs(num=1, num2="{num:0>10}")
    {'num': 1, 'num2': '0000000001'}
    """
    param_dict = params if param_dict is None else {**param_dict, **params}
    original_param_order = tuple(param_dict.keys())

    output_dict = {}
    next_items = OnlyOnceList()

    while len(param_dict) > 0:
        param, default_val = param_dict.popitem()

        if isinstance(default_val, str):
            fields = get_str_format_fields(default_val)

            if "" in fields:
                raise ValueError(f"You must use named formatting arguments: '{default_val}' ('{param}')")

            next_items.clear()
            for field in fields:
                if field not in output_dict.keys():
                    next_val = param_dict.pop(field)  # find the items this current one refers to
                    try:
                        next_items.append((field, next_val))
                    except ValueError:
                        raise CircularReferenceError(f"'{next_val}'")

            if next_items:
                next_items.insert(0, (param, default_val))  # put the original item back but before the next items
                for item in next_items:
                    param_dict.update(next_items)
                continue  # the next loop will process the item that the current one depends on
            else:
                default_val = default_val.format(**output_dict)

        output_dict[param] = get_job_input(param, default_val, allow_defaults)

    return {param_name: output_dict[param_name] for param_name in original_param_order}


def get_notebook_info():
    """
    Returns a JSON of all notebook/job info available
    :return: dict
    """
    dbutils = get_dbutils()

    return json.loads(dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())


def get_job_url():
    """
    Returns the databricks job URL as a string
    """
    notebook_info = get_notebook_info()

    return "{workspace_url}/#job/{job_id}/run/{run_id}".format(
        workspace_url=DATABRICKS_HOST_URL,
        job_id=notebook_info["tags"]["jobId"],
        run_id=notebook_info["tags"]["idInJob"]
    )


def get_notebook_url():
    """
    Returns the databricks notebook URL as a string
    """
    notebook_info = get_notebook_info()

    return "{workspace_url}/#notebook/{notebook_id}".format(
        workspace_url=notebook_info["tags"]["browserHostName"],
        notebook_id=notebook_info["tags"]["notebookId"]
    )


def get_environment_url():
    """
    Returns the databricks notebook or job URL as a string
    """

    url = None

    try:
        url = get_job_url()
    except KeyError as error:
        if 'jobId' in str(error):
            pass
        else:
            raise error

    if not url:
        url = get_notebook_url()

    return url


def get_notebook_path():
    """
    Returns the databricks notebook path as a string
    """
    notebook_info = get_notebook_info()
    return notebook_info["extraContext"]["notebook_path"],


def get_notebook_user():
    """
    Returns the databricks notebook user as a string
    """
    notebook_info = get_notebook_info()
    return notebook_info["tags"]["user"]


def get_notebook_user_id():
    """
    Returns the databricks notebook user as a string
    """
    notebook_info = get_notebook_info()
    return notebook_info["tags"]["userId"]


def get_cluster_id():
    """
    returns cluster id of job
    :return: str
    """

    return get_notebook_info()["tags"]["clusterId"]


def print_job_inputs(**job_inputs):
    """
    Prints job inputs dict to log
    :return: None
    """
    print(json.dumps(job_inputs, indent=4, default=str))


def table_exists(table_name: str, spark: SparkSession = None) -> bool:
    """
    Check if a table exists in the metastore catalog and return bool.
    """
    if spark is None:
        spark = get_spark_session()
    return spark._jsparkSession.catalog().tableExists(table_name)


class DeltaLakeWriter:
    """
    Example usage:
    >>> partitioning
    >>> DeltaLakeWriter(df, "cdw_dev_tmp.test").write()
    >>> DeltaLakeWriter(df, "cdw_dev_tmp.test").write(partition_by=["p_date"]).table_optimize(zorder_by=["ts"])
    >>> DeltaLakeWriter(df, "cdw_dev_tmp.test").write(partitions_filter=[{"p_date": {"between": ["2021-01-01", "2021-01-05"]}}])
    >>> clustering
    >>> DeltaLakeWriter(df, "cdw_dev_tmp.test").write_v2(cluster_by=["user_id", "event_type"])
    >>> DeltaLakeWriter(df, "cdw_dev_tmp.test").write_v2(cluster_by=["user_id"], overwrite=True, options={ "userMetadata": "Refresh user events", "delta.clustering.maxBlockRowCount": "67108864"})
    >>> delta_table = DeltaLakeWriter(df, "cdw_dev_tmp.test").write_v2(cluster_by=["user_id"], overwrite_where=[{"column": "date", "operator": "=", "value": "2024-03-20"}])
    """
    default_options = {
        "delta.checkpoint.writeStatsAsStruct": "true",
        "delta.checkpoint.writeStatsAsJson": "false",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "false",
        "delta.logRetentionDuration": "interval 90 days",
        "delta.deletedFileRetentionDuration": "interval 60 days",
    }

    def __init__(self, df: DataFrame, target_table_name: str):
        self.df = df
        self.spark = SparkSession.builder.getOrCreate()
        self.table_name = target_table_name
        self.checkpoint_version = None
        self._delta_table = None

    def __repr__(self) -> str:
        return f"DeltaLakeWriter(target_table_name='{self.table_name}', df={str(self.df)})"

    def write(
        self,
        partition_by: List[str] = None,
        partition_filter: List[dict] = None,
        version: int = 1,
        overwrite: bool = False,
        **options
    ) -> "DeltaLakeWriter":
        """
        options:
            'userMetadata': custom commit message that will be written to Delta history
            'delta.targetFileSize': target file size used for Delta optimization, in bytes or other units
            'delta.tuneFileSizesForRewrites': {'true', 'false'}
        """
        write_options = {**self.default_options, **options}

        if not self.table_exists():
            self.df.write.saveAsTable(
                self.table_name,
                format="delta",
                mode="errorifexists",
                partitionBy=partition_by,
                **write_options
            )
        elif overwrite:
            self.df.write.option("overwriteSchema", "true").saveAsTable(
                self.table_name,
                format="delta",
                mode="overwrite",
                partitionBy=partition_by,
                **write_options
            )
        else:
            self.checkpoint_version = self.current_table_version
            self._clean_up_partitions(version=version, partition_filter=partition_filter)
            try:
                self.df.write.insertInto(self.table_name, overwrite=False)  # this will use the delta settings set at table creation time
            except Exception as e:
                self._restore_checkpoint_version()
                raise e
        return self
    
    def write_v2(
        self,
        cluster_by: List[str] = None,
        overwrite_where: List[dict] = None,
        version: int = 1,
        overwrite: bool = False,
        **options
    ) -> "DeltaLakeWriter":
        """
        options:
            'userMetadata': custom commit message that will be written to Delta history
            'delta.targetFileSize': target file size used for Delta optimization, in bytes or other units
            'delta.tuneFileSizesForRewrites': {'true', 'false'}
            # Small tables (<1M rows)
            'delta.clustering.maxBlockRowCount': "1048576"  # 1M rows
            # Medium tables (1M-100M rows)
            'delta.clustering.maxBlockRowCount': "67108864"  # 64M rows
            # Large tables (>100M rows)
            'delta.clustering.maxBlockRowCount': "268435456"  # 256M rows
        """

        write_options = {**self.default_options, **options}
        
        if not self.table_exists():
            self.df.write.clusterBy(*cluster_by).saveAsTable(
                self.table_name,
                format="delta",
                mode="errorifexists",
                **write_options
            )
        elif overwrite:
            self.df.write.option("overwriteSchema", "true").clusterBy(*cluster_by).saveAsTable(
                self.table_name,
                format="delta",
                mode="overwrite",
                **write_options
            )
        else:
            self.checkpoint_version = self.current_table_version
            self._clean_up_partitions(version=version, partition_filter=overwrite_where)
            try:
                self.df.write.insertInto(self.table_name)  # this will use the delta settings set at table creation time
            except Exception as e:
                self._restore_checkpoint_version()
                raise e
        return self

    @property
    def delta_table(self):
        if self._delta_table is None:
            if self.table_exists():
                self._delta_table = DeltaTable.forName(self.spark, self.table_name)
            else:
                raise Exception(f"Can't create DeltaTable for table {self.table_name}. Table doesn't exist.")
        return self._delta_table

    def _clean_up_partitions(self, version=1, **kwargs):
        if version == 1:
            self._merge_delete_with_pruning(**kwargs)
        if version == 2:
            self._delete_partitions(**kwargs)
        else:
            ValueError(f"Invalid version {version}. Must be in {1, 2}")

    @staticmethod
    def _render_partition_filter(partition_filter: List[Dict], alias: str = None) -> str:
        """
        partition_filter is a list of dicts that map the names of partiton columns to the values.
        Values can represented a dict which supports keys "value", "type", and "between". If type
        is not specified, defaults to string.

        partition_filter examples:
        >>> [
        ...    {"p_date": "2021-01-01"},
        ... ]
        >>> [
        ...    {"p_date": {"value": "2021-01-01"}},
        ... ]
        >>> [
        ...    {"p_date": {"value": "2021-01-01", "type": "string"}},
        ... ]
        >>> [
        ...    {"p_date": {"between": ["2021-01-01", "2021-01-31"], "type": "string"}},
        ... ]
        >>> [
        ...    {"p_date": {"value": "2021-01-01", "type": "date"}, "p_client": "finn"},
        ...    {"p_date": {"value": "2021-01-01", "type": "date"}, "p_client": "vg"},
        ... ]
        """
        alias = f"{alias}." if alias is not None else ""

        rendered_filter_parts = []
        for pval in partition_filter:

            column_conditions = []
            for p_col_name, value_spec in pval.items():
                if isinstance(value_spec, dict):
                    data_type = value_spec.get("type", "string")
                    if "between" in value_spec:
                        val_from = render_value_literal(value_spec["between"][0], data_type)
                        val_to = render_value_literal(value_spec["between"][-1], data_type)
                        column_conditions.append(
                            f"{alias}`{p_col_name}` BETWEEN {val_from} AND {val_to}"
                        )
                    elif "value" in value_spec:
                        val = render_value_literal(value_spec["value"], data_type)
                        column_conditions.append(
                            f"{alias}`{p_col_name}` = {val}"
                        )
                else:
                    column_conditions.append(
                        f"{alias}`{p_col_name}` = {render_value_literal(value_spec)}"
                    )
            rendered_filter_parts.append(
                "({})".format(" AND ".join(column_conditions))
            )
        return "({})".format(" OR ".join(rendered_filter_parts))

    def _merge_delete_with_pruning(self, **kwargs):
        """
        Delete partitions in the target Delta table using Delta merge with a delete when matched condition.

        kwargs:
            partition_filter
        """
        partition_cols = self._get_table_partition_cols()

        delta_table_alias = "delta_table"
        updates_df_alias = "updates"

        partition_filter = kwargs.get("partition_filter", [])
        partition_filter_condition = self._render_partition_filter(
            partition_filter, alias=delta_table_alias
        )
        match_condition = " AND ".join(
            [f"{delta_table_alias}.`{c}` = {updates_df_alias}.`{c}`" for c in partition_cols]
        )
        condition = f"{partition_filter_condition} AND ({match_condition})"
        logging.info(condition)
        self.delta_table.alias(delta_table_alias).merge(
            source=self.df.alias(updates_df_alias),
            condition=condition
        ).whenMatchedDelete().execute()

    def _delete_matching_partitions(self, **kwargs) -> None:
        """
        Delete partitions in the target Delta table using a delete command
        Selects distinct partition column values from the source dataset and runs a delete command
        on the target Delta table.
        """
        partition_cols = self._get_table_partition_cols()
        rows = self.df.select(*partition_cols).distinct().collect()
        partition_vals = [r.asDict() for r in rows]
        self._delete_partitions(partition_vals)

    def _delete_partitions(self, partition_filter: List[Dict]) -> None:
        """
        Runs a delete
        partition_filter example
        [
            {"p_date": "2021-01-01", "p_client": "vg"},
            {"p_date": "2021-01-01", "p_client": "finn"},
            {"p_date": "2021-01-02", "p_client": "vg"},
            {"p_date": "2021-01-02", "p_client": "finn"},
        ]
        """
        delete_filter = self._render_partition_filter(partition_filter)
        self.delta_table.delete(delete_filter)

    def _get_table_detail(self) -> dict:
        q = f"DESCRIBE DETAIL {self.table_name}"
        return self.spark.sql(q).collect()[0].asDict()

    def _get_table_partition_cols(self) -> List[str]:
        return self._get_table_detail().get("partitionColumns", [])

    def _get_table_partition_cols_type_dict(self) -> Dict[str, str]:
        """
        Return a dict of partition column name -> column type name.
        """
        rows = self.spark.sql(
            f"DESCRIBE TABLE {self.table_name}"
        ).select(
            "col_name", "data_type"
        ).filter(
            F.col("col_name").isin(self._get_table_partition_cols())
        ).collect()
        return {r["col_name"]: r["data_type"] for r in rows}

    def table_exists(self) -> bool:
        return table_exists(table_name=self.table_name, spark=self.spark)

    @property
    def current_table_version(self) -> int:
        return self.delta_table.history().select(
            F.max("version").alias("version")
        ).collect()[0]["version"]

    def _restore_checkpoint_version(self) -> None:
        if self.checkpoint_version is None:
            raise Exception("Cannot restore checkpoint version of the table. Checkpoint version is unavailable.")

        if self.current_table_version > self.checkpoint_version:
            self.delta_table.restoreToVersion(self.checkpoint_version)

    def delete(self, skip_if_not_exists: bool = True) -> None:
        """
        Delete the target Delta table.

        Built in-line with:
        https://kb.databricks.com/delta/drop-delta-table.html
        """
        if self.table_exists():
            self.delta_table.delete()
            self.table_vacuum(retention_hours=0)
            self.spark.sql(f"DROP TABLE {self.table_name}")
        elif not skip_if_not_exists:
            raise Exception(f"Can't delete table {self.table_name}. Table doesn't exist.")

    def table_vacuum(self, retention_hours: int = None) -> None:
        """
        Perform VACUUM operation on the Delta table.
        https://docs.delta.io/latest/delta-utility.html#remove-files-no-longer-referenced-by-a-delta-table
        """
        with tmp_spark_setting(self.spark, "spark.databricks.delta.vacuum.parallelDelete.enabled", "true"):
            if retention_hours is not None:
                with tmp_spark_setting(self.spark, "spark.databricks.delta.retentionDurationCheck.enabled", "false"):
                    self.delta_table.vacuum(retention_hours)
            else:
                self.delta_table.vacuum()

    def table_optimize(
        self,
        partition_filter: List[dict] = None,
        zorder_by: List[str] = None,
        target_file_size: str = None
    ):
        """
        Perform OPTIMIZE command. If zorder_by is not provided run compaction (bin-packing),
        otherwise run Z-Ordering.

        target_file_size: str
            in bytes or other unites (e.g. '256MB', '1GB')
        """
        if target_file_size is not None:
            self.table_set_property("delta.targetFileSize", target_file_size)

        if partition_filter is not None:
            where_clause = "WHERE {}".format(self._render_partition_filter(partition_filter))
        else:
            where_clause = ""

        if zorder_by is not None:
            zorder_clause = "ZORDER BY ({})".format(", ".join(zorder_by))
        else:
            zorder_clause = ""

        q = f"OPTIMIZE {self.table_name} {where_clause} {zorder_clause}"
        self.spark.sql(q)

    def table_set_property(self, name, value):
        self.spark.sql(f"ALTER TABLE {self.table_name} SET TBLPROPERTIES('{name}'='{value}')")

