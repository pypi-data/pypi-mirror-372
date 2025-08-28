# openapi

OpenApi dynamic producer for Akeyless

The payload for this producer looks like:

```
{"api_key": "ADMIN_API_KEY_HERE", "id": "ID_FOR_THE_ADMIN_API_KEY}
```

Call `clearskies_akeyless_custom_openapi.build_openapi_producer()` to initialize the create/revoke endpoints.  You can
optionally provide the `url` parameter which will add a prefix to the endpoints.  This can then be attached to a
[clearskies context](https://clearskies.info/docs/context/index.html) or an [endpoint group](https://clearskies.info/docs/endpoint-groups/endpoint-groups.html):

If used as a producer, it will use the provided credentials to fetch and return a temporary OpenApi admin key.  It can also be used as a rotator,
in which case it will generate a new admin key and revoke the old one.

## Installation

```
pip install clear-skies-akeyless-custom-openapi
```

## Usage Example

```python
import clearskies
import clearskies_akeyless_custom_openapi

wsgi = clearskies.contexts.WsgiRef(
    clearskies_akeyless_custom_openapi.build_openapi_producer()
)
wsgi()
```

Which you can test directly using calls like:

```
curl 'http://localhost:8080/sync/create' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'




curl 'http://localhost:8080/sync/revoke' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'

```

**NOTE:** Akeyless doesn't store your payload as JSON, even when you put in a JSON payload.  Instead, it ends up as a stringified-json
(hence the escaped apostrophes in the above example commands).  This is normal, and normally invisible to you, unless you try to invoke the
endpoints yourself.

## Development

To set up your development environment with pre-commit hooks:

```bash
# Install uv if not already installed
pip install uv

# Create a virtual environment and install all dependencies (including dev)
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Optionally, run pre-commit on all files
uv run pre-commit run --all-files
```
