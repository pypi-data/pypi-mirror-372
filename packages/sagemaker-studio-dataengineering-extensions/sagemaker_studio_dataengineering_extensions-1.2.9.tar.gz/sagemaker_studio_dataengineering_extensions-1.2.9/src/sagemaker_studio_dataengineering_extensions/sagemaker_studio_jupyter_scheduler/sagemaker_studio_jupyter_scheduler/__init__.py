import json
from os import path
from pathlib import Path

from ._version import __version__
from .extension import SageMakerSchedulingApp

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open(encoding="utf-8") as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]

def _jupyter_server_extension_points():
    return [{
        'module': 'sagemaker_studio_jupyter_scheduler',
        'app': SageMakerSchedulingApp,
    }]

def _load_jupyter_server_extension(nb_app):
    nb_app.log.info('Loading SageMaker Scheduler server extension')
    web_app = nb_app.web_app
    base_url = web_app.settings['base_url']

load_jupyter_server_extension = _load_jupyter_server_extension
