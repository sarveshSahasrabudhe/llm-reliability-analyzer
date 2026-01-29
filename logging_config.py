import logging
import os
import sys

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # You can add FileHandler here if needed
        ]
    )
    # Set lower level for some noisy libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger("llm_reliability_analyzer")
