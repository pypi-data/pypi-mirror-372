# api-24sea-ai

**api-24sea-ai** is an extension package for
[API-24SEA](https://pypi.org/project/api-24sea/) that provides tools to interact
with the AI models hosted on the 24SEA platform.

## Installation

The package supports Python [3.8:3.12). To install it, run the following command
in your terminal:

``` shell
pip install api-24sea-ai
```

### Importing the package

``` python
# %%
# **Package Imports**
# - From the Python Standard Library
import logging
import os
import sys

# - From third party libraries
import pandas as pd
import dotenv  # <-- Not necessary to api-24sea-ai per se, but useful for
               #     loading environment variables. Install it with
               #     `pip install python-dotenv`

# - Local imports
from api_24sea.ai.version import __version__, parse_version
```

``` python
# %%
# **Package Versions**
print("Working Folder: ", os.getcwd())
print(f"Python Version: {sys.version}")
print(f"Pandas Version: {pd.__version__}")
print(f"Package {parse_version(__version__)}")
# **Notebook Configuration**
logging.basicConfig(level=logging.INFO)
```

### Setting up the environment variables (optional)

This step assumes that you have a file structure similar to the
following one:

``` shell
.
├── env
│   └── .env
├── notebooks
│   └── example.ipynb
└── requirements.txt
```

The [.env]{.title-ref} file should look like this:

``` shell
API_24SEA_USERNAME=your_value
API_24SEA_PASSWORD=your_value
```

With this in mind, the following code snippet shows how to load the
environment variables from the [.env]{.title-ref} file:

``` python
# %%
# **Load Environment Variables from .env File**
_ = dotenv.load_dotenv("../env/.env")
if _:
    print("Environment Variables Loaded Successfully")
    print(os.getenv("API_24SEA_USERNAME"))
    print(os.getenv("API_24SEA_PASSWORD"))
else:
    raise Exception("Environment Variables Not Loaded")
    print("Environment Variables Loaded Successfully")
    print(os.getenv("API_24SEA_USERNAME"))
    # print(os.getenv("API_24SEA_PASSWORD"))  # <-- Avoid printing sensitive info
else:
    raise Exception("Environment Variables Not Loaded")
```

###Performing AI model predictions

``` python
# %%
# **Authenticating AI Client and Viewing Models Overview**
from api_24sea.ai.core import AsyncAPI
api = AsyncAPI()
api.authenticate()  # <-- Ensure that the environment variables are set
api.models_overview  # <-- View the models overview
```

```python
# %%
# **Making Predictions**
api.get_predictions(
    sites="WF",
    locations="A01",
    model="mean_WF_A01_some_ai_model",
    start_timestamp="2020-03-01",
    end_timestamp="2020-06-01",
).head()
```

## Project Structure

```shell
    .
    ├── .azure/
    ├── .github/
    ├── docs/
    ├── api-24sea/
    │   └── ai/
    │       ├── __init__.py
    │       ├── core.py
    │       ├── schemas.py
    │       ├── utils.py
    │       └── version.py
    ├── notebooks/
    ├── tasks/
    ├── tests/
    ├── .flake8
    ├── .gitignore
    ├── .pre-commit-config.yaml
    ├── .pylintrc
    ├── .bitbucket-pipelines.yml
    ├── bumpversion.py
    ├── invoke.yaml
    ├── pyproject.toml
    ├── README.md
    ├── VERSION
    └── LICENSE
```

## License

The package is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
