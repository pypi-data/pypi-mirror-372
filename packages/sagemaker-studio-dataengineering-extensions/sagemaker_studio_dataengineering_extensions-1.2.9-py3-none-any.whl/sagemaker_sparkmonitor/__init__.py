"""Package sparkmonitor
    kernelextension.py is the Jupyter ipython kernel extension.
"""

import logging
import os

logger = logging.getLogger(__name__)
logger.name = "SageMakerSparkMonitorWidget"
logger.setLevel(logging.INFO)
logger.propagate = True

logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logPath = "/var/log/apps"
fileName = "spark_monitor"
log_filename = f"{logPath}/{fileName}.log"
try:
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
except:
    log_filename = "/tmp" + log_filename
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
fileHandler = logging.FileHandler(log_filename)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

def _jupyter_nbextension_paths():
    """Used by 'jupyter nbextension' command to install frontend extension"""
    return [dict(
        section='notebook',
        # the path is relative to the `my_fancy_module` directory
        src='nbextension',
        # directory in the `nbextension/` namespace
        dest='sagemaker_sparkmonitor',
        # _also_ in the `nbextension/` namespace
        require='sagemaker_sparkmonitor/extension')]

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "sagemaker_sparkmonitor"
    }]
