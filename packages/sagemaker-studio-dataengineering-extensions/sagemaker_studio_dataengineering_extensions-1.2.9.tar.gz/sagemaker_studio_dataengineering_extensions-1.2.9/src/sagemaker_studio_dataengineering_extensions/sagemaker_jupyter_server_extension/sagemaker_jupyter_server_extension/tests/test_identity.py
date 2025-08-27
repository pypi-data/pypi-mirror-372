import subprocess
from unittest.mock import patch

from jupyter_server.auth.identity import User

from ..identity import SageMakerIdentityProvider

identity_provider = SageMakerIdentityProvider()

@patch("subprocess.run")
def test_get_user_with_git_config_response_success(mock_run):
    identity_provider._SageMakerIdentityProvider__get_git_username.cache_clear()
    mock_run.return_value = subprocess.CompletedProcess(args=['git', 'config', '--get', 'user.name'], returncode=0, stdout='testuser\n')
    user = identity_provider.get_user(mock_run)
    assert user == User(username='testuser', name='testuser', display_name='testuser', initials='T', avatar_url=None, color=None)

@patch("subprocess.run")
def test_get_user_with_git_config_response_failure(mock_run):
    # Clear cache before test to ensure clean state
    identity_provider._SageMakerIdentityProvider__get_git_username.cache_clear()
    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=['git', 'config', '--get', 'user.name'])
    user = identity_provider.get_user(mock_run)
    assert user == User(username='User', name='User', display_name='User', initials='U', avatar_url=None, color=None)
