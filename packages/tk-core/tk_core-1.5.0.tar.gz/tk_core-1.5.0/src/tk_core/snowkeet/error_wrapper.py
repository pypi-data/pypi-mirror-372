"""
Python decorator that will wrap the function call in snowkeet_new
and output the current DB and SCHEMA values if there is an error, then raise the error.
"""

from functools import wraps

from tk_core.snowkeet.snow_logger import logger


def get_table_name(args: list, kwargs: dict) -> str | None:
    """
    Get the table name from the args or kwargs.

    If it is not found in the kwargs it will look for the second argument in the args.
    if it is not found in either, it will return None.

    Returns:
        str | None: The table name or None if not found.
    """
    # first check the kwargs
    table_name = kwargs.get("table_name")
    # if not, it is the second argument (if there are enough args)
    if not table_name and len(args) > 1:
        return args[1]
    return table_name


def sf_schema_checker(func):  # noqa
    """
    Logs the current database, schema, warehouse, and role
    before calling the function.

    If there is an error, it will log the error and the context
    in which the error occurred.

    This wrapper assumes that `table_name` is the second parameter
    or a named keyword argument in the function. All other attributes
    are from the object itself.

    That means this should really only be used for the following methods:
    - write_to_snowflake
    - merge_table_single_key
    - merge_table_dual_key
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):  # noqa
        try:
            table_name = get_table_name(args, kwargs)
            logger.info(
                f"{func.__name__} | "
                f"{self.database}.{self.schema}.{table_name} | "
                f"WH: {self.warehouse} | Role: {self.role}"
            )
            # call the function
            return func(self, *args, **kwargs)
        except Exception as e:
            default_msg = str(e)
            msg = (
                f"{default_msg}\n\n-- ERROR CONTEXT --\n"
                f"{func.__name__} | "
                f"{self.database}.{self.schema}.{table_name} | "
                f"WH: {self.warehouse} | Role: {self.role}"
            )
            raise type(e)(msg).with_traceback(e.__traceback__) from e

    return wrapper
