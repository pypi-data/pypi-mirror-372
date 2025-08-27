import os
import logging
from flask import g
from logging.handlers import TimedRotatingFileHandler
from prediction_market_agent_tooling.loggers import logger


class CustomLogger:
    def __init__(self, name: str, loglevel=logging.INFO):
        """Initialize the CustomLogger class

        Args:
            name (str): the name of the logger (e.g., __name__).
            loglevel (_type_, optional): the log level. Defaults to logging.INFO.
        """
        # Create a custom logger
        self.logger = logger

    def getlog(self):
        return self.logger
