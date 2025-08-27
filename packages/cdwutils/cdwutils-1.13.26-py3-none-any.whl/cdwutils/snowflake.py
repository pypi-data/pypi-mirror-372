import logging
import re
from typing import List, Optional

from boto3.session import Session
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from snowflake import connector as sfc

from .aws.secrets_manager import get_secret
from .misc import random_hex


class SnowflakeConnection:
    def __init__(
        self,
        credentials_name: str,
        database: str,
        schema: str,
        warehouse: str,
        role: str,
        spark: SparkSession,
        *,
        boto3_session: Optional[Session] = None
    ):
        self.secret_id = credentials_name
        self.database = database
        self.schema = schema
        self.warehouse = warehouse
        self.role = role
        self.spark = spark
        self.boto3_session = boto3_session
        self._credentials = None

    def _get_secret(self) -> dict:
        return get_secret(self.secret_id, session=self.boto3_session)

    @property
    def credentials(self) -> dict:
        if self._credentials is None:
            snowflake_creds = self._get_secret()
            self._credentials = {
              "sfUrl": snowflake_creds["url"],
              "sfUser": snowflake_creds["user"],
              "sfPassword": snowflake_creds["password"],
              "sfAccount": snowflake_creds["account"],
            }
        return self._credentials

    def _config_options(self) -> dict:
        options = dict(**self.credentials)
        options.update({
          "sfDatabase": self.database,
          "sfSchema": self.schema,
          "sfWarehouse": self.warehouse,
          "sfRole": self.role,
        })
        return options

    def load_table(self, name) -> DataFrame:
        """
        Load a table into the dataframe.
        Table name `name` can optionally include db/schema name.
        """
        options = self._config_options()
        return self.spark.read.format("snowflake").options(**options).option("dbtable", name).load()

    def load_query(self, sql) -> DataFrame:
        """
        Return a dataframe made from the sql query.
        """
        options = self._config_options()
        return self.spark.read.format("snowflake").options(**options).option("query", sql).load()

    def load(self, *, sql: Optional[str] = None, table_name: Optional[str] = None) -> DataFrame:
        """
        Return DataFrame loaded from either a `sql` query or from a table `table_name`.
        """
        if sql is not None and table_name is not None:
            raise ValueError("Too many arguments: must provide only `sql` or `table_name`, not both.")
        elif sql is not None:
            return self.load_query(sql)
        elif table_name is not None:
            return self.load_table(table_name)
        else:
            raise ValueError("Missing arguments: must provide either `sql` or `table_name`.")

    def insert(self, df: DataFrame, table_name: str, mode: str = "append") -> None:
        """
        Load the data of spark dataframe `df` into Snowflake table `table_name`.
        """
        options = self._config_options()
        df.write.format("snowflake").mode(mode).options(**options)\
          .option("dbtable", table_name).save()

    def insert_overwrite(
            self,
            df: DataFrame,
            table_name: str,
            overwrite_where: str,
            upsert: bool = False,
            key=None,
    ) -> None:
        """
        Insert data into a table and overwrite a subset of rows
        Assumes the table has a binary column called `soft_delete`
        """
        SnowflakeTable.from_qualified_name(table_name, self).insert_overwrite(
            df,
            overwrite_where,
            upsert=upsert,
            key=key
        )

    def run_query(self, sql: str) -> list:
        """
        Run DDL or DML query in Snowflake and return a list of resulting rows.
        To get a large result set back use `load_query` method instead.
        This method is useful for running DDL query and such.
        """
        sf_connection = sfc.connect(
            user=self.credentials["sfUser"],
            password=self.credentials["sfPassword"],
            account=self.credentials["sfAccount"],
            database=self.database,
            schema=self.schema,
            warehouse=self.warehouse,
            role=self.role,
            validate_default_parameters=True
        )
        return sf_connection.cursor().execute(sql).fetchall()

    def table(self, name: str, *, database: Optional[str] = None, schema: Optional[str] = None) -> "SnowflakeTable":
        """
        Return a SnowflakeTable.
        """
        database = database if database is not None else self.database
        schema = schema if schema is not None else self.schema
        return SnowflakeTable(database, schema, name, self)

    def table_exists(self, table: str, database: Optional[str] = None, schema: Optional[str] = None) -> bool:
        """
        Check if table exists in the specified schema.
        """

        database = database if database is not None else self.database
        schema = schema if schema is not None else self.schema

        query = f"""
            SHOW TABLES LIKE '{table}'
            IN SCHEMA {database}.{schema}
        """

        result = self.run_query(query)

        return len(result) > 0

    def view(self, name: str, *, database: Optional[str] = None, schema: Optional[str] = None) -> "SnowflakeView":
        """
        Return a SnowflakeView.
        """
        database = database if database is not None else self.database
        schema = schema if schema is not None else self.schema
        return SnowflakeView(database, schema, name, self)

    def materialized_view(self, name: str, *, database: Optional[str] = None, schema: Optional[str] = None) -> "SnowflakeMaterializedView":
        """
        Return a SnowflakeMaterializedView.
        """
        database = database if database is not None else self.database
        schema = schema if schema is not None else self.schema
        return SnowflakeMaterializedView(database, schema, name, self)


class ViewPrivileges:
    ALL = "ALL"
    SELECT = "SELECT"


class ViewQueryNotDefined(Exception):
    pass


class SnowflakeObject:
    """
    Base class for Snowflake objects.

    Parameters:
    -----------
    object_type: str
        'VIEW' or 'BASE TABLE'
    database: str
        Database where the view is located.
    schema: str
        Schema where the view is located.
    name: str
        Name of the view.
    snowflake_connection: SnowflakeConnection
        Connection to use for submitting Snowflake queries.
    comment: str
        Description of the view. Empty by default.
    quoted_identifiers: bool
        Whether to quote the view name. False be default.
    """

    def __init__(
        self,
        object_type: str,
        database: str,
        schema: str,
        name: str,
        snowflake_connection: SnowflakeConnection,
        *,
        comment: Optional[str] = None,
        quoted_identifiers: Optional[bool] = False
    ):
        self.object_type = object_type
        self.database = self.process_identifier(database, quoted_identifiers)
        self.schema = self.process_identifier(schema, quoted_identifiers)
        self.name = self.process_identifier(name, quoted_identifiers)
        self.view_query = None
        self.comment = "" if comment is None else comment
        self.snowflake_connection = snowflake_connection

    @staticmethod
    def process_identifier(identifier: str, quoted: bool, validate: Optional[bool] = True) -> str:
        """
        Return a cleaned identifier.
        Parameters:
        -----------
        identifier: str
            Snowflake object identifier (e.g. database name, schema name, view name)
        quoted: bool
            Whether to quote the identifier. False be default.
        validate: bool
            Check whether the identifier is valid. Raise ValueError if not valid.
        """
        if (idl := len(identifier)) > 255:
            raise ValueError(f"Identifier too long ({idl} characters): '{identifier}'")

        if validate and not quoted:
            validation_pat = re.compile(r"^[A-Za-z_]{1}[A-Za-z_0-9]*$")
            m = validation_pat.fullmatch(identifier)
            if m is None:
                raise ValueError(f"Invalid identifier: '{identifier}'")
            else:
                return identifier.upper()
        elif quoted:
            return f'"{identifier.upper()}"'

    @property
    def qualified_name(self) -> str:
        """Return a fully qualified name of the object."""
        return ".".join([self.database, self.schema, self.name])

    def get_info(self) -> Optional[dict]:
        """
        Return a dict of the information fields about the object (table/view) if it exists,
        None otherwise.
        """
        q = f"""
        SELECT *
          FROM {self.database}.INFORMATION_SCHEMA.TABLES
         WHERE UPPER(TABLE_CATALOG) = '{self.database}'
           AND UPPER(TABLE_SCHEMA) = '{self.schema}'
           AND UPPER(TABLE_NAME) = '{self.name}'
           AND UPPER(TABLE_TYPE) = '{self.object_type}'
        """
        info = self.snowflake_connection.load_query(q).collect()
        if len(info) == 1:
            return info[0].asDict()
        elif len(info) == 0:
            return None
        else:
            raise ValueError(f"Too many rows in the INFORMATION_SCHEMA for '{self.qualified_name}'")

    def exists(self) -> bool:
        """
        Class method to see if a snowflake table exists

        This method queries the information schema using the database,
        schema, object name and type from the instance variables.

        Parameters: None

        Returns:
        Boolean: If object exists it returns True
        """
        if self.get_info() is not None:
            return True
        else:
            return False

    def __bool__(self):
        return self.exists()

    def get_columns(self):
        """
        Return columns in object if it exists, otherwise None
        """
        if self.exists():
            q = f"""
                SELECT COLUMN_NAME
                  FROM {self.database}.INFORMATION_SCHEMA.COLUMNS
                 WHERE UPPER(TABLE_CATALOG) = '{self.database}'
                   AND UPPER(TABLE_SCHEMA) = '{self.schema}'
                   AND UPPER(TABLE_NAME) = '{self.name}'
                 ORDER BY ORDINAL_POSITION
            """
            columns = self.snowflake_connection.load_query(q).collect()
            if len(columns) > 0:
                return [r["COLUMN_NAME"] for r in columns]
        else:
            return None

    def grant(self, privileges: str, grantee: str):
        """
        Grant `privileges` on the view to `grantee`.
        """
        self.snowflake_connection.run_query(
            f"GRANT {privileges} ON {self.qualified_name} TO {grantee}"
        )
        return self

    def _delete(self, sf_object_type: Optional[str] = None):
        if sf_object_type is None:
            object_type = self.object_type
        else:
            object_type = sf_object_type

        self.snowflake_connection.run_query(
            f"DROP {object_type} IF EXISTS {self.qualified_name}"
        )
        return self


class SnowflakeView(SnowflakeObject):
    """
    Snowflake View.

    Parameters:
    -----------
    database: str
        Database where the view is located.
    schema: str
        Schema where the view is located.
    name: str
        Name of the view.
    snowflake_connection: SnowflakeConnection
        Connection to use for submitting Snowflake queries.
    comment: str
        Description of the view. Empty by default.
    quoted_identifiers: bool
        Whether to quote the view name. False be default.
    """

    def __init__(
        self,
        database: str,
        schema: str,
        name: str,
        snowflake_connection: SnowflakeConnection,
        *,
        comment: Optional[str] = None,
        quoted_identifiers: Optional[bool] = False
    ):
        super().__init__(
            object_type="VIEW",
            database=database,
            schema=schema,
            name=name,
            snowflake_connection=snowflake_connection,
            comment=comment,
            quoted_identifiers=quoted_identifiers
        )

    @classmethod
    def from_qualified_name(
            cls,
            qualified_name: str,
            snowflake_connection,
            *,
            comment: Optional[str] = None,
            quoted_identifiers: Optional[bool] = False
    ):
        database, schema, table = qualified_name.split(".")

        return cls(
            database=database,
            schema=schema,
            name=table,
            snowflake_connection=snowflake_connection,
            comment=comment,
            quoted_identifiers=quoted_identifiers
        )

    def from_table(
            self,
            qualified_name: str,
            where_condition: str = "",
            additional_select_expressions: Optional[List[str]] = None,
            except_columns: Optional[List[str]] = None,
            case_sensitive: bool = False,
            group_by: str = "",
    ):
        """
        Add a source query for the view equal to "SELECT * FROM `qualified_name`".
        If `except_columns` is provided, the query select all the base table columns except the ones listed.
        Note: The method will ignore any columns in `except_columns` that don't exist in the base table.

        :param qualified_name: Table name in format {databaseName}.{schemaName}.{tableName}
        :param where_condition: String to be added to the where clause in SQL format
        :param additional_select_expressions: Columns to be added to the view in SQL format.
        :param except_columns: List of table columns to exclude from the view. Use "*" to exclude all table columns
        :param case_sensitive: Flag to indicate if the column names are case sensitive
        :param group_by: String to be added to the group by clause in SQL format
        """

        if except_columns is None:
            view_cols = ["*"]
        elif except_columns == "*":
            view_cols = []
        else:
            table_database, table_schema, table_name = qualified_name.split(".")
            base_table = SnowflakeTable(table_database, table_schema, table_name, self.snowflake_connection)
            base_table_cols = base_table.get_columns()
            if not case_sensitive:
                base_table_cols = [col.upper() for col in base_table_cols]
                except_columns = [col.upper() for col in except_columns]

            view_cols = [base_col for base_col in base_table_cols if base_col not in except_columns]

        if additional_select_expressions is not None:
            view_cols.extend(additional_select_expressions)

        if where_condition:
            where_clause = f"WHERE {where_condition}"
        else:
            where_clause = ""

        if group_by:
            group_by_clause = f"GROUP BY {group_by}"
        else:
            group_by_clause = ""

        self.view_query = f"SELECT {', '.join(view_cols)} FROM {qualified_name} {where_clause} {group_by_clause}"

        return self

    def from_query(self, query: str):
        """
        Add a source query for the view equal to `query`.
        """
        self.view_query = query
        return self

    def create(self, replace: bool = False):
        """
        Create the view. By default does nothing if the view already exists.
        Parameters:
        -----------
        replace: bool
            Whether to replace the view if it already exists. False by default.
        """

        if replace:
            create_statement = f"CREATE OR REPLACE {self.object_type} {self.qualified_name}"
        else:
            create_statement = f"CREATE {self.object_type} IF NOT EXISTS {self.qualified_name}"

        if self.view_query is None:
            raise ViewQueryNotDefined

        full_query = f"{create_statement} COMMENT = '{self.comment}' AS {self.view_query}"

        results = self.snowflake_connection.run_query(full_query)

        return self

    def delete(self):
        return self._delete()


class SnowflakeTable(SnowflakeObject):
    """
    Snowflake Table.

    Parameters:
    -----------
    database: str
        Database where the view is located.
    schema: str
        Schema where the view is located.
    name: str
        Name of the view.
    snowflake_connection: SnowflakeConnection
        Connection to use for submitting Snowflake queries.
    comment: str
        Description of the table. Empty by default.
    quoted_identifiers: bool
        Whether to quote the table name. False be default.
    """

    def __init__(
        self,
        database: str,
        schema: str,
        name: str,
        snowflake_connection: SnowflakeConnection,
        *,
        table_type: Optional[str] = "BASE TABLE",
        comment: Optional[str] = None,
        quoted_identifiers: Optional[bool] = False
    ):
        super().__init__(
            object_type=table_type,
            database=database,
            schema=schema,
            name=name,
            snowflake_connection=snowflake_connection,
            comment=comment,
            quoted_identifiers=quoted_identifiers
        )

    @classmethod
    def from_qualified_name(
            cls,
            qualified_name: str,
            snowflake_connection,
            *,
            comment: Optional[str] = None,
            quoted_identifiers: Optional[bool] = False
    ):
        database, schema, table = qualified_name.split(".")

        return cls(
            database=database,
            schema=schema,
            name=table,
            snowflake_connection=snowflake_connection,
            comment=comment,
            quoted_identifiers=quoted_identifiers
        )

    def to_df(self) -> DataFrame:
        """
        Return pyspark.sql.DataFrame loaded from the Snowflake table.
        """
        return self.snowflake_connection.load_table(self.qualified_name)

    def insert_into(self, df: DataFrame, mode: str = "append") -> None:
        """
        Save data from the `df` into the Snowflake table with `mode`.
        """
        self.snowflake_connection.insert(df, self.qualified_name, mode)

    def create_from_df(self, df: DataFrame, insert_data: bool = True, replace: bool = False) -> "SnowflakeTable":
        """
        Create table based on the schema of the `df`. Optionally insert the `df` into the created table.
        By default the method won't overwrite the table if it already exists but can provide `replace` to override this.
        """
        fields = [
            f"{f.name} {rename_type(f.dataType.typeName())}" for f in df.schema.fields
        ]
        query = f"CREATE TABLE IF NOT EXISTS {self.qualified_name}"
        if replace:
            query = f"CREATE OR REPLACE TABLE {self.qualified_name}"

        query = f"{query} ({', '.join(fields)}) COMMENT = '{self.comment}'"

        results = self.snowflake_connection.run_query(query)

        if insert_data:
            self.insert_into(df)
        return self

    def delete(self):
        return self._delete("TABLE")

    @staticmethod
    def generate_tmp_table(base_table: "SnowflakeTable") -> "SnowflakeTable":
        table_exists = True

        while table_exists:
            tmp_table_name = f"TMP_{base_table.name}_{random_hex()}"
            tmp_table = SnowflakeTable(
                base_table.database,
                base_table.schema,
                tmp_table_name,
                base_table.snowflake_connection
            )

            table_exists = tmp_table.exists()

        return tmp_table

    def insert_overwrite(
            self,
            df: DataFrame,
            overwrite_where: str,
            upsert: bool = False,
            key=None,
    ) -> None:
        """
        Insert data into a table and overwrite a subset of rows
        If `upsert` is True, then the load is upserted on key
        If `upsert` is False, then the load is inserted into the target
        """

        if upsert and key is None:
            raise ValueError("A `key` has to be specified when `upsert` is True")

        if not self.exists():
            self.insert_into(df, "append")
        else:
            tmp_table = self.generate_tmp_table(self)

            delete_query = f"DELETE FROM {self.qualified_name} WHERE {overwrite_where};"

            delete_query_escaped = delete_query.replace("'", "\\'")

            get_query_id = f"""
                  SELECT QUERY_ID  
                    FROM table(INFORMATION_SCHEMA.QUERY_HISTORY_BY_USER())
                   WHERE QUERY_TEXT = '{delete_query_escaped}'
                ORDER BY START_TIME DESC
                   LIMIT 1
            """

            insert_query = f"""
                INSERT INTO {self.qualified_name}
                     SELECT * 
                       FROM {tmp_table.qualified_name}
            """

            query_id = ""
            try:
                tmp_table.insert_into(df)

                self.snowflake_connection.run_query(delete_query)
                query_id = self.snowflake_connection.run_query(get_query_id)[0][0]
                print(f"The Delete query query_id is {query_id}")

                if not upsert:
                    self.snowflake_connection.run_query(insert_query)
                else:
                    self._self_merge_on_key(tmp_table.qualified_name, key)

            except Exception as e:
                if query_id:
                    self.rollback(statement_id=query_id)
                raise e

            finally:
                drop_tmp_query = f"DROP TABLE IF EXISTS {tmp_table.qualified_name};"
                self.snowflake_connection.run_query(drop_tmp_query)

    def _self_merge_on_key(self, source_table, key):
        query_structure = """
        MERGE INTO {target_table} tgt USING {source_table} src
        ON {join_expr}
        WHEN MATCHED THEN 
            UPDATE SET {update_columns}
        WHEN NOT MATCHED THEN 
            INSERT ({insert_columns}) VALUES ({insert_values});
        """

        join_expr = f"tgt.{key} = src.{key}"

        table_columns = self.get_columns()

        update_columns = ", \n".join(f"{col} = src.{col}" for col in table_columns)

        insert_columns = ", \n".join(table_columns)

        insert_values = ", \n".join([f"src.{col}" for col in table_columns])

        query = query_structure.format(
            target_table=self.qualified_name,
            source_table=source_table,
            join_expr=join_expr,
            update_columns=update_columns,
            insert_columns=insert_columns,
            insert_values=insert_values,
        )

        logging.info(query)

        self.snowflake_connection.run_query(query)

    def rollback(self, *, statement_id) -> None:
        self.snowflake_connection.run_query(
            f"""
                INSERT OVERWRITE INTO {self.qualified_name} 
                SELECT * 
                  FROM {self.qualified_name} before(statement => '{statement_id}');
            """
        )

    def cluster_by(self, *args):
        """
        Wrapper for the CLUSTER BY command
        https://docs.snowflake.com/en/user-guide/tables-clustering-keys.html#changing-the-clustering-key-for-a-table

        Cluster a table by the arguments passed as args
        :param args: Columns or expressions to cluster the table by
        """
        response = self.snowflake_connection.run_query(
            f"ALTER TABLE {self.qualified_name} CLUSTER BY ({', '.join([*args])})"
        )
        return self


class SnowflakeMaterializedView(SnowflakeView):
    """
    Snowflake View.

    Parameters:
    -----------
    database: str
        Database where the view is located.
    schema: str
        Schema where the view is located.
    name: str
        Name of the view.
    snowflake_connection: SnowflakeConnection
        Connection to use for submitting Snowflake queries.
    comment: str
        Description of the view. Empty by default.
    quoted_identifiers: bool
        Whether to quote the view name. False be default.
    """

    def __init__(
        self,
        database: str,
        schema: str,
        name: str,
        snowflake_connection: SnowflakeConnection,
        *,
        comment: Optional[str] = None,
        quoted_identifiers: Optional[bool] = False
    ):
        super(SnowflakeView, self).__init__(
            object_type="MATERIALIZED VIEW",
            database=database,
            schema=schema,
            name=name,
            snowflake_connection=snowflake_connection,
            comment=comment,
            quoted_identifiers=quoted_identifiers
        )


def rename_type(type_name):
    """
    Return Snowflake-compatible column type name.
    """
    if type_name.upper() in {"SHORT", "SMALLINT", "INT", "INTEGER", "LONG", "BIGINT"}:
        return "NUMBER"
    elif type_name.upper() in {"FLOAT", "REAL", "DOUBLE"}:
        return "NUMBER(38,9)"
    elif type_name.upper() == "TIMESTAMP":
        return "TIMESTAMP_LTZ"
    elif type_name.upper() in {"STRUCT", "MAP"}:
        return "VARIANT"
    else:
        return type_name.upper()
