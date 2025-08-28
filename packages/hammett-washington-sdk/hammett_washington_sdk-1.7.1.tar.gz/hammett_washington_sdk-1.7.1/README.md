
# Getting Started with APIMATIC Calculator

## Introduction

Simple calculator API hosted on APIMATIC

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install hammett-washington-sdk==1.7.1
```

You can also view the package at:
https://pypi.python.org/pypi/hammett-washington-sdk/1.7.1

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands


pip install -r test-requirements.txt
pytest


## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| environment | `Environment` | The API environment. <br> **Default: `Environment.PRODUCTION`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |

The API client can be initialized as follows:

```python
from apimaticcalculator.apimaticcalculator_client import ApimaticcalculatorClient
from apimaticcalculator.configuration import Environment

client = ApimaticcalculatorClient(
    environment=Environment.PRODUCTION
)
```

## List of APIs

* [Simple Calculator](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/controllers/simple-calculator.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/http-response.md)
* [HttpRequest](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/ZahraN444/hammett-washington-python-sdk/tree/1.7.1/doc/unix-date-time.md)

