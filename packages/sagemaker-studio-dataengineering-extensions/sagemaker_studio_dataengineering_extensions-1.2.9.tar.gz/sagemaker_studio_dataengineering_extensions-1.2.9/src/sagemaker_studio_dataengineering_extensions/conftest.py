# moved from original project sagemaker-jupyter-server-extension
import pytest

pytest_plugins = ("pytest_jupyter.jupyter_server", )

configs: list = [
    {
        "ServerApp": {
            "jpserver_extensions": {"sagemaker_jupyter_server_extension": True},
            "session_manager_class": "jupyter_server.services.sessions.sessionmanager.SessionManager"
        }
    }
]


@pytest.fixture(params=configs)
def jp_server_config(request):
    return request.param
