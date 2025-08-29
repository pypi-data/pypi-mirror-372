from __future__ import annotations

import os
import uuid
from datetime import datetime
from types import TracebackType
from typing import Any

import numpy as np
import pandas as pd
import snowflake.snowpark as sp
import snowflake.snowpark.functions as F
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa, rsa
from retry import retry
from snowflake.snowpark import DataFrame, Row, Session
from snowflake.snowpark.types import StructType, VariantType
from tk_core.common.dictionary import replace_empty_dict_value
from tk_core.common.s3 import S3Util
from tk_core.snowkeet.error_wrapper import sf_schema_checker
from tk_core.snowkeet.snow_logger import logger

# TODO: Investigate better defaults and potential wrapper for sane configs.


class Snowkeet:
    """
    A class for interacting with Snowflake databases. Include common helper patterns

    Args:
        database (str, optional): The name of the database to connect to. Defaults to None.
        schema (str, optional): The name of the schema to connect to. Defaults to None.
        role (str, optional): The name of the role to use. Defaults to None.
        warehouse (str, optional): The name of the warehouse to use. Defaults to None.
        private_key_str (str, optional): The private key string to use. Defaults to None.
        private_key_encrypted (bool, optional): Whether the private key is encrypted. Defaults to False.

    Methods:
        session(): Returns the current session object.
        get_schema(table: str) -> sp.types.StructType: Returns the schema for a given table.
        write_to_snowflake(df: pd.DataFrame, table_name: str, mode: str = "append"):
            Writes a pandas DataFrame to Snowflake.
        merge_table_single_key(df: pd.DataFrame, table_name: str, key: str):
            Merges a pandas DataFrame into a Snowflake table using a single key.
        merge_table_dual_key(df: pd.DataFrame, table_name: str, key1: str, key2: str):
            Merges a pandas DataFrame into a Snowflake table using two keys.
        get_table_with_filter(table_name: str, var: str, value: str) -> pd.DataFrame:
            Gets data from a table with a single filter.
        get_table_with_dual_filter(table_name: str, var_1: str, var_1_value: str, var_2: str, var_2_value: str)
        -> pd.DataFrame:
            Gets data from a table with two filters.
        delete_from_table_dual_var(table_name: str, var_1: str, var_1_value: str, var_2: str, var_2_value: str)
         -> dict:
             Deletes rows from a table using two variables.
        custom_dml(sql: str) -> dict: Runs a custom DML statement in Snowflake.

    """

    def __init__(
        self,
        database: str | None = None,
        schema: str | None = None,
        role: str | None = None,
        warehouse: str | None = None,
        private_key_str: str | None = None,
        private_key_encrypted: bool = False,
    ) -> None:
        # check to make sure SNOWFLAKE_ACCOUNT, SNOWFLAKE_USERNAME, SNOWFLAKE_PASSWORD are set
        self.validate_account_vars()
        # assign the values from the environment variables or the arguments
        self.database = database or os.environ.get("SNOWFLAKE_DB")
        if self.database is None:
            raise ValueError("Database name is required as an argument or in the environment variable SNOWFLAKE_DB.")
        self.schema = schema or os.environ.get("SNOWFLAKE_SCHEMA")
        if self.schema is None:
            raise ValueError("Schema name is required as an argument or in the environment variable SNOWFLAKE_SCHEMA.")
        self.role = role or os.environ.get("SNOWFLAKE_ROLE")
        if self.role is None:
            raise ValueError("Role name is required as an argument or in the environment variable SNOWFLAKE_ROLE.")
        self.warehouse = warehouse or os.environ.get("SNOWFLAKE_WAREHOUSE")
        if self.warehouse is None:
            raise ValueError("Warehouse name is required as an argument or in the environment variable SNOWFLAKE_WAREHOUSE.")
        if private_key_encrypted and "SNOWFLAKE_PRIVATE_PASSCODE" not in os.environ:
            raise ValueError("Need SNOWFLAKE_PRIVATE_PASSCODE environment variable to decrypt the private key.")

        self.private_key_str = private_key_str
        self.private_key_path = os.environ.get("SNOWFLAKE_PRIVATE_KEY_FILE")

        if self.private_key_str is None and self.private_key_path is None:
            self._conn_params = {
                "account": os.environ["SNOWFLAKE_ACCOUNT"],
                "user": os.environ["SNOWFLAKE_USERNAME"],
                "password": os.environ["SNOWFLAKE_PASSWORD"],
                "role": self.role,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
                "paramstyle": "qmark",
            }
        else:
            # get the private key
            if private_key_str:
                pkb = self.get_private_key_str()
            else:
                pkb = self.get_private_key_file(private_key_encrypted)

            self._conn_params = {
                "account": os.environ["SNOWFLAKE_ACCOUNT"],
                "user": os.environ["SNOWFLAKE_USERNAME"],
                "role": self.role,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
                "private_key": pkb,
                "private_key_file_pwd": None,
                "paramstyle": "qmark",
            }

        self._session = None

    @staticmethod
    def validate_account_vars() -> None:
        """Validate that the required environment variables are set."""
        if "SNOWFLAKE_ACCOUNT" not in os.environ:
            raise ValueError("SNOWFLAKE_ACCOUNT environment variable is required.")
        if "SNOWFLAKE_USERNAME" not in os.environ:
            raise ValueError("SNOWFLAKE_USERNAME environment variable is required.")
        if "SNOWFLAKE_PASSWORD" not in os.environ and "SNOWFLAKE_PRIVATE_KEY_FILE" not in os.environ:
            raise ValueError("SNOWFLAKE_PASSWORD environment variable is required if SNOWFLAKE_PRIVATE_KEY_FILE is not set.")

    def __enter__(
        self,
        schema: str | None = None,
        database: str | None = None,
    ) -> Snowkeet:
        """
        Enter the context manager and return the session object.
        Offer option to change schema and database
        """
        if schema:
            self._conn_params["schema"] = schema
        if database:
            self._conn_params["database"] = database
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        Close the session when exiting the context manager.
        """
        self._close_session()

    def __str__(self) -> str:
        cloned_params = {k: v for k, v in self._conn_params.items() if k != "password"}
        return str(cloned_params)

    @retry(Exception, tries=4, delay=1, backoff=2)
    def _create_session(self) -> None:
        """Creates a new session object."""
        logger.info(f"Creating new session. DB: {self.database} SCHEMA: {self.schema} ROLE: {self.role} WH: {self.warehouse}")
        self._session = Session.builder.configs(self._conn_params).create()

    def _close_session(self) -> None:
        """Closes the current session object."""
        if self._session:
            logger.info(
                f"Closing current session. DB: {self.database} SCHEMA: {self.schema} ROLE: {self.role} WH: {self.warehouse}"
            )
            self._session.close()

    @property
    def session(self) -> Session:
        """Returns the current session object."""
        if not self._session:
            self._create_session()
        return self._session

    def set_query_tag(self, query_tag: str) -> None:
        """Sets the query tag for the session."""
        self.session.query_tag = query_tag

    def delete_query_tag(self) -> None:
        """Deletes the query tag for the session."""
        self.session.query_tag = None

    def set_schema(self, schema: str) -> None:
        """Sets the schema for the session."""
        if schema != self._conn_params["schema"]:
            self._conn_params["schema"] = schema
            self._close_session()
            self._create_session()

    def set_database(self, database: str) -> None:
        """Sets the database for the session."""
        if database != self._conn_params["database"]:
            self._conn_params["database"] = database
            self._close_session()
            self._create_session()

    def get_schema(self, table: str) -> StructType:
        """Returns table schema from Snowflake for an sp.DataFrame"""
        return self.session.table(table).schema

    def create_df_with_schema(self, data: list | dict, table_name: str, drop_duplicates: bool = False) -> DataFrame:
        """Create a DataFrame with selected data and a particular schema from Snowflake"""
        schema = self.get_schema(table_name)
        df = self.session.create_dataframe(data, schema)
        if drop_duplicates:
            return df.drop_duplicates()
        else:
            return df

    @staticmethod
    def get_merge_conditions(df: pd.DataFrame, update_when_matched: bool) -> list:
        """
        Get the merge conditions for a DataFrame and a table in Snowflake

        If we want to update the values when matched, we need to create a list of conditions
        We will always insert when not matched

        Importantly, this function also allows for the columns to be in any order
        """
        update_values = {col: df[col] for col in df.columns}

        insert_values = update_values.copy()
        insert_values["CREATED_AT"] = insert_values["UPDATED_AT"]

        conditions = [F.when_not_matched().insert(insert_values)]
        # if set, update the values when matched
        if update_when_matched:
            conditions.append(F.when_matched().update(update_values))

        return conditions

    @sf_schema_checker
    def merge_table_single_key(
        self,
        obj: list | dict | pd.DataFrame,
        table_name: str,
        key: str,
        drop_duplicates: bool = False,
        update_when_matched: bool = True,
    ) -> tuple:
        """
        Merge a single-key table in Snowflake with incoming data.

        Args:
            obj (Any): The incoming data to merge.
            table_name (str): The name of the table to merge.
            key (str): The name of the key to use for merging.
            drop_duplicates (bool, optional): Whether to drop duplicates. Defaults to False.

        Returns:
            Tuple: A tuple containing the merge result and the merged DataFrame.
        """
        if "UPDATED_AT" in obj.columns:
            obj["UPDATED_AT"] = pd.Timestamp.now()
        df = self.create_df_with_schema(obj, table_name, drop_duplicates)
        target_table = self.session.table(table_name)

        logger.info(f"{df.columns=}")
        logger.info(f"{target_table.columns=}")

        # get the merge conditions depending on if we want to update_when_matched
        conditions = self.get_merge_conditions(df, update_when_matched)

        # merge the results
        # if we don't find a match
        # merge only the columns in the incoming data
        merge_result = target_table.merge(df, (target_table[key] == df[key]), conditions)
        return (merge_result, df)

    @sf_schema_checker
    def merge_table_dual_key(
        self,
        obj: pd.DataFrame,
        table_name: str,
        key1: str,
        key2: str,
        drop_duplicates: bool = False,
        update_when_matched: bool = True,
    ) -> tuple:
        """
        Merge a single-key table in Snowflake with incoming data.

        Args:
            obj (pd.DataFrame): The incoming data to merge.
            table_name (str): The name of the table to merge.
            key (str): The name of the key to use for merging.
            drop_duplicates (bool, optional): Whether to drop duplicates. Defaults to False.

        Returns:
            Tuple: A tuple containing the merge result and the merged DataFrame.
        """
        if "UPDATED_AT" in obj.columns:
            obj["UPDATED_AT"] = pd.Timestamp.now()
        df = self.create_df_with_schema(obj, table_name, drop_duplicates)
        target_table = self.session.table(table_name)

        logger.info(f"{df.columns=}")
        logger.info(f"{target_table.columns=}")

        # pull the conditions for the merge
        conditions = self.get_merge_conditions(df, update_when_matched)
        merge_result = target_table.merge(
            df,
            (target_table[key1] == df[key1]) & (target_table[key2] == df[key2]),
            conditions,
        )
        return (merge_result, df)

    @sf_schema_checker
    def merge_table(
        self,
        obj: pd.DataFrame,
        table_name: str,
        keys: list[str],
        drop_duplicates: bool = False,
        update_when_matched: bool = True,
    ) -> tuple:
        """
        Merge a multi-key table in Snowflake with incoming data.

        Args:
            obj (pd.DataFrame): The incoming data to merge.
            table_name (str): The name of the table to merge.
            keys (list[str]): The list of keys to use for merging.
            drop_duplicates (bool, optional): Whether to drop duplicates. Defaults to False.

        Returns:
            Tuple: A tuple containing the merge result and the merged DataFrame.
        """
        if "UPDATED_AT" in obj.columns:
            obj["UPDATED_AT"] = pd.Timestamp.now()
        df = self.create_df_with_schema(obj, table_name, drop_duplicates)
        target_table = self.session.table(table_name)

        logger.info(f"{df.columns=}")
        logger.info(f"{target_table.columns=}")

        # pull the conditions for the merge
        conditions = self.get_merge_conditions(df, update_when_matched)
        merge_condition = F.lit(True)
        for key in keys:
            merge_condition &= target_table[key] == df[key]

        merge_result = target_table.merge(df, merge_condition, conditions)
        return (merge_result, df)

    def update_table_one_condition(
        self,
        table_name: str,
        column_to_update: str,
        new_value: Any,
        condition_column: str | None = None,
        condition_value: Any | None = None,
    ) -> tuple:
        """
        Update a table in Snowflake with incoming data.

        Args:
            table_name (str): The name of the table to update.
            column_to_update (str): The name of the column to update.
            new_value (Any): The new value to insert into the column.
            condition (dict): The condition to use for updating.
                should be formatted as the column name as the key and the value to match as the value
        """
        logger.info(
            "update_table_one_condition | "
            f"{self.database}.{self.schema}.{table_name} | "
            f"WH: {self.warehouse} | Role: {self.role}"
        )
        target_table = self.session.table(table_name)
        update_dictionary = {
            column_to_update: new_value,
            "UPDATED_AT": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if condition_column is None or condition_value is None:
            update_result = target_table.update(update_dictionary)

        update_result = target_table.update(
            update_dictionary,
            target_table[condition_column] == condition_value,
        )
        return update_result

    def remove_ts(self, df: sp.DataFrame) -> sp.DataFrame:
        """Remove the timestamp columns from a DataFrame"""
        return df.drop("created_at").drop("updated_at")

    @sf_schema_checker
    def write_to_snowflake(self, dataframe: pd.DataFrame, table_name: str, mode: str = "append") -> None:
        """
        Writes a table to Snowflake using the schema from Snowpark.

        Args:
            snow (Snowkeet): _description_
            dataframe (list): A list of dictionaries with columns that match the schema we're writing to
            table_name (str): Name of table
            mode (str, optional): Append or overwrite the table. Defaults to 'append'. Use caution with 'overwrite'.
        """

        if dataframe.empty:
            empty_df_error_msg = "Error in write_to_snowflake: 'dataframe' arg cannot be empty"
            logger.error(empty_df_error_msg)
            raise Exception(empty_df_error_msg)

        # get the schema for the table
        schema = self.get_schema(table_name)
        # clean up dataframe
        dataframe = self.pre_process_dataframe_for_write(dataframe, schema)

        # write the dataframe to snowflake using th
        sf_df = None
        try:
            sf_df = self.session.create_dataframe(data=dataframe, schema=schema)
        except Exception as e:
            error_id = uuid.uuid4()
            logger.error(f"Error saving dataframe to Snowflake schema: {e}\nError ID: {error_id}")
            s3 = S3Util("tk-data-engineering")
            s3.write_json(
                f"troubleshooting/snowflake-schema-error/{error_id}.json",
                dataframe.to_dict(),
            )
        try:
            if sf_df:
                sf_df.write.mode(mode).save_as_table(table_name)
                return len(dataframe)
        except Exception as e:
            error_id = uuid.uuid4()
            logger.error(f"Error writing to Snowflake: {e}")
            logger.error(f"Error ID: {error_id}")
            s3 = S3Util("tk-data-engineering")
            s3.write_json(
                f"troubleshooting/snowflake-write-error/{error_id}.json",
                dataframe.to_dict(),
            )

    def create_snowflake_schema(self, schema_name: str) -> None:
        try:
            self.execute_sql("CREATE SCHEMA IF NOT EXISTS ?", params=[schema_name])
            logger.info(f"Schema {schema_name} created")
        except Exception as e:
            logger.error(f"Error creating schema {schema_name}: {e}")

    def count_table(self, table_name: str) -> int:
        """Count the number of rows in a table in Snowflake.
        Returns: int: The number of rows in the table."""
        count_sql = "SELECT (SELECT COUNT(*) FROM IDENTIFIER(?)) AS COUNT"
        counts_dct = self.execute_sql(count_sql, params=[table_name])
        return counts_dct[0]["COUNT"]

    def output_config(self) -> None:
        """Output the current configuration for the session."""
        config_output = (
            f"account: {self._conn_params['account']} | "
            f"db: {self.database} | schema: {self.schema} | "
            f"role: {self.role} | warehouse: {self.warehouse}"
        )
        logger.info(config_output)

    def get_top_result_filtered(self, table_name: str, filter_var: str, filter_value: str, column_to_get: str) -> bool:
        """
        Check if rows exist in a table.

        Args:
            snow (Snowkeet): The Snowkeet object.
            table_name (str): The name of the table to check.
            filter_value (str): The value to filter on.

        Returns:
            bool: True if rows exist, False if not.
        """
        query = "SELECT top 1 IDENTIFIER(?) from IDENTIFIER(?) where IDENTIFIER(?) = ?"
        rows = self.execute_sql(query, params=[column_to_get, table_name, filter_var, filter_value])
        return rows[0][0]

    def pre_process_dataframe_for_write(self, dataframe: pd.DataFrame, schema: StructType) -> pd.DataFrame:
        """
        Pre-process a DataFrame before writing to Snowflake

        Args:
            dataframe (pd.DataFrame): The DataFrame to process.
            schema (StructType): The schema for the DataFrame in snowflake

        Returns:
            pd.DataFrame: The processed DataFrame.
        """
        # replace NaN with None
        dataframe = dataframe.replace(np.nan, None)
        # do some formatting to match the columns to the schema
        dataframe.columns = [col.upper() for col in dataframe.columns]
        # replace empty {}s in variant columns with ""
        dataframe = self.clean_variant_empty_dictionary_values(dataframe, schema)
        # reorder columns in dataframe to match schema
        return dataframe[schema.names]

    @staticmethod
    def clean_variant_empty_dictionary_values(dataframe: pd.DataFrame, schema: StructType) -> pd.DataFrame:
        """
        Clean variant column with empty dictionaries

        Args:
            dataframe (pd.DataFrame): The DataFrame to clean.
            schema (StructType): The schema for the DataFrame in snowflake

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        variant_column_names = [x.name for x in schema if isinstance(x.datatype, VariantType)]
        for col in variant_column_names:
            dataframe[col] = dataframe[col].apply(replace_empty_dict_value)

        return dataframe

    def execute_sql(self, sql_query_str: str, params: list = None) -> list[Row]:
        """
        Execute a SQL statement in Snowflake.
        """
        return self.session.sql(sql_query_str, params=params).collect()

    def check_if_rows_exist(self, table_name: str, filter_var: str, filter_value: str) -> bool:
        """
        Check if rows exist in a table.

        Args:
            snow (Snowkeet): The Snowkeet object.
            table_name (str): The name of the table to check.
            filter_value (str): The value to filter on.

        Returns:
            bool: True if rows exist, False if not.
        """
        query_str = "SELECT exists(select top 1 1 from IDENTIFIER(?) where IDENTIFIER(?) = ?) as exist_check"
        rows = self.execute_sql(query_str, params=[table_name, filter_var, filter_value])
        return rows[0]["EXIST_CHECK"]

    def get_table_two_var_filter(
        self,
        table_name: str,
        var_1: str,
        var_1_value: str,
        var_2: str,
        var_2_value: str,
    ) -> pd.DataFrame:
        """
        Get table from snowflake with two variables to filter

        Args:
            table_name (str): The name of the table to delete from.
            var_1 (str): The first variable to use
            var_1_value (str): The value of the first variable to use
            var_2 (str): The second variable to use
            var_2_value (str): The value of the second variable to use

        Returns:
            pandas.DataFrame: The URLs to project from Snowflake.
        """
        try:
            query = "select * from IDENTIFIER(?) where IDENTIFIER(?) = ? and IDENTIFIER(?) = ?"
            df = self.session.sql(query, params=[table_name, var_1, var_1_value, var_2, var_2_value]).to_pandas()
            return df
        except Exception:
            logger.error(f"Error getting table {table_name} with filter {var_1} = {var_1_value} and {var_2} = {var_2_value}")

    def delete_from_table_dual_var(
        self,
        table_name: str,
        var_1: str,
        var_1_value: str,
        var_2: str,
        var_2_value: str,
    ) -> dict:
        """
        Delete from a table in Snowflake using two variables.

        Args:
            table_name (str): The name of the table to delete from.
            var_1 (str): The first variable to use for deletion.
            var_1_value (str): The value of the first variable to use for deletion.
            var_2 (str): The second variable to use for deletion.
            var_2_value (str): The value of the second variable to use for deletion.

        Returns:
            None
        """
        query = "delete from IDENTIFIER(?) where IDENTIFIER(?) = ? and IDENTIFIER(?) = ?"
        results = self.execute_sql(query, params=[table_name, var_1, var_1_value, var_2, var_2_value])
        return results[0].as_dict()

    def custom_dml(self, sql: str, params: list = None) -> dict:
        """
        Run a custom DML statement in Snowflake.

        Args:
            sql (str): The SQL statement to run.

        Returns:
            None
        """
        results = self.session.sql(sql, params=params).collect()
        return results[0].as_dict()

    def get_private_key_file(self, private_key_encrypted: bool) -> bytes:
        """Read the private key from the file and return the serialized private key."""

        if private_key_encrypted:
            password = os.environ.get("SNOWFLAKE_PRIVATE_PASSCODE").encode()
        else:
            password = None

        with open(self.private_key_path, "rb") as key:
            p_key = serialization.load_pem_private_key(
                key.read(),
                password=password,
                backend=default_backend(),
            )

        return self.serialize_private_key(p_key)

    def get_private_key_str(self) -> bytes:
        """Read the private key from the string and return the serialized private key."""
        p_key = serialization.load_pem_private_key(
            self.private_key_str.encode("utf-8"),
            # Replace with the correct password if the key is encrypted
            password=None,
            backend=default_backend(),
        )

        return self.serialize_private_key(p_key)

    def serialize_private_key(self, private_key: rsa.RSAPrivateKey | dsa.DSAPrivateKey) -> bytes:
        """Serialize the private key and return the serialized private key."""
        pkb = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return pkb
