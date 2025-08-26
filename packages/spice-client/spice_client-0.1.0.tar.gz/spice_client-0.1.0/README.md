# SPICE Client

A Python client library for interacting with the [SPICE API](https://github.com/EERL-EPFL/spice-api) - a system for managing ice nucleation particle experiment data.

## Installation

```bash
pip install spice-client
```

## Quick Start

```python
from spice_client import ApiClient, Configuration
from helpers.wrapper import get_jwt_token
from spice_client.api.default_api import DefaultApi
import pandas as pd
import geopandas as gpd
import json

SERVER = "https://spice.epfl.ch"

auth_token = get_jwt_token(SERVER)
config = Configuration(host=SERVER, access_token=auth_token)
api = DefaultApi(ApiClient(configuration=config))

# List experiments
experiments = api.get_experiments()
print(experiments)
```

## Features

- Full API coverage for SPICE endpoints
- Keycloak authentication with token caching
- Type-safe models and responses
- Jupyter notebook integration
- Comprehensive documentation

## Authentication

The client includes Keycloak integration for secure API access. Authentication tokens are cached and refreshed.

## Documentation

For complete API documentation, visit the live API documentation at https://spice.epfl.ch/api/docs
