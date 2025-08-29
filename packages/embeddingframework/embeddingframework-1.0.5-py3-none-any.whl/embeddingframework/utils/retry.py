import backoff
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def retry_on_exception(max_tries: int = 5):
    """
    Decorator for retrying a function on any exception with exponential backoff.
    """
    return backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=max_tries,
        jitter=None,
        on_backoff=lambda details: logging.warning(
            f"Retrying after exception: {details.get('exception')}, try {details.get('tries')}/{max_tries}"
        )
    )
