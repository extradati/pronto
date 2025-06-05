import logging
from typing import Callable

import joblib
from fastapi import FastAPI

from app.core.config import DEBUG


def preload_model():
    """
    In order to load model on memory to each worker
    """
    from app.services.predict import MachineLearningModelHandlerScore

    MachineLearningModelHandlerScore.get_model(joblib.load)


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        if DEBUG:
            logging.info("Starting application in DEBUG mode")
        else:
            logging.info("Starting application")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logging.info("Stopping application")

    return stop_app
