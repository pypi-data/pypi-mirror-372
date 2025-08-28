Copilot Authentication: copilot-auth
-----------
[![PyPI version](https://badge.fury.io/py/copilot-auth.svg)](https://badge.fury.io/py/copilot-auth)
[![License](https://img.shields.io/pypi/l/copilot-auth.svg)](https://pypi.org/project/copilot-auth/)
[![Downloads](https://static.pepy.tech/personalized-badge/copilot_auth?period=total&units=none&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/copilot_auth)
[![coverage](https://img.shields.io/codecov/c/github/bhachauk/copilot-auth)](https://app.codecov.io/gh/bhachauk/copilot-auth)


### Prerequisite

- python>=3.13
- requests

```shell
pip install requests
```

### Installation

```shell
pip install copilot-auth
```


### Getting started

**Steps to fetch copilot github token :**

- Fetch Github Access token using device flow
- Fetch Copilot Github token using Github Access token

```python
import copilot_auth as ca

# Custom token handler to process the token
def token_handler(token):
    print(token)

# Fetch the github access token
ca.authenticate_github_access_token([token_handler])

# Fetch the copilot github token using the github access token
ca.authenticate_copilot_token([token_handler])

```