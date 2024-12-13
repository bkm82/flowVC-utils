import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
from flowvcutils.utils import get_project_root
import os
import uuid


def test_logging_integration():

    logger = logging.getLogger("test_logging_integration")
    settup_logging()
    unique_id = str(uuid.uuid4())
    test_message = f"Test Log From test_logging_integration. unique ID: {unique_id}"
    logger.debug(test_message)
    root = get_project_root()
    log_file = os.path.join(root, "logs", "flowvcutils.log")

    found_message = False
    with open(log_file, "r") as f:
        if test_message in f.read():
            found_message = True

    assert found_message, "Test message not found in log file"

    assert True
