import requests
import pandas as pd
from api_to_dataframe.utils.logger import logger


class GetData:
    @staticmethod
    def get_response(endpoint: str, headers: dict, connection_timeout: int):
        # Make the request
        response = requests.get(endpoint, timeout=connection_timeout, headers=headers)

        # Attempt to raise for status to catch errors
        response.raise_for_status()

        return response

    @staticmethod
    def to_dataframe(response):
        df = pd.DataFrame(response)

        # Check if DataFrame is empty
        if df.empty:
            error_msg = "::: DataFrame is empty :::"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return df
