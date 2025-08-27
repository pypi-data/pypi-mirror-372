import datetime as dt
import json
from typing import Tuple

import pyspark.sql.column
from pyspark.sql import functions as F
from pyspark.sql import SparkSession, DataFrame
from .databricks import get_cluster_id, get_environment_url, get_notebook_user, get_notebook_path, get_notebook_user_id
from . import snowflake


def add_key_column(
    df: DataFrame,
    key_name: str,
    key_columns: list,
    output_int64: bool = False,
    replace_nulls_with: str = ""
) -> DataFrame:
    """
    Return a DataFrame with new column called `key_name` created by hashing `key_columns`.
    If a key is all nulls the hash value will default to -1

    Parameters:
    df (pyspark.sql.DataFrame): This is the dataframe to which you want to add a key column.
    key_name (String): This is the name you want to give the key column
    key_columns (List[String]): This is the list of columns to make the key from
    output_int64 (bool): output an int64 key value instead of the default string.
     Note: uses xxhash64 if True, md5 otherwise.
    replace_nulls_with (str): string to replace nulls with, defaults to an empty string.
    """

    key_array = ['visit_key', 'visitor_key', 'session_key']
    df = df.withColumn("vvs_keys", F.lit(False))

    if key_name in key_array:
        df = df.withColumn("vvs_keys", (sum(F.col(col).isNull().cast("int") for col in key_columns) > 0))

    key_columns_coalesced = (F.coalesce(F.col(col_name), F.lit(replace_nulls_with)) for col_name in key_columns)
    hash_input = F.concat_ws("|", *key_columns_coalesced)

    if output_int64:
        hashed_key = F.xxhash64(hash_input)
    else:
        hashed_key = F.md5(hash_input)

    all_null_key_value = -1 if output_int64 else "-1"

    return df.withColumn(
        "all_null_key",
        (sum(F.col(col).isNull().cast("int") for col in key_columns) == len(key_columns))
    ).select(
        F.when(
            F.col("all_null_key") == True,
            all_null_key_value
        ).when(
            F.col("vvs_keys") == True,
            all_null_key_value
        ).otherwise(
            hashed_key
        ).alias(key_name),
        "*"
    ).drop(
        "all_null_key",
        "vvs_keys"
    )


def remove_already_loaded(
    df: DataFrame,
    comparison_table_name: str,
    key_name: str,
    comparison_key_name: str = None,
) -> DataFrame:
    """
    Static method removing all rows from a dataframe present in a table

    This method removes all rows in a dataframe which are present in
    another table. The method uses the column key_name as a row identifier
    in both tables. If the other table isn't present it is treated as empty.
    Loosely: df = df EXCEPT comparison table

    Parameters:
    df (pyspark.sql.DataFrame): This is the dataframe from which you want to remove rows
    comparison_table (String): Name of spark table containing the rows we do not want to process again
    key_name (String): This is the name of the column providing a unique row identifier

    Returns:
    pyspark.sql.DataFrame: Returns a new dataframe without rows present in the comparison table

    """
    if not comparison_key_name:
        comparison_key_name = key_name

    spark = SparkSession.builder.getOrCreate()
    if spark._jsparkSession.catalog().tableExists(comparison_table_name):
        already_calculated = spark.table(comparison_table_name).select(key_name)
        df = df.join(
            already_calculated,
            df[key_name] == already_calculated[comparison_key_name],
            how='left_anti'
        )
    return df


def add_etl_metadata_columns(df: DataFrame) -> DataFrame:
    """
    Static method adding some ETL columns

    This method adds two columns to a dataframe:
    1. 'ETL_CREATED_DATE' - telling us when the data was processed by Databricks
    2. 'ETL_JOB_DETAILS' - telling us the job url, cluster id, user, userid, and notebook path

    Parameters:
    df (pyspark.sql.DataFrame): This is the dataframe to which we want to add the rows

    Returns:
    pyspark.sql.DataFrame: Returns a new dataframe with the ETL columns
    """

    job_details = json.dumps(
        {
            "url": get_environment_url(),
            "cluster_id": get_cluster_id(),
            "notebook_path": get_notebook_path(),
            "user_id": get_notebook_user_id(),
            "user": get_notebook_user()
        }
    )

    return df.withColumn(
        "ETL_CREATED_DATE", F.lit(dt.datetime.now())
    ).withColumn(
        "ETL_JOB_DETAILS", F.lit(job_details)
    )


# TODO: explore comparing table values (hashes maybe?)
# create a df of SF table and S3 table: key, hash of all other columns
# try to joining and see if you have rows that don't match
def snowflake_in_sync(
    spark_target_table_name: str,
    snowflake_table: snowflake.SnowflakeTable,
    spark: SparkSession
) -> bool:
    """
    Static method to check if two tables have the same number of rows

    This method tests if tables have the same number of rows


    Parameters:
    spark_target_table (String): Name of spark table of dimension
    snowflake_table (String): Name of table in Snowflake
    spark (sparkSession): For checking if spark table exists
    snowflake (SnowflakeConnection): For querying snowflake

    Returns true if both tables have the same number of rows
    """

    # Only count rows if table exists
    if spark._jsparkSession.catalog().tableExists(spark_target_table_name):
        rows_in_spark = spark.table(spark_target_table_name).count()
    else:
        rows_in_spark = 0

    # Only count rows if table exists
    if snowflake_table.exists():
        rows_in_snowflake = snowflake_table.get_info()["ROW_COUNT"]
    else:
        rows_in_snowflake = 0

    return rows_in_snowflake == rows_in_spark


# TODO: improve in the future, allows for better file management
# Split write to S3 and update Snowflake
def save_delta_loaded_data(
    spark_target_table_name: str,
    snowflake_table: snowflake.SnowflakeTable,
    delta_load_data: DataFrame
) -> None:
    """
    This method tests if tables exists, then it counts the rows
    if they're not equal, spark table is used to overwrite the Snowflake one.


    Parameters:
    spark_target_table (String): Name of spark table of dimension
    snowflake_table (String): Name of table in Snowflake
    delta_load_data (pyspark.sql.DataFrame): The delta loaded data
    snowflake (SnowflakeConnection): To perform queries

    Returns None
    """
    spark = SparkSession.builder.getOrCreate()

    in_sync = snowflake_in_sync(spark_target_table_name, snowflake_table, spark)

    # Write the new data to the pyspark table
    delta_load_data.write.format("parquet").saveAsTable(spark_target_table_name, mode='append')

    # If the number of rows are different we overwrite the snowflake table with the python one
    if in_sync:
        snowflake_table.snowflake_connection.insert(
            delta_load_data,
            snowflake_table.qualified_name
        )
    else:
        snowflake_table.snowflake_connection.insert(
            spark.table(spark_target_table_name),
            snowflake_table.qualified_name,
            mode='overwrite'
        )


def split_datetime_column(col_name: str, validate_col_name=True) -> Tuple[pyspark.sql.column.Column, ...]:
    """
    Standard way of processing datetime columns in CDW.
    The column is split into 3 new columns:
    - A date column
    - A time column
    - A time column truncated down to minute
    """

    if validate_col_name and col_name[-9:] != "_datetime":
        raise ValueError("The column name must end with `_datetime`")

    base_col_name = col_name[:-9]

    col = F.col(col_name).cast("Timestamp")

    return (
        F.date_format(col, "yyyy-MM-dd").alias(f"{base_col_name}_date"),
        F.date_format(col, "HH:mm:ss.SSSSSSS").alias(f"precise_{base_col_name}_time"),
        F.date_format(F.date_trunc("minute", col), "HH:mm:ss").alias(f"{base_col_name}_time"),
    )


# Retrieves the column names from the DataFrame schema.
def get_column_names(df):
    column_list = ", ".join([f"{field.name}" for field in df.schema])
    return column_list


# Generates the schema for creating a Delta table with an identity column.
def generate_identity_schema(df, identityColName="rowId", offset=0, increment=1):
    try:
        return ",".join(
            map(
                str,
                [
                    f"{identityColName} bigint generated always AS identity \
                    (start with {offset} increment by {increment})"
                ]
                + [obj[0] + " " + obj[1] for obj in df.dtypes],
            )
        )
    except:
        return None


# Generates a DDL statement for creating a Delta table.
def generate_create_table(df, glue_target, glue_target_tbl):
    identityColumn = f"{glue_target_tbl}_sid"  # f"{glue_target_tbl}_sid" to be changed
    schema = generate_identity_schema(df, identityColumn)
    return f"""CREATE TABLE {glue_target} (
        {schema}
        ) USING DELTA"""


# Generates a DDL statement for insertion a Delta table.
def generate_insert_query(cols, values):
    return f"""INSERT ({cols}) VALUES ({values})"""


# Generates a DDL statement for update on a Delta table.
def generate_update_query(update_columns):
    return f"""UPDATE SET {update_columns}"""


def add_etl_date_column(df: DataFrame) -> DataFrame:
    """
    Static method adding some ETL columns

    This method adds one columns to a dataframe:
    1. 'ETL_CREATED_DATE' - telling us when the data was processed by Databricks

    Parameters:
    df (pyspark.sql.DataFrame): This is the dataframe to which we want to add the rows

    Returns:
    pyspark.sql.DataFrame: Returns a new dataframe with the ETL date
    """

    return df.withColumn(
        "ETL_CREATED_DATE", F.lit(dt.datetime.now())
    )
