
# Getting Started with Shell Card Management APIs

## Introduction

The Shell Card Management API provides secure and structured access to the Shell Card Platform, enabling integration with Shell’s internal systems for managing card-related resources.

This REST-based API uses the POST method for all operations—including retrieval, creation, update, and deletion of resources. It supports flexible search capabilities through JSON-encoded request bodies and returns JSON-formatted responses. Standard HTTP status codes are used to indicate the outcome of each request.

Authentication is handled via OAuth 2.0 using the Client Credentials flow. Access tokens must be included in the Authorization header of each request.

All resources are managed within the Shell Card Platform, which abstracts the complexity of backend systems. Some operations may be processed asynchronously, and clients should be prepared to handle delayed responses or polling mechanisms where applicable.

Go to the Shell Developer Portal: [https://developer.shell.com](https://developer.shell.com)

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install card-management-sdk==2.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/card-management-sdk/2.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands


pip install -r test-requirements.txt
pytest


## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| environment | `Environment` | The API environment. <br> **Default: `Environment.SIT`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| client_credentials_auth_credentials | [`ClientCredentialsAuthCredentials`](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/auth/oauth-2-client-credentials-grant.md) | The credential object for OAuth 2 Client Credentials Grant |

The API client can be initialized as follows:

```python
from shellcardmanagementapis.configuration import Environment
from shellcardmanagementapis.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from shellcardmanagementapis.shellcardmanagementapis_client import ShellcardmanagementapisClient

client = ShellcardmanagementapisClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id='OAuthClientId',
        o_auth_client_secret='OAuthClientSecret'
    ),
    environment=Environment.SIT
)
```

## Environments

The SDK can be configured to use a different environment for making API calls. Available environments are:

### Fields

| Name | Description |
|  --- | --- |
| SIT | **Default** |
| Production | - |

## Authorization

This API uses the following authentication schemes.

* [`BearerToken (OAuth 2 Client Credentials Grant)`](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/auth/oauth-2-client-credentials-grant.md)

## List of APIs

* [Customer](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/controllers/customer.md)
* [Restriction](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/controllers/restriction.md)
* [Card](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/controllers/card.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/sdks-io/card-management-python-sdk/tree/2.0.0/doc/unix-date-time.md)

