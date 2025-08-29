import pandas as pd


def col_case_change(dataframe: pd.DataFrame, case: str = "upper") -> pd.DataFrame:
    """Changes case of column names in a pandas dataframe
    Mainly used to change to upper case for Snowflake

    Args:
        dataframe (pd.DataFrame): pandas dataframe
        case (str): case to change to, either 'upper' or 'lower'

    Raises:
        ValueError: If case parameter is not 'upper' or 'lower'

    Returns:
        pd.DataFrame: pandas dataframe with case changed
    """
    if case in ["upper", "lower"]:
        # lower case all values in case parameter
        case = case.lower()
        # get list of columns
        cols = list(dataframe.columns)
        # create list of new columns with case applied
        new_cols = [getattr(x, case)() for x in cols]
        # rename columns
        dataframe.columns = new_cols

        return dataframe
    else:
        raise ValueError("case parameter must be 'upper' or 'lower' in pandas_col_case_change function")
