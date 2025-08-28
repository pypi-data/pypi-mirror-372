# Health

Types:

```python
from bluehive.types import HealthCheckResponse
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/bluehive/resources/health.py">check</a>() -> <a href="./src/bluehive/types/health_check_response.py">HealthCheckResponse</a></code>

# Version

Types:

```python
from bluehive.types import VersionRetrieveResponse
```

Methods:

- <code title="get /v1/version">client.version.<a href="./src/bluehive/resources/version.py">retrieve</a>() -> <a href="./src/bluehive/types/version_retrieve_response.py">VersionRetrieveResponse</a></code>

# Providers

Types:

```python
from bluehive.types import ProviderLookupResponse
```

Methods:

- <code title="get /v1/providers/lookup">client.providers.<a href="./src/bluehive/resources/providers.py">lookup</a>(\*\*<a href="src/bluehive/types/provider_lookup_params.py">params</a>) -> <a href="./src/bluehive/types/provider_lookup_response.py">ProviderLookupResponse</a></code>

# Database

Types:

```python
from bluehive.types import DatabaseCheckHealthResponse
```

Methods:

- <code title="get /v1/database/health">client.database.<a href="./src/bluehive/resources/database.py">check_health</a>() -> <a href="./src/bluehive/types/database_check_health_response.py">DatabaseCheckHealthResponse</a></code>

# Fax

Types:

```python
from bluehive.types import FaxListProvidersResponse, FaxRetrieveStatusResponse, FaxSendResponse
```

Methods:

- <code title="get /v1/fax/providers">client.fax.<a href="./src/bluehive/resources/fax.py">list_providers</a>() -> <a href="./src/bluehive/types/fax_list_providers_response.py">FaxListProvidersResponse</a></code>
- <code title="get /v1/fax/status/{id}">client.fax.<a href="./src/bluehive/resources/fax.py">retrieve_status</a>(id) -> <a href="./src/bluehive/types/fax_retrieve_status_response.py">FaxRetrieveStatusResponse</a></code>
- <code title="post /v1/fax/send">client.fax.<a href="./src/bluehive/resources/fax.py">send</a>(\*\*<a href="src/bluehive/types/fax_send_params.py">params</a>) -> <a href="./src/bluehive/types/fax_send_response.py">FaxSendResponse</a></code>
