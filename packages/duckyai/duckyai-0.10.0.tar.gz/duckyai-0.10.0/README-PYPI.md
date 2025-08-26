# duckyai

Developer-friendly & type-safe Python SDK specifically catered to leverage *duckyai* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=duckyai&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<br /><br />
🌐 Links

[🔗 Ducky Website](https://ducky.ai/)

[📘 API Documentation](https://docs.ducky.ai/docs/getting-started#/)


<br /><br />
> [!IMPORTANT]
> This SDK is not yet ready for production use. To complete setup please follow the steps outlined in your [workspace](https://app.speakeasy.com/org/ducky/feather-backend). Delete this section before > publishing to a package manager.

<!-- Start Summary [summary] -->
## Summary

Ducky API: API for managing and retrieving data from Ducky.
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [duckyai](https://github.com/lycoai/duckyai-python/blob/master/#duckyai)
  * [SDK Installation](https://github.com/lycoai/duckyai-python/blob/master/#sdk-installation)
  * [IDE Support](https://github.com/lycoai/duckyai-python/blob/master/#ide-support)
  * [SDK Example Usage](https://github.com/lycoai/duckyai-python/blob/master/#sdk-example-usage)
  * [Authentication](https://github.com/lycoai/duckyai-python/blob/master/#authentication)
  * [Available Resources and Operations](https://github.com/lycoai/duckyai-python/blob/master/#available-resources-and-operations)
  * [File uploads](https://github.com/lycoai/duckyai-python/blob/master/#file-uploads)
  * [Retries](https://github.com/lycoai/duckyai-python/blob/master/#retries)
  * [Error Handling](https://github.com/lycoai/duckyai-python/blob/master/#error-handling)
  * [Server Selection](https://github.com/lycoai/duckyai-python/blob/master/#server-selection)
  * [Custom HTTP Client](https://github.com/lycoai/duckyai-python/blob/master/#custom-http-client)
  * [Resource Management](https://github.com/lycoai/duckyai-python/blob/master/#resource-management)
  * [Debugging](https://github.com/lycoai/duckyai-python/blob/master/#debugging)
* [Development](https://github.com/lycoai/duckyai-python/blob/master/#development)
  * [Maturity](https://github.com/lycoai/duckyai-python/blob/master/#maturity)
  * [Contributions](https://github.com/lycoai/duckyai-python/blob/master/#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add duckyai
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install duckyai
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add duckyai
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from duckyai python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "duckyai",
# ]
# ///

from duckyai import DuckyAI

sdk = DuckyAI(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example 1

```python
# Synchronous Example
from duckyai import DuckyAI
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.index_file(index_name="<value>", file={
        "file_name": "example.file",
        "content": open("example.file", "rb"),
    })

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from duckyai import DuckyAI
import os

async def main():

    async with DuckyAI(
        api_key=os.getenv("DUCKYAI_API_KEY", ""),
    ) as ducky_ai:

        res = await ducky_ai.documents.index_file_async(index_name="<value>", file={
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        })

        # Handle response
        print(res)

asyncio.run(main())
```

### Example 2

```python
# Synchronous Example
from duckyai import DuckyAI
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.index_multimodal(index_name="index_name", doc_id="doc_id", image={
        "url": "https://openapi-generator.tech",
        "base64": "base64",
        "mime_type": "mime_type",
    }, content="content", title="title", url="url", metadata={
        "key": "",
    })

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from duckyai import DuckyAI
import os

async def main():

    async with DuckyAI(
        api_key=os.getenv("DUCKYAI_API_KEY", ""),
    ) as ducky_ai:

        res = await ducky_ai.documents.index_multimodal_async(index_name="index_name", doc_id="doc_id", image={
            "url": "https://openapi-generator.tech",
            "base64": "base64",
            "mime_type": "mime_type",
        }, content="content", title="title", url="url", metadata={
            "key": "",
        })

        # Handle response
        print(res)

asyncio.run(main())
```

### Example 3

```python
# Synchronous Example
from duckyai import DuckyAI
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.index(index_name="index_name", content="content", doc_id="doc_id", title="title", url="url", file_id="file_id", metadata={
        "key": "",
    })

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from duckyai import DuckyAI
import os

async def main():

    async with DuckyAI(
        api_key=os.getenv("DUCKYAI_API_KEY", ""),
    ) as ducky_ai:

        res = await ducky_ai.documents.index_async(index_name="index_name", content="content", doc_id="doc_id", title="title", url="url", file_id="file_id", metadata={
            "key": "",
        })

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name      | Type   | Scheme  | Environment Variable |
| --------- | ------ | ------- | -------------------- |
| `api_key` | apiKey | API key | `DUCKYAI_API_KEY`    |

To authenticate with the API the `api_key` parameter must be set when initializing the SDK client instance. For example:
```python
from duckyai import DuckyAI
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.list(index_name="<value>")

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [documents](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md)

* [list](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#list) - List documents within an index
* [batch_index](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#batch_index) - Batch index text documents
* [index_file](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#index_file) - Index a document by uploading a file
* [index_multimodal](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#index_multimodal) - Index a document from an image and text content
* [index](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#index) - Index a document from text content
* [retrieve](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#retrieve) - Retrieve documents from an index
* [delete](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#delete) - Delete a document
* [get](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/documents/README.md#get) - Get a document by ID with pagination


### [indexes](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md)

* [list](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md#list) - List indexes within a project
* [create](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md#create) - Create an index
* [delete](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md#delete) - Delete an index
* [get](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md#get) - Get an index
* [ask](https://github.com/lycoai/duckyai-python/blob/master/docs/sdks/indexes/README.md#ask) - Ask a question to an index

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start File uploads [file-upload] -->
## File uploads

Certain SDK methods accept file objects as part of a request body or multi-part request. It is possible and typically recommended to upload files as a stream rather than reading the entire contents into memory. This avoids excessive memory consumption and potentially crashing with out-of-memory errors when working with very large files. The following example demonstrates how to attach a file stream to a request.

> [!TIP]
>
> For endpoints that handle file uploads bytes arrays can also be used. However, using streams is recommended for large files.
>

```python
from duckyai import DuckyAI
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.index_file(index_name="<value>", file={
        "file_name": "example.file",
        "content": open("example.file", "rb"),
    })

    # Handle response
    print(res)

```
<!-- End File uploads [file-upload] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from duckyai import DuckyAI
from duckyai.utils import BackoffStrategy, RetryConfig
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.list(index_name="<value>",
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from duckyai import DuckyAI
from duckyai.utils import BackoffStrategy, RetryConfig
import os


with DuckyAI(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.list(index_name="<value>")

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`DuckyAiError`](https://github.com/lycoai/duckyai-python/blob/master/./src/duckyai/models/duckyaierror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](https://github.com/lycoai/duckyai-python/blob/master/#error-classes). |

### Example
```python
from duckyai import DuckyAI, models
import os


with DuckyAI(
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:
    res = None
    try:

        res = ducky_ai.documents.list(index_name="<value>")

        # Handle response
        print(res)


    except models.DuckyAiError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, models.ErrorResponse):
            print(e.data.error)  # Optional[str]
```

### Error Classes
**Primary errors:**
* [`DuckyAiError`](https://github.com/lycoai/duckyai-python/blob/master/./src/duckyai/models/duckyaierror.py): The base class for HTTP error responses.
  * [`ErrorResponse`](https://github.com/lycoai/duckyai-python/blob/master/./src/duckyai/models/errorresponse.py): Generic error.

<details><summary>Less common errors (5)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`DuckyAiError`](https://github.com/lycoai/duckyai-python/blob/master/./src/duckyai/models/duckyaierror.py)**:
* [`ResponseValidationError`](https://github.com/lycoai/duckyai-python/blob/master/./src/duckyai/models/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from duckyai import DuckyAI
import os


with DuckyAI(
    server_url="https://api.ducky.ai",
    api_key=os.getenv("DUCKYAI_API_KEY", ""),
) as ducky_ai:

    res = ducky_ai.documents.list(index_name="<value>")

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from duckyai import DuckyAI
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = DuckyAI(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from duckyai import DuckyAI
from duckyai.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = DuckyAI(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `DuckyAI` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from duckyai import DuckyAI
import os
def main():

    with DuckyAI(
        api_key=os.getenv("DUCKYAI_API_KEY", ""),
    ) as ducky_ai:
        # Rest of application here...


# Or when using async:
async def amain():

    async with DuckyAI(
        api_key=os.getenv("DUCKYAI_API_KEY", ""),
    ) as ducky_ai:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from duckyai import DuckyAI
import logging

logging.basicConfig(level=logging.DEBUG)
s = DuckyAI(debug_logger=logging.getLogger("duckyai"))
```

You can also enable a default debug logger by setting an environment variable `DUCKYAI_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=duckyai&utm_campaign=python)
