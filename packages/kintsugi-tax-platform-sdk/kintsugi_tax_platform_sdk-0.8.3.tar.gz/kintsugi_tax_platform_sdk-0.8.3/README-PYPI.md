# kintsugi-tax-platform-sdk

Developer-friendly & type-safe Python SDK specifically catered to leverage *kintsugi-tax-platform-sdk* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=kintsugi-tax-platform-sdk&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>


<br /><br />
> [!IMPORTANT]
> This SDK is not yet ready for production use. To complete setup please follow the steps outlined in your [workspace](https://app.speakeasy.com/org/kintsugi-ai/tax-platform). Delete this section before > publishing to a package manager.

<!-- Start Summary [summary] -->
## Summary


<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [kintsugi-tax-platform-sdk](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#kintsugi-tax-platform-sdk)
  * [SDK Installation](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#sdk-installation)
  * [IDE Support](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#ide-support)
  * [SDK Example Usage](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#sdk-example-usage)
  * [Authentication](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#authentication)
  * [Available Resources and Operations](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#available-resources-and-operations)
  * [File uploads](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#file-uploads)
  * [Retries](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#retries)
  * [Error Handling](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#error-handling)
  * [Server Selection](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#server-selection)
  * [Custom HTTP Client](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#custom-http-client)
  * [Resource Management](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#resource-management)
  * [Debugging](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#debugging)
* [Development](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#development)
  * [Maturity](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#maturity)
  * [Contributions](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#contributions)

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
uv add kintsugi-tax-platform-sdk
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install kintsugi-tax-platform-sdk
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add kintsugi-tax-platform-sdk
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from kintsugi-tax-platform-sdk python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "kintsugi-tax-platform-sdk",
# ]
# ///

from kintsugi_tax_platform_sdk import SDK

sdk = SDK(
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

### Example

```python
# Synchronous Example
from kintsugi_tax_platform_sdk import SDK, models


with SDK() as sdk:

    res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
        api_key_header="<YOUR_API_KEY_HERE>",
    ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from kintsugi_tax_platform_sdk import SDK, models

async def main():

    async with SDK() as sdk:

        res = await sdk.address_validation.search_async(security=models.SearchV1AddressValidationSearchPostSecurity(
            api_key_header="<YOUR_API_KEY_HERE>",
        ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security schemes globally:

| Name             | Type   | Scheme  |
| ---------------- | ------ | ------- |
| `api_key_header` | apiKey | API key |
| `custom_header`  | apiKey | API key |

You can set the security parameters through the `security` optional parameter when initializing the SDK client instance. The selected scheme will be used by default to authenticate with the API for all operations that support it. For example:
```python
from kintsugi_tax_platform_sdk import SDK, models


with SDK(
    security=models.Security(
        api_key_header="<YOUR_API_KEY_HERE>",
        custom_header="<YOUR_API_KEY_HERE>",
    ),
) as sdk:

    res = sdk.address_validation.suggestions(line1="1600 Amphitheatre Parkway", line2="", line3="", city="Mountain View", state="CA", country="US", postal_code="94043", id=215, county="", full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

    # Handle response
    print(res)

```

### Per-Operation Security Schemes

Some operations in this SDK require the security scheme to be specified at the request level. For example:
```python
from kintsugi_tax_platform_sdk import SDK, models


with SDK() as sdk:

    res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
        api_key_header="<YOUR_API_KEY_HERE>",
    ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [address_validation](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/addressvalidation/README.md)

* [search](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/addressvalidation/README.md#search) - Search
* [suggestions](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/addressvalidation/README.md#suggestions) - Suggestions

### [customers](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md)

* [list](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#list) - Get Customers
* [create](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#create) - Create Customer
* [get](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#get) - Get Customer By Id
* [update](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#update) - Update Customer
* [get_by_external_id](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#get_by_external_id) - Get Customer By External Id
* [get_transactions](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#get_transactions) - Get Transactions By Customer Id
* [create_transaction](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/customers/README.md#create_transaction) - Create Transaction By Customer Id

### [exemptions](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md)

* [list](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md#list) - Get Exemptions
* [create](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md#create) - Create Exemption
* [get](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md#get) - Get Exemption By Id
* [upload_certificate](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md#upload_certificate) - Upload Exemption Certificate
* [list_attachments](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/exemptions/README.md#list_attachments) - Get Attachments For Exemption

### [filings](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/filings/README.md)

* [get_all](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/filings/README.md#get_all) - Get Filings
* [get](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/filings/README.md#get) - Get Filing By Id
* [get_by_registration_id](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/filings/README.md#get_by_registration_id) - Get Filings By Registration Id

### [nexus](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md)

* [get_physical](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md#get_physical) - Get Physical Nexus
* [create_physical](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md#create_physical) - Create Physical Nexus
* [update_physical_nexus](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md#update_physical_nexus) - Update Physical Nexus
* [delete_physical_nexus](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md#delete_physical_nexus) - Delete Physical Nexus
* [get_all](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/nexus/README.md#get_all) - Get Nexus For Org

### [products](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md)

* [get](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md#get) - Get Products
* [create](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md#create) - Create Product
* [retrieve](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md#retrieve) - Get Product By Id
* [update](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md#update) - Update Product
* [get_categories](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/products/README.md#get_categories) - Get Product Categories

### [registrations](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md)

* [get_all](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md#get_all) - Get Registrations
* [create](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md#create) - Create Registration
* [get](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md#get) - Get Registration By Id
* [update](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md#update) - Update Registration
* [deregister](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/registrations/README.md#deregister) - Deregister Registration


### [tax_estimation](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/taxestimation/README.md)

* [estimate](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/taxestimation/README.md#estimate) - Estimate Tax

### [transactions](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md)

* [list](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#list) - Get Transactions
* [create](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#create) - Create Transaction
* [get_by_external_id](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#get_by_external_id) - Get Transaction By External Id
* [update](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#update) - Update Transaction
* [get_by_id](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#get_by_id) - Get Transaction By Id
* [get_by_filing_id](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#get_by_filing_id) - Get Transactions By Filing Id
* [create_credit_note](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#create_credit_note) - Create Credit Note By Transaction Id
* [update_credit_note](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/docs/sdks/transactions/README.md#update_credit_note) - Update Credit Note By Transaction Id

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
from kintsugi_tax_platform_sdk import SDK, models


with SDK(
    security=models.Security(
        api_key_header="<YOUR_API_KEY_HERE>",
        custom_header="<YOUR_API_KEY_HERE>",
    ),
) as sdk:

    res = sdk.exemptions.upload_certificate(exemption_id="<id>", file={
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
from kintsugi_tax_platform_sdk import SDK, models
from kintsugi_tax_platform_sdk.utils import BackoffStrategy, RetryConfig


with SDK() as sdk:

    res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
        api_key_header="<YOUR_API_KEY_HERE>",
    ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043",
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from kintsugi_tax_platform_sdk import SDK, models
from kintsugi_tax_platform_sdk.utils import BackoffStrategy, RetryConfig


with SDK(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
) as sdk:

    res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
        api_key_header="<YOUR_API_KEY_HERE>",
    ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`SDKError`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/sdkerror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#error-classes). |

### Example
```python
from kintsugi_tax_platform_sdk import SDK, errors, models


with SDK() as sdk:
    res = None
    try:

        res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
            api_key_header="<YOUR_API_KEY_HERE>",
        ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

        # Handle response
        print(res)


    except errors.SDKError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.ErrorResponse):
            print(e.data.detail)  # str
```

### Error Classes
**Primary error:**
* [`SDKError`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/sdkerror.py): The base class for HTTP error responses.

<details><summary>Less common errors (16)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`SDKError`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/sdkerror.py)**:
* [`ErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/errorresponse.py): Applicable to 32 of 41 methods.*
* [`HTTPValidationError`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/httpvalidationerror.py): Validation Error. Status code `422`. Applicable to 9 of 41 methods.*
* [`BackendSrcExemptionsResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcexemptionsresponsesvalidationerrorresponse.py): Validation issues, such as missing required fields or invalid field values. Status code `422`. Applicable to 5 of 41 methods.*
* [`BackendSrcRegistrationsResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcregistrationsresponsesvalidationerrorresponse.py): Validation error. Status code `422`. Applicable to 5 of 41 methods.*
* [`BackendSrcTransactionsResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrctransactionsresponsesvalidationerrorresponse.py): Status code `422`. Applicable to 5 of 41 methods.*
* [`BackendSrcNexusResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcnexusresponsesvalidationerrorresponse.py): Validation error. Status code `422`. Applicable to 4 of 41 methods.*
* [`BackendSrcProductsResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcproductsresponsesvalidationerrorresponse.py): Validation error. Status code `422`. Applicable to 4 of 41 methods.*
* [`BackendSrcCustomersResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrccustomersresponsesvalidationerrorresponse.py): Query parameters failed validation, such as an out-of-range page number. Status code `422`. Applicable to 3 of 41 methods.*
* [`BackendSrcFilingsResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcfilingsresponsesvalidationerrorresponse.py): Validation error. Status code `422`. Applicable to 3 of 41 methods.*
* [`BackendSrcAddressValidationResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrcaddressvalidationresponsesvalidationerrorresponse.py): Validation error - Address fields failed validation or are incomplete. Status code `422`. Applicable to 2 of 41 methods.*
* [`BackendSrcTaxEstimationResponsesValidationErrorResponse`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/backendsrctaxestimationresponsesvalidationerrorresponse.py): Validation Error. Status code `422`. Applicable to 1 of 41 methods.*
* [`ResponseValidationError`](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/./src/kintsugi_tax_platform_sdk/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](https://github.com/kintsugi-tax/kintsugi-tax-python-sdk/blob/master/#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from kintsugi_tax_platform_sdk import SDK, models


with SDK(
    server_url="https://api.trykintsugi.com",
) as sdk:

    res = sdk.address_validation.search(security=models.SearchV1AddressValidationSearchPostSecurity(
        api_key_header="<YOUR_API_KEY_HERE>",
    ), phone="555-123-4567", street_1="1600 Amphitheatre Parkway", street_2="Building 40", city="Mountain View", county="Santa Clara", state="CA", postal_code="94043", country=models.CountryCodeEnum.US, full_address="1600 Amphitheatre Parkway, Mountain View, CA 94043")

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
from kintsugi_tax_platform_sdk import SDK
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = SDK(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from kintsugi_tax_platform_sdk import SDK
from kintsugi_tax_platform_sdk.httpclient import AsyncHttpClient
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

s = SDK(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `SDK` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from kintsugi_tax_platform_sdk import SDK
def main():

    with SDK() as sdk:
        # Rest of application here...


# Or when using async:
async def amain():

    async with SDK() as sdk:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from kintsugi_tax_platform_sdk import SDK
import logging

logging.basicConfig(level=logging.DEBUG)
s = SDK(debug_logger=logging.getLogger("kintsugi_tax_platform_sdk"))
```
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

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=kintsugi-tax-platform-sdk&utm_campaign=python)
