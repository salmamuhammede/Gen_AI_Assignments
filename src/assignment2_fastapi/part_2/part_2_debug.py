# Standard library

# Third-party libraries
import logging
from logging.handlers import RotatingFileHandler

# Local imports


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("api-logs.log", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
)


logger = logging.getLogger(__name__)


def main():
    logger.info("Application Starting")


if __name__ == "__main__":
    main()
