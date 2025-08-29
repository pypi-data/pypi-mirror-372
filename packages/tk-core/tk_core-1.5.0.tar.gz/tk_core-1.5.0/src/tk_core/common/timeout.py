import functools
import signal

from requests.exceptions import Timeout


def timeout(seconds: int = 10, error_message: Exception = Timeout) -> any:
    """
    Decorator to timeout functions without inherent timeouts (UNIX applicable only)
    """

    def decorator(func: any) -> any:
        def _handle_timeout(signum: any, frame: any) -> None:
            raise error_message

        @functools.wraps(func)
        def wrapper(*args: any, **kwargs: any) -> any:
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
