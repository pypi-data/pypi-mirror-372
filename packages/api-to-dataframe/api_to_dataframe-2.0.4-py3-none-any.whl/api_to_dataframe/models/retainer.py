import time
from enum import Enum

from requests.exceptions import RequestException
from api_to_dataframe.utils.logger import logger
from api_to_dataframe.utils import Constants


class Strategies(Enum):
    NO_RETRY_STRATEGY = 0
    LINEAR_RETRY_STRATEGY = 1
    EXPONENTIAL_RETRY_STRATEGY = 2


def retry_strategies(func):
    def wrapper(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
        retry_number = 0
        while retry_number < args[0].retries:
            try:
                if retry_number > 0:
                    logger.info(
                        f"Trying for the {retry_number} of {Constants.MAX_OF_RETRIES} retries. Using {args[0].retry_strategy}"
                    )
                return func(*args, **kwargs)
            except RequestException as e:
                retry_number += 1

                if args[0].retry_strategy == Strategies.NO_RETRY_STRATEGY:
                    raise e
                if args[0].retry_strategy == Strategies.LINEAR_RETRY_STRATEGY:
                    time.sleep(args[0].delay)
                elif args[0].retry_strategy == Strategies.EXPONENTIAL_RETRY_STRATEGY:
                    time.sleep(args[0].delay * retry_number)

                if retry_number in (args[0].retries, Constants.MAX_OF_RETRIES):
                    logger.error(f"Failed after {retry_number} retries")
                    raise e

    return wrapper
