import logging

logging.basicConfig(
    encoding="utf-8",
    format="%(asctime)s :: api-to-dataframe[%(levelname)s] :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z",
    level=logging.INFO,
)

# Initialize traditional logger
logger = logging.getLogger("api-to-dataframe")
