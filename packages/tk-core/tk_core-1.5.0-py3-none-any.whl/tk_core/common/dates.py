import datetime


def datecode() -> str:
    """Generate YYYYMMDD date code, as string"""
    current_date = datetime.datetime.today()
    return current_date.strftime("%Y%m%d")


def add_timestamps(incoming: list | dict) -> list | dict:
    """Add created_at and updated_at timestamps to incoming dictionary or list of dictionaries."""
    ts = datetime.datetime.now()
    if isinstance(incoming, list):
        return [_add_timestamps(item, ts) for item in incoming]
    else:
        return _add_timestamps(incoming, ts)


def _add_timestamps(incoming: dict, ts: datetime) -> dict:
    """Add created_at and updated_at timestamps to incoming dictionary."""

    incoming["created_at"] = ts
    incoming["updated_at"] = ts
    return incoming
