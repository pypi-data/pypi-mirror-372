# Memory

## DrmInstances

Types:

```python
from entities_python.types.memory import (
    DrmInstance,
    DrmInstanceListResponse,
    DrmInstanceGetMemoryContextResponse,
    DrmInstanceGetMessagesResponse,
    DrmInstanceLogMessagesResponse,
)
```

Methods:

- <code title="post /api/memory/drm-instances/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">create</a>(\*\*<a href="src/entities_python/types/memory/drm_instance_create_params.py">params</a>) -> <a href="./src/entities_python/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="get /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">retrieve</a>(id) -> <a href="./src/entities_python/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="put /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">update</a>(id, \*\*<a href="src/entities_python/types/memory/drm_instance_update_params.py">params</a>) -> <a href="./src/entities_python/types/memory/drm_instance.py">DrmInstance</a></code>
- <code title="get /api/memory/drm-instances/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">list</a>() -> <a href="./src/entities_python/types/memory/drm_instance_list_response.py">DrmInstanceListResponse</a></code>
- <code title="delete /api/memory/drm-instances/{id}/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">delete</a>(id) -> None</code>
- <code title="get /api/memory/drm-instances/{id}/memory-context/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">get_memory_context</a>(id) -> <a href="./src/entities_python/types/memory/drm_instance_get_memory_context_response.py">DrmInstanceGetMemoryContextResponse</a></code>
- <code title="get /api/memory/drm-instances/{id}/messages/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">get_messages</a>(id) -> <a href="./src/entities_python/types/memory/drm_instance_get_messages_response.py">DrmInstanceGetMessagesResponse</a></code>
- <code title="post /api/memory/drm-instances/{id}/log-messages/">client.memory.drm_instances.<a href="./src/entities_python/resources/memory/drm_instances.py">log_messages</a>(id, \*\*<a href="src/entities_python/types/memory/drm_instance_log_messages_params.py">params</a>) -> <a href="./src/entities_python/types/memory/drm_instance_log_messages_response.py">DrmInstanceLogMessagesResponse</a></code>

# Orgs

## APIKeys

Types:

```python
from entities_python.types.orgs import APIKey, APIKeyListResponse
```

Methods:

- <code title="post /api/orgs/api-keys/">client.orgs.api_keys.<a href="./src/entities_python/resources/orgs/api_keys.py">create</a>(\*\*<a href="src/entities_python/types/orgs/api_key_create_params.py">params</a>) -> <a href="./src/entities_python/types/orgs/api_key.py">APIKey</a></code>
- <code title="get /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities_python/resources/orgs/api_keys.py">retrieve</a>(id) -> <a href="./src/entities_python/types/orgs/api_key.py">APIKey</a></code>
- <code title="put /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities_python/resources/orgs/api_keys.py">update</a>(id, \*\*<a href="src/entities_python/types/orgs/api_key_update_params.py">params</a>) -> <a href="./src/entities_python/types/orgs/api_key.py">APIKey</a></code>
- <code title="get /api/orgs/api-keys/">client.orgs.api_keys.<a href="./src/entities_python/resources/orgs/api_keys.py">list</a>() -> <a href="./src/entities_python/types/orgs/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /api/orgs/api-keys/{id}/">client.orgs.api_keys.<a href="./src/entities_python/resources/orgs/api_keys.py">delete</a>(id) -> None</code>

## Organizations

Types:

```python
from entities_python.types.orgs import Organization, OrganizationListResponse
```

Methods:

- <code title="post /api/orgs/organizations/">client.orgs.organizations.<a href="./src/entities_python/resources/orgs/organizations.py">create</a>(\*\*<a href="src/entities_python/types/orgs/organization_create_params.py">params</a>) -> <a href="./src/entities_python/types/orgs/organization.py">Organization</a></code>
- <code title="get /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities_python/resources/orgs/organizations.py">retrieve</a>(id) -> <a href="./src/entities_python/types/orgs/organization.py">Organization</a></code>
- <code title="put /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities_python/resources/orgs/organizations.py">update</a>(id, \*\*<a href="src/entities_python/types/orgs/organization_update_params.py">params</a>) -> <a href="./src/entities_python/types/orgs/organization.py">Organization</a></code>
- <code title="get /api/orgs/organizations/">client.orgs.organizations.<a href="./src/entities_python/resources/orgs/organizations.py">list</a>() -> <a href="./src/entities_python/types/orgs/organization_list_response.py">OrganizationListResponse</a></code>
- <code title="delete /api/orgs/organizations/{id}/">client.orgs.organizations.<a href="./src/entities_python/resources/orgs/organizations.py">delete</a>(id) -> None</code>

# Toolbox

## Adapters

Types:

```python
from entities_python.types.toolbox import Adapter, AdapterListResponse
```

Methods:

- <code title="post /api/toolbox/adapters/">client.toolbox.adapters.<a href="./src/entities_python/resources/toolbox/adapters.py">create</a>(\*\*<a href="src/entities_python/types/toolbox/adapter_create_params.py">params</a>) -> <a href="./src/entities_python/types/toolbox/adapter.py">Adapter</a></code>
- <code title="get /api/toolbox/adapters/{id}/">client.toolbox.adapters.<a href="./src/entities_python/resources/toolbox/adapters.py">retrieve</a>(id) -> <a href="./src/entities_python/types/toolbox/adapter.py">Adapter</a></code>
- <code title="put /api/toolbox/adapters/{id}/">client.toolbox.adapters.<a href="./src/entities_python/resources/toolbox/adapters.py">update</a>(id, \*\*<a href="src/entities_python/types/toolbox/adapter_update_params.py">params</a>) -> <a href="./src/entities_python/types/toolbox/adapter.py">Adapter</a></code>
- <code title="get /api/toolbox/adapters/">client.toolbox.adapters.<a href="./src/entities_python/resources/toolbox/adapters.py">list</a>() -> <a href="./src/entities_python/types/toolbox/adapter_list_response.py">AdapterListResponse</a></code>
- <code title="delete /api/toolbox/adapters/{id}/">client.toolbox.adapters.<a href="./src/entities_python/resources/toolbox/adapters.py">delete</a>(id) -> None</code>

## Tools

Types:

```python
from entities_python.types.toolbox import Tool, ToolListResponse
```

Methods:

- <code title="post /api/toolbox/tools/">client.toolbox.tools.<a href="./src/entities_python/resources/toolbox/tools.py">create</a>(\*\*<a href="src/entities_python/types/toolbox/tool_create_params.py">params</a>) -> <a href="./src/entities_python/types/toolbox/tool.py">Tool</a></code>
- <code title="get /api/toolbox/tools/{id}/">client.toolbox.tools.<a href="./src/entities_python/resources/toolbox/tools.py">retrieve</a>(id) -> <a href="./src/entities_python/types/toolbox/tool.py">Tool</a></code>
- <code title="put /api/toolbox/tools/{id}/">client.toolbox.tools.<a href="./src/entities_python/resources/toolbox/tools.py">update</a>(id, \*\*<a href="src/entities_python/types/toolbox/tool_update_params.py">params</a>) -> <a href="./src/entities_python/types/toolbox/tool.py">Tool</a></code>
- <code title="get /api/toolbox/tools/">client.toolbox.tools.<a href="./src/entities_python/resources/toolbox/tools.py">list</a>() -> <a href="./src/entities_python/types/toolbox/tool_list_response.py">ToolListResponse</a></code>
- <code title="delete /api/toolbox/tools/{id}/">client.toolbox.tools.<a href="./src/entities_python/resources/toolbox/tools.py">delete</a>(id) -> None</code>

# Cloud

## Runtimes

Types:

```python
from entities_python.types.cloud import Runtime, StatusEnum, RuntimeListResponse
```

Methods:

- <code title="post /api/cloud/runtimes/">client.cloud.runtimes.<a href="./src/entities_python/resources/cloud/runtimes.py">create</a>(\*\*<a href="src/entities_python/types/cloud/runtime_create_params.py">params</a>) -> <a href="./src/entities_python/types/cloud/runtime.py">Runtime</a></code>
- <code title="get /api/cloud/runtimes/{id}/">client.cloud.runtimes.<a href="./src/entities_python/resources/cloud/runtimes.py">retrieve</a>(id) -> <a href="./src/entities_python/types/cloud/runtime.py">Runtime</a></code>
- <code title="patch /api/cloud/runtimes/{id}/">client.cloud.runtimes.<a href="./src/entities_python/resources/cloud/runtimes.py">update</a>(id, \*\*<a href="src/entities_python/types/cloud/runtime_update_params.py">params</a>) -> <a href="./src/entities_python/types/cloud/runtime.py">Runtime</a></code>
- <code title="get /api/cloud/runtimes/">client.cloud.runtimes.<a href="./src/entities_python/resources/cloud/runtimes.py">list</a>() -> <a href="./src/entities_python/types/cloud/runtime_list_response.py">RuntimeListResponse</a></code>
- <code title="delete /api/cloud/runtimes/{id}/">client.cloud.runtimes.<a href="./src/entities_python/resources/cloud/runtimes.py">delete</a>(id) -> None</code>

## Identities

Types:

```python
from entities_python.types.cloud import Identity, IdentityListResponse
```

Methods:

- <code title="post /api/cloud/identities/">client.cloud.identities.<a href="./src/entities_python/resources/cloud/identities.py">create</a>(\*\*<a href="src/entities_python/types/cloud/identity_create_params.py">params</a>) -> <a href="./src/entities_python/types/cloud/identity.py">Identity</a></code>
- <code title="get /api/cloud/identities/{id}/">client.cloud.identities.<a href="./src/entities_python/resources/cloud/identities.py">retrieve</a>(id) -> <a href="./src/entities_python/types/cloud/identity.py">Identity</a></code>
- <code title="put /api/cloud/identities/{id}/">client.cloud.identities.<a href="./src/entities_python/resources/cloud/identities.py">update</a>(id, \*\*<a href="src/entities_python/types/cloud/identity_update_params.py">params</a>) -> <a href="./src/entities_python/types/cloud/identity.py">Identity</a></code>
- <code title="get /api/cloud/identities/">client.cloud.identities.<a href="./src/entities_python/resources/cloud/identities.py">list</a>() -> <a href="./src/entities_python/types/cloud/identity_list_response.py">IdentityListResponse</a></code>
- <code title="delete /api/cloud/identities/{id}/">client.cloud.identities.<a href="./src/entities_python/resources/cloud/identities.py">delete</a>(id) -> None</code>
