from api_to_dataframe.models.retainer import retry_strategies, Strategies
from api_to_dataframe.models.get_data import GetData
from api_to_dataframe.utils.logger import logger


class ClientBuilder:
    def __init__(  # pylint: disable=too-many-positional-arguments,too-many-arguments
        self,
        endpoint: str,
        headers: dict = None,
        retry_strategy: Strategies = Strategies.NO_RETRY_STRATEGY,
        retries: int = 3,
        initial_delay: int = 1,
        connection_timeout: int = 1,
    ):
        """
        Initializes the ClientBuilder object.

        Args:
            endpoint (str): The API endpoint to connect to.
            headers (dict, optional): The headers to use for the API request. Defaults to None.
            retry_strategy (Strategies, optional): Defaults to Strategies.NO_RETRY_STRATEGY.
            retries (int): The number of times to retry a failed request. Defaults to 3.
            initial_delay (int): The delay between retries in seconds. Defaults to 1.
            connection_timeout (int): The timeout for the connection in seconds. Defaults to 1.

        Raises:
            ValueError: If endpoint is an empty string.
            ValueError: If retries is not a non-negative integer.
            ValueError: If delay is not a non-negative integer.
            ValueError: If connection_timeout is not a non-negative integer.
        """

        if headers is None:
            headers = {}
        if endpoint == "":
            error_msg = "endpoint cannot be an empty string"
            logger.error(error_msg)
            raise ValueError
        if not isinstance(retries, int) or retries < 0:
            error_msg = "retries must be a non-negative integer"
            logger.error(error_msg)
            raise ValueError
        if not isinstance(initial_delay, int) or initial_delay < 0:
            error_msg = "initial_delay must be a non-negative integer"
            logger.error(error_msg)
            raise ValueError
        if not isinstance(connection_timeout, int) or connection_timeout < 0:
            error_msg = "connection_timeout must be a non-negative integer"
            logger.error(error_msg)
            raise ValueError

        self.endpoint = endpoint
        self.retry_strategy = retry_strategy
        self.connection_timeout = connection_timeout
        self.headers = headers
        self.retries = retries
        self.delay = initial_delay

    @retry_strategies
    def get_api_data(self):
        """
        Retrieves data from the API using the defined endpoint and retry strategy.

        This function sends a request to the API using the endpoint, headers, and
        connection timeout specified in the instance attributes. It uses the
        defined retry strategy to handle potential failures and retries.

        Returns:
            dict: The JSON response from the API as a dictionary.
        """
        response = GetData.get_response(
            endpoint=self.endpoint,
            headers=self.headers,
            connection_timeout=self.connection_timeout,
        )

        return response.json()

    @staticmethod
    def api_to_dataframe(response: dict):
        """
        Converts an API response to a DataFrame.

        This function takes a dictionary response from an API,
        uses the `to_dataframe` function from the `GetData` class
        to convert it into a DataFrame, and logs the operation as successful.

        Args:
            response (dict): The dictionary containing the API response.

        Returns:
            DataFrame: A pandas DataFrame containing the data from the API response.
        """
        return GetData.to_dataframe(response)
