import time

from loguru import logger


class Timer:
    def __init__(self):
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        logger.info(f"code executed in {end_time - self.start_time} seconds")
