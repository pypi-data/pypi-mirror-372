# platform-python-sdk

This Python package is intended to provide clients and models for accessing the Platform APIs.

**Current Version**: `3.8.0`

## Requirements.

Python 3.6

## Installation & Usage
### pip install

```sh
pip install strongmind-platform-sdk
```

Then import and use the package:
```python
from strongmind_platform_sdk.platform_sdk.clients.oneroster_client import get_authenticated_oneroster_client
from oneroster_client.api.enrollments_management_api import EnrollmentsManagementApi
base_client = get_authenticated_oneroster_client(
            base_url,
            id_server_base_url,
            client_id,
            client_secret
        )

enrollments_client = EnrollmentsManagementApi(base_client)
enrollment = enrollments_client.get_enrollment("{UUID}")
```

## OneRoster Diagram
![spec-image018](https://user-images.githubusercontent.com/3137263/156631023-7bade029-d038-4a64-88d3-104d416d7d90.jpeg)
