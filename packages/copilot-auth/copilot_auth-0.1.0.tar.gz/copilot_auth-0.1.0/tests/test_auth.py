import os

import copilot_auth as ca
import pytest

def test_authenticate_copilot_github_token():
    with pytest.raises(Exception) as exec:
        def token_handler(token):
            print(token)
        ca.authenticate_copilot_token([token_handler])
    os.unsetenv("GITHUB_ACCESS_TOKEN")
    assert exec.value is not None
    assert "GITHUB_ACCESS_TOKEN is not set. Please authenticate first for github access token" in exec.value.__str__()
