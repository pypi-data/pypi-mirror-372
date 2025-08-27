from functools import partial

from .extension import Extension

__version__ = "0.3.0"
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.propagate = True
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logPath = "/var/log/apps"
fileName = "server_extension"
log_filename = f"{logPath}/{fileName}.log"
try:
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
except:
    log_filename = "/tmp" + log_filename
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
fileHandler = logging.FileHandler(log_filename)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

def _jupyter_server_extension_points():
    return [{
        "module": "sagemaker_jupyter_server_extension",
        "app": Extension
    }]


