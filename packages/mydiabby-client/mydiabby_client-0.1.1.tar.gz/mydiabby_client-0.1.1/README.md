# mydiabby-client

`mydiabby-client` is a Python package that provides an API client for exporting MyDiabby user data, including CGM, pump, and account information, as JSON files.

## Installation

Install the package from PyPI:

```bash
pip install mydiabby-client
```

## Usage

Import the package in your Python code:

```python
from mydiabby_client import MyDiabbyClient
```

Initialise the client as:

```python
client = MyDiabbyClient(f"{username}", f"{password}")
```

Docstrings are written in the source code to help you find the relevant methods. For the moment, the 2 most relevant are `client.get_account()` to get all the relevant account information and `client.get_data()` to access all the pump and CGM data that has been uploaded to MyDiabby.