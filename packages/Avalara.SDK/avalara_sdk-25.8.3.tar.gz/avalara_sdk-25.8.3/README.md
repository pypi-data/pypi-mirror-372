# Avalara.SDK - the Unified Java SDK for next gen Avalara services.

Unified SDK consists of services on top of which the Avalara Compliance Cloud platform is built. These services are foundational and provide functionality such as einvoicing.

## Requirements.

Python >= 3.6

## Installation & Usage

### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install Avalara.SDK==24.12.1
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```

### Running SDK unit tests

```sh
pip install -r test-requirements.txt
pytest
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import time
from Avalara.SDK.configuration import Configuration
from Avalara.SDK.api_client import ApiClient
from Avalara.SDK.exceptions import ApiException
from Avalara.SDK.api.EInvoicing.V1.mandates_api import MandatesApi  # noqa: E501
from pprint import pprint

# Define configuration object with parameters specified to your application.
configuration = Configuration(
    app_name='test app',
    app_version='1.0',
    machine_name='some machine',
    access_token='',
    environment='sandbox'
)
# Enter a context with an instance of the API client
with ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = MandatesApi(api_client)
    x_avalara_client = "Swagger UI; 22.7.0; Custom; 1.0" # str | Identifies the software you are using to call this API.  For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) . (optional) if omitted the server will use the default value of "Swagger UI; 22.7.0; Custom; 1.0"

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Retrieve geolocation information for a specified address
        api_response = api_instance.get_mandates(avalara_version="1.2", x_avalara_client=x_avalara_client)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling MandatesApi->get_mandates: %s\n" % e)
```

## Documentation for API Endpoints

<a name="documentation-for-EInvoicing-V1-api-endpoints"></a>

### EInvoicing V1 API Documentation

| Class                | Method                                                                                                    | HTTP request                                                    | Description                                                                                             |
| -------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| _DataInputFieldsApi_ | [**get_data_input_fields**](docs/EInvoicing/V1/DataInputFieldsApi.md#get_data_input_fields)               | **GET** /data-input-fields                                      | Returns the optionality of document fields for different country mandates                               |
| _DocumentsApi_       | [**download_document**](docs/EInvoicing/V1/DocumentsApi.md#download_document)                             | **GET** /documents/{documentId}/$download                       | Returns a copy of the document                                                                          |
| _DocumentsApi_       | [**fetch_documents**](docs/EInvoicing/V1/DocumentsApi.md#fetch_documents)                                 | **POST** /documents/$fetch                                      | Fetch the inbound document from a tax authority                                                         |
| _DocumentsApi_       | [**get_document_list**](docs/EInvoicing/V1/DocumentsApi.md#get_document_list)                             | **GET** /documents                                              | Returns a summary of documents for a date range                                                         |
| _DocumentsApi_       | [**get_document_status**](docs/EInvoicing/V1/DocumentsApi.md#get_document_status)                         | **GET** /documents/{documentId}/status                          | Checks the status of a document                                                                         |
| _DocumentsApi_       | [**submit_document**](docs/EInvoicing/V1/DocumentsApi.md#submit_document)                                 | **POST** /documents                                             | Submits a document to Avalara E-Invoicing API                                                           |
| _InteropApi_         | [**submit_interop_document**](docs/EInvoicing/V1/InteropApi.md#submit_interop_document)                   | **POST** /interop/documents                                     | Submit a document                                                                                       |
| _MandatesApi_        | [**get_mandate_data_input_fields**](docs/EInvoicing/V1/MandatesApi.md#get_mandate_data_input_fields)      | **GET** /mandates/{mandateId}/data-input-fields                 | Returns document field information for a country mandate, a selected document type, and its version     |
| _MandatesApi_        | [**get_mandates**](docs/EInvoicing/V1/MandatesApi.md#get_mandates)                                        | **GET** /mandates                                               | List country mandates that are supported by the Avalara E-Invoicing platform                            |
| _TradingPartnersApi_ | [**batch_search_participants**](docs/EInvoicing/V1/TradingPartnersApi.md#batch_search_participants)       | **POST** /trading-partners/batch-searches                       | Creates a batch search and performs a batch search in the directory for participants in the background. |
| _TradingPartnersApi_ | [**download_batch_search_report**](docs/EInvoicing/V1/TradingPartnersApi.md#download_batch_search_report) | **GET** /trading-partners/batch-searches/{id}/$download-results | Download batch search results in a csv file.                                                            |
| _TradingPartnersApi_ | [**get_batch_search_detail**](docs/EInvoicing/V1/TradingPartnersApi.md#get_batch_search_detail)           | **GET** /trading-partners/batch-searches/{id}                   | Get the batch search details for a given id.                                                            |
| _TradingPartnersApi_ | [**list_batch_searches**](docs/EInvoicing/V1/TradingPartnersApi.md#list_batch_searches)                   | **GET** /trading-partners/batch-searches                        | List all batch searches that were previously submitted.                                                 |
| _TradingPartnersApi_ | [**search_participants**](docs/EInvoicing/V1/TradingPartnersApi.md#search_participants)                   | **GET** /trading-partners                                       | Returns a list of participants matching the input query.                                                |

<a name="documentation-for-models"></a>

## Documentation for Models

<a name="documentation-for-EInvoicing-V1-models"></a>

### EInvoicing V1 Model Documentation

- [Avalara.SDK.models.EInvoicing.V1.BadDownloadRequest](docs/EInvoicing/V1/BadDownloadRequest.md)
- [Avalara.SDK.models.EInvoicing.V1.BadRequest](docs/EInvoicing/V1/BadRequest.md)
- [Avalara.SDK.models.EInvoicing.V1.BatchSearch](docs/EInvoicing/V1/BatchSearch.md)
- [Avalara.SDK.models.EInvoicing.V1.BatchSearchListResponse](docs/EInvoicing/V1/BatchSearchListResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.ConditionalForField](docs/EInvoicing/V1/ConditionalForField.md)
- [Avalara.SDK.models.EInvoicing.V1.DataInputField](docs/EInvoicing/V1/DataInputField.md)
- [Avalara.SDK.models.EInvoicing.V1.DataInputFieldNotUsedFor](docs/EInvoicing/V1/DataInputFieldNotUsedFor.md)
- [Avalara.SDK.models.EInvoicing.V1.DataInputFieldOptionalFor](docs/EInvoicing/V1/DataInputFieldOptionalFor.md)
- [Avalara.SDK.models.EInvoicing.V1.DataInputFieldRequiredFor](docs/EInvoicing/V1/DataInputFieldRequiredFor.md)
- [Avalara.SDK.models.EInvoicing.V1.DataInputFieldsResponse](docs/EInvoicing/V1/DataInputFieldsResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.DirectorySearchResponse](docs/EInvoicing/V1/DirectorySearchResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.DirectorySearchResponseValueInner](docs/EInvoicing/V1/DirectorySearchResponseValueInner.md)
- [Avalara.SDK.models.EInvoicing.V1.DirectorySearchResponseValueInnerAddressesInner](docs/EInvoicing/V1/DirectorySearchResponseValueInnerAddressesInner.md)
- [Avalara.SDK.models.EInvoicing.V1.DirectorySearchResponseValueInnerIdentifiersInner](docs/EInvoicing/V1/DirectorySearchResponseValueInnerIdentifiersInner.md)
- [Avalara.SDK.models.EInvoicing.V1.DirectorySearchResponseValueInnerSupportedDocumentTypesInner](docs/EInvoicing/V1/DirectorySearchResponseValueInnerSupportedDocumentTypesInner.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentFetch](docs/EInvoicing/V1/DocumentFetch.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentFetchRequest](docs/EInvoicing/V1/DocumentFetchRequest.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentFetchRequestDataInner](docs/EInvoicing/V1/DocumentFetchRequestDataInner.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentFetchRequestMetadata](docs/EInvoicing/V1/DocumentFetchRequestMetadata.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentListResponse](docs/EInvoicing/V1/DocumentListResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentStatusResponse](docs/EInvoicing/V1/DocumentStatusResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentSubmissionError](docs/EInvoicing/V1/DocumentSubmissionError.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentSubmitResponse](docs/EInvoicing/V1/DocumentSubmitResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.DocumentSummary](docs/EInvoicing/V1/DocumentSummary.md)
- [Avalara.SDK.models.EInvoicing.V1.ErrorResponse](docs/EInvoicing/V1/ErrorResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.ForbiddenError](docs/EInvoicing/V1/ForbiddenError.md)
- [Avalara.SDK.models.EInvoicing.V1.InputDataFormats](docs/EInvoicing/V1/InputDataFormats.md)
- [Avalara.SDK.models.EInvoicing.V1.InternalServerError](docs/EInvoicing/V1/InternalServerError.md)
- [Avalara.SDK.models.EInvoicing.V1.Mandate](docs/EInvoicing/V1/Mandate.md)
- [Avalara.SDK.models.EInvoicing.V1.MandateDataInputField](docs/EInvoicing/V1/MandateDataInputField.md)
- [Avalara.SDK.models.EInvoicing.V1.MandateDataInputFieldNamespace](docs/EInvoicing/V1/MandateDataInputFieldNamespace.md)
- [Avalara.SDK.models.EInvoicing.V1.MandatesResponse](docs/EInvoicing/V1/MandatesResponse.md)
- [Avalara.SDK.models.EInvoicing.V1.NotFoundError](docs/EInvoicing/V1/NotFoundError.md)
- [Avalara.SDK.models.EInvoicing.V1.NotUsedForField](docs/EInvoicing/V1/NotUsedForField.md)
- [Avalara.SDK.models.EInvoicing.V1.RequiredWhenField](docs/EInvoicing/V1/RequiredWhenField.md)
- [Avalara.SDK.models.EInvoicing.V1.StatusEvent](docs/EInvoicing/V1/StatusEvent.md)
- [Avalara.SDK.models.EInvoicing.V1.SubmitDocumentMetadata](docs/EInvoicing/V1/SubmitDocumentMetadata.md)
- [Avalara.SDK.models.EInvoicing.V1.SubmitInteropDocument202Response](docs/EInvoicing/V1/SubmitInteropDocument202Response.md)
- [Avalara.SDK.models.EInvoicing.V1.WorkflowIds](docs/EInvoicing/V1/WorkflowIds.md)
<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

<a name="documentation-for-EInvoicing-V1-api-endpoints"></a>
### EInvoicing V1 API Documentation

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*DataInputFieldsApi* | [**get_data_input_fields**](docs/EInvoicing/V1/DataInputFieldsApi.md#get_data_input_fields) | **GET** /data-input-fields | Returns the optionality of document fields for different country mandates
*DocumentsApi* | [**download_document**](docs/EInvoicing/V1/DocumentsApi.md#download_document) | **GET** /documents/{documentId}/$download | Returns a copy of the document
*DocumentsApi* | [**fetch_documents**](docs/EInvoicing/V1/DocumentsApi.md#fetch_documents) | **POST** /documents/$fetch | Fetch the inbound document from a tax authority
*DocumentsApi* | [**get_document_list**](docs/EInvoicing/V1/DocumentsApi.md#get_document_list) | **GET** /documents | Returns a summary of documents for a date range
*DocumentsApi* | [**get_document_status**](docs/EInvoicing/V1/DocumentsApi.md#get_document_status) | **GET** /documents/{documentId}/status | Checks the status of a document
*DocumentsApi* | [**submit_document**](docs/EInvoicing/V1/DocumentsApi.md#submit_document) | **POST** /documents | Submits a document to Avalara E-Invoicing API
*InteropApi* | [**submit_interop_document**](docs/EInvoicing/V1/InteropApi.md#submit_interop_document) | **POST** /interop/documents | Submit a document
*MandatesApi* | [**get_mandate_data_input_fields**](docs/EInvoicing/V1/MandatesApi.md#get_mandate_data_input_fields) | **GET** /mandates/{mandateId}/data-input-fields | Returns document field information for a country mandate, a selected document type, and its version
*MandatesApi* | [**get_mandates**](docs/EInvoicing/V1/MandatesApi.md#get_mandates) | **GET** /mandates | List country mandates that are supported by the Avalara E-Invoicing platform
*SubscriptionsApi* | [**create_webhook_subscription**](docs/EInvoicing/V1/SubscriptionsApi.md#create_webhook_subscription) | **POST** /webhooks/subscriptions | Create a subscription to events
*SubscriptionsApi* | [**delete_webhook_subscription**](docs/EInvoicing/V1/SubscriptionsApi.md#delete_webhook_subscription) | **DELETE** /webhooks/subscriptions/{subscription-id} | Unsubscribe from events
*SubscriptionsApi* | [**get_webhook_subscription**](docs/EInvoicing/V1/SubscriptionsApi.md#get_webhook_subscription) | **GET** /webhooks/subscriptions/{subscription-id} | Get details of a subscription
*SubscriptionsApi* | [**list_webhook_subscriptions**](docs/EInvoicing/V1/SubscriptionsApi.md#list_webhook_subscriptions) | **GET** /webhooks/subscriptions | List all subscriptions
*TaxIdentifiersApi* | [**tax_identifier_schema_by_country**](docs/EInvoicing/V1/TaxIdentifiersApi.md#tax_identifier_schema_by_country) | **GET** /tax-identifiers/schema | Returns the tax identifier request & response schema for a specific country.
*TaxIdentifiersApi* | [**validate_tax_identifier**](docs/EInvoicing/V1/TaxIdentifiersApi.md#validate_tax_identifier) | **POST** /tax-identifiers/validate | Validates a tax identifier.
*TradingPartnersApi* | [**batch_search_participants**](docs/EInvoicing/V1/TradingPartnersApi.md#batch_search_participants) | **POST** /trading-partners/batch-searches | Handles batch search requests by uploading a file containing search parameters.
*TradingPartnersApi* | [**create_trading_partner**](docs/EInvoicing/V1/TradingPartnersApi.md#create_trading_partner) | **POST** /trading-partners | Creates a new trading partner.
*TradingPartnersApi* | [**create_trading_partners_batch**](docs/EInvoicing/V1/TradingPartnersApi.md#create_trading_partners_batch) | **POST** /trading-partners/batch | Creates a batch of multiple trading partners.
*TradingPartnersApi* | [**delete_trading_partner**](docs/EInvoicing/V1/TradingPartnersApi.md#delete_trading_partner) | **DELETE** /trading-partners/{id} | Deletes a trading partner using ID.
*TradingPartnersApi* | [**download_batch_search_report**](docs/EInvoicing/V1/TradingPartnersApi.md#download_batch_search_report) | **GET** /trading-partners/batch-searches/{id}/$download-results | Downloads batch search results in a csv file.
*TradingPartnersApi* | [**get_batch_search_detail**](docs/EInvoicing/V1/TradingPartnersApi.md#get_batch_search_detail) | **GET** /trading-partners/batch-searches/{id} | Returns the batch search details using ID.
*TradingPartnersApi* | [**list_batch_searches**](docs/EInvoicing/V1/TradingPartnersApi.md#list_batch_searches) | **GET** /trading-partners/batch-searches | Lists all batch searches that were previously submitted.
*TradingPartnersApi* | [**search_participants**](docs/EInvoicing/V1/TradingPartnersApi.md#search_participants) | **GET** /trading-partners | Returns a list of participants matching the input query.
*TradingPartnersApi* | [**update_trading_partner**](docs/EInvoicing/V1/TradingPartnersApi.md#update_trading_partner) | **PUT** /trading-partners/{id} | Updates a trading partner using ID.

<a name="documentation-for-A1099-V2-api-endpoints"></a>
### A1099 V2 API Documentation

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*CompaniesW9Api* | [**create_company**](docs/A1099/V2/CompaniesW9Api.md#create_company) | **POST** /w9/companies | Create a company
*CompaniesW9Api* | [**delete_company**](docs/A1099/V2/CompaniesW9Api.md#delete_company) | **DELETE** /w9/companies/{id} | Delete a company
*CompaniesW9Api* | [**get_companies**](docs/A1099/V2/CompaniesW9Api.md#get_companies) | **GET** /w9/companies | List companies
*CompaniesW9Api* | [**get_company**](docs/A1099/V2/CompaniesW9Api.md#get_company) | **GET** /w9/companies/{id} | Retrieve a company
*CompaniesW9Api* | [**update_company**](docs/A1099/V2/CompaniesW9Api.md#update_company) | **PUT** /w9/companies/{id} | Update a company
*Forms1099Api* | [**bulk_upsert1099_forms**](docs/A1099/V2/Forms1099Api.md#bulk_upsert1099_forms) | **POST** /1099/forms/$bulk-upsert | Create or update multiple 1099/1095/W2/1042S forms
*Forms1099Api* | [**create1099_form**](docs/A1099/V2/Forms1099Api.md#create1099_form) | **POST** /1099/forms | Create a 1099/1095/W2/1042S form
*Forms1099Api* | [**delete1099_form**](docs/A1099/V2/Forms1099Api.md#delete1099_form) | **DELETE** /1099/forms/{id} | Delete a 1099/1095/W2/1042S form
*Forms1099Api* | [**get1099_form**](docs/A1099/V2/Forms1099Api.md#get1099_form) | **GET** /1099/forms/{id} | Retrieve a 1099/1095/W2/1042S form
*Forms1099Api* | [**get1099_form_pdf**](docs/A1099/V2/Forms1099Api.md#get1099_form_pdf) | **GET** /1099/forms/{id}/pdf | Retrieve the PDF file for a 1099/1095/W2/1042S form
*Forms1099Api* | [**list1099_forms**](docs/A1099/V2/Forms1099Api.md#list1099_forms) | **GET** /1099/forms | List 1099/1095/W2/1042S forms
*Forms1099Api* | [**update1099_form**](docs/A1099/V2/Forms1099Api.md#update1099_form) | **PUT** /1099/forms/{id} | Update a 1099/1095/W2/1042S form
*FormsW9Api* | [**create_and_send_w9_form_email**](docs/A1099/V2/FormsW9Api.md#create_and_send_w9_form_email) | **POST** /w9/forms/$create-and-send-email | Create a minimal W9/W4/W8 form and sends the e-mail request
*FormsW9Api* | [**create_w9_form**](docs/A1099/V2/FormsW9Api.md#create_w9_form) | **POST** /w9/forms | Create a W9/W4/W8 form
*FormsW9Api* | [**delete_w9_form**](docs/A1099/V2/FormsW9Api.md#delete_w9_form) | **DELETE** /w9/forms/{id} | Delete a W9/W4/W8 form
*FormsW9Api* | [**get_w9_form**](docs/A1099/V2/FormsW9Api.md#get_w9_form) | **GET** /w9/forms/{id} | Retrieve a W9/W4/W8 form
*FormsW9Api* | [**list_w9_forms**](docs/A1099/V2/FormsW9Api.md#list_w9_forms) | **GET** /w9/forms | List W9/W4/W8 forms
*FormsW9Api* | [**send_w9_form_email**](docs/A1099/V2/FormsW9Api.md#send_w9_form_email) | **POST** /w9/forms/{id}/$send-email | Send an email to the vendor/payee requesting they fill out a W9/W4/W8 form
*FormsW9Api* | [**update_w9_form**](docs/A1099/V2/FormsW9Api.md#update_w9_form) | **PUT** /w9/forms/{id} | Update a W9/W4/W8 form
*FormsW9Api* | [**upload_w9_files**](docs/A1099/V2/FormsW9Api.md#upload_w9_files) | **POST** /w9/forms/{id}/attachment | Replace the PDF file for a W9/W4/W8 form
*Issuers1099Api* | [**create_issuer**](docs/A1099/V2/Issuers1099Api.md#create_issuer) | **POST** /1099/issuers | Create an issuer
*Issuers1099Api* | [**delete_issuer**](docs/A1099/V2/Issuers1099Api.md#delete_issuer) | **DELETE** /1099/issuers/{id} | Delete an issuer
*Issuers1099Api* | [**get_issuer**](docs/A1099/V2/Issuers1099Api.md#get_issuer) | **GET** /1099/issuers/{id} | Retrieve an issuer
*Issuers1099Api* | [**get_issuers**](docs/A1099/V2/Issuers1099Api.md#get_issuers) | **GET** /1099/issuers | List issuers
*Issuers1099Api* | [**update_issuer**](docs/A1099/V2/Issuers1099Api.md#update_issuer) | **PUT** /1099/issuers/{id} | Update an issuer
*JobsApi* | [**get_job**](docs/A1099/V2/JobsApi.md#get_job) | **GET** /jobs/{id} | Retrieves information about the job

<a name="documentation-for-models"></a>
## Documentation for Models

<a name="documentation-for-EInvoicing-V1-models"></a>
### EInvoicing V1 Model Documentation

 - [Avalara.SDK.models.EInvoicing.V1.Address](docs/EInvoicing/V1/Address.md)
 - [Avalara.SDK.models.EInvoicing.V1.BadDownloadRequest](docs/EInvoicing/V1/BadDownloadRequest.md)
 - [Avalara.SDK.models.EInvoicing.V1.BadRequest](docs/EInvoicing/V1/BadRequest.md)
 - [Avalara.SDK.models.EInvoicing.V1.BatchErrorDetail](docs/EInvoicing/V1/BatchErrorDetail.md)
 - [Avalara.SDK.models.EInvoicing.V1.BatchSearch](docs/EInvoicing/V1/BatchSearch.md)
 - [Avalara.SDK.models.EInvoicing.V1.BatchSearchListResponse](docs/EInvoicing/V1/BatchSearchListResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.BatchSearchParticipants202Response](docs/EInvoicing/V1/BatchSearchParticipants202Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.ConditionalForField](docs/EInvoicing/V1/ConditionalForField.md)
 - [Avalara.SDK.models.EInvoicing.V1.Consents](docs/EInvoicing/V1/Consents.md)
 - [Avalara.SDK.models.EInvoicing.V1.CreateTradingPartner201Response](docs/EInvoicing/V1/CreateTradingPartner201Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.CreateTradingPartnersBatch200Response](docs/EInvoicing/V1/CreateTradingPartnersBatch200Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.CreateTradingPartnersBatch200ResponseValueInner](docs/EInvoicing/V1/CreateTradingPartnersBatch200ResponseValueInner.md)
 - [Avalara.SDK.models.EInvoicing.V1.CreateTradingPartnersBatchRequest](docs/EInvoicing/V1/CreateTradingPartnersBatchRequest.md)
 - [Avalara.SDK.models.EInvoicing.V1.DataInputField](docs/EInvoicing/V1/DataInputField.md)
 - [Avalara.SDK.models.EInvoicing.V1.DataInputFieldNotUsedFor](docs/EInvoicing/V1/DataInputFieldNotUsedFor.md)
 - [Avalara.SDK.models.EInvoicing.V1.DataInputFieldOptionalFor](docs/EInvoicing/V1/DataInputFieldOptionalFor.md)
 - [Avalara.SDK.models.EInvoicing.V1.DataInputFieldRequiredFor](docs/EInvoicing/V1/DataInputFieldRequiredFor.md)
 - [Avalara.SDK.models.EInvoicing.V1.DataInputFieldsResponse](docs/EInvoicing/V1/DataInputFieldsResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentFetch](docs/EInvoicing/V1/DocumentFetch.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentListResponse](docs/EInvoicing/V1/DocumentListResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentStatusResponse](docs/EInvoicing/V1/DocumentStatusResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentSubmissionError](docs/EInvoicing/V1/DocumentSubmissionError.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentSubmitResponse](docs/EInvoicing/V1/DocumentSubmitResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.DocumentSummary](docs/EInvoicing/V1/DocumentSummary.md)
 - [Avalara.SDK.models.EInvoicing.V1.ErrorResponse](docs/EInvoicing/V1/ErrorResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.EventId](docs/EInvoicing/V1/EventId.md)
 - [Avalara.SDK.models.EInvoicing.V1.EventMessage](docs/EInvoicing/V1/EventMessage.md)
 - [Avalara.SDK.models.EInvoicing.V1.EventPayload](docs/EInvoicing/V1/EventPayload.md)
 - [Avalara.SDK.models.EInvoicing.V1.EventSubscription](docs/EInvoicing/V1/EventSubscription.md)
 - [Avalara.SDK.models.EInvoicing.V1.Extension](docs/EInvoicing/V1/Extension.md)
 - [Avalara.SDK.models.EInvoicing.V1.FetchDocumentsRequest](docs/EInvoicing/V1/FetchDocumentsRequest.md)
 - [Avalara.SDK.models.EInvoicing.V1.FetchDocumentsRequestDataInner](docs/EInvoicing/V1/FetchDocumentsRequestDataInner.md)
 - [Avalara.SDK.models.EInvoicing.V1.FetchDocumentsRequestMetadata](docs/EInvoicing/V1/FetchDocumentsRequestMetadata.md)
 - [Avalara.SDK.models.EInvoicing.V1.ForbiddenError](docs/EInvoicing/V1/ForbiddenError.md)
 - [Avalara.SDK.models.EInvoicing.V1.HmacSignature](docs/EInvoicing/V1/HmacSignature.md)
 - [Avalara.SDK.models.EInvoicing.V1.HmacSignatureValue](docs/EInvoicing/V1/HmacSignatureValue.md)
 - [Avalara.SDK.models.EInvoicing.V1.Id](docs/EInvoicing/V1/Id.md)
 - [Avalara.SDK.models.EInvoicing.V1.Identifier](docs/EInvoicing/V1/Identifier.md)
 - [Avalara.SDK.models.EInvoicing.V1.InputDataFormats](docs/EInvoicing/V1/InputDataFormats.md)
 - [Avalara.SDK.models.EInvoicing.V1.InternalServerError](docs/EInvoicing/V1/InternalServerError.md)
 - [Avalara.SDK.models.EInvoicing.V1.Mandate](docs/EInvoicing/V1/Mandate.md)
 - [Avalara.SDK.models.EInvoicing.V1.MandateDataInputField](docs/EInvoicing/V1/MandateDataInputField.md)
 - [Avalara.SDK.models.EInvoicing.V1.MandateDataInputFieldNamespace](docs/EInvoicing/V1/MandateDataInputFieldNamespace.md)
 - [Avalara.SDK.models.EInvoicing.V1.MandatesResponse](docs/EInvoicing/V1/MandatesResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.NotFoundError](docs/EInvoicing/V1/NotFoundError.md)
 - [Avalara.SDK.models.EInvoicing.V1.NotUsedForField](docs/EInvoicing/V1/NotUsedForField.md)
 - [Avalara.SDK.models.EInvoicing.V1.OutputDataFormats](docs/EInvoicing/V1/OutputDataFormats.md)
 - [Avalara.SDK.models.EInvoicing.V1.Pagination](docs/EInvoicing/V1/Pagination.md)
 - [Avalara.SDK.models.EInvoicing.V1.RequiredWhenField](docs/EInvoicing/V1/RequiredWhenField.md)
 - [Avalara.SDK.models.EInvoicing.V1.SearchParticipants200Response](docs/EInvoicing/V1/SearchParticipants200Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.Signature](docs/EInvoicing/V1/Signature.md)
 - [Avalara.SDK.models.EInvoicing.V1.SignatureSignature](docs/EInvoicing/V1/SignatureSignature.md)
 - [Avalara.SDK.models.EInvoicing.V1.SignatureValue](docs/EInvoicing/V1/SignatureValue.md)
 - [Avalara.SDK.models.EInvoicing.V1.SignatureValueSignature](docs/EInvoicing/V1/SignatureValueSignature.md)
 - [Avalara.SDK.models.EInvoicing.V1.StatusEvent](docs/EInvoicing/V1/StatusEvent.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubmitDocumentMetadata](docs/EInvoicing/V1/SubmitDocumentMetadata.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubmitInteropDocument202Response](docs/EInvoicing/V1/SubmitInteropDocument202Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubscriptionCommon](docs/EInvoicing/V1/SubscriptionCommon.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubscriptionDetail](docs/EInvoicing/V1/SubscriptionDetail.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubscriptionListResponse](docs/EInvoicing/V1/SubscriptionListResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.SubscriptionRegistration](docs/EInvoicing/V1/SubscriptionRegistration.md)
 - [Avalara.SDK.models.EInvoicing.V1.SuccessResponse](docs/EInvoicing/V1/SuccessResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.SupportedDocumentTypes](docs/EInvoicing/V1/SupportedDocumentTypes.md)
 - [Avalara.SDK.models.EInvoicing.V1.TaxIdentifierRequest](docs/EInvoicing/V1/TaxIdentifierRequest.md)
 - [Avalara.SDK.models.EInvoicing.V1.TaxIdentifierResponse](docs/EInvoicing/V1/TaxIdentifierResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.TaxIdentifierResponseValue](docs/EInvoicing/V1/TaxIdentifierResponseValue.md)
 - [Avalara.SDK.models.EInvoicing.V1.TaxIdentifierSchemaByCountry200Response](docs/EInvoicing/V1/TaxIdentifierSchemaByCountry200Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.TradingPartner](docs/EInvoicing/V1/TradingPartner.md)
 - [Avalara.SDK.models.EInvoicing.V1.UpdateTradingPartner200Response](docs/EInvoicing/V1/UpdateTradingPartner200Response.md)
 - [Avalara.SDK.models.EInvoicing.V1.ValidationError](docs/EInvoicing/V1/ValidationError.md)
 - [Avalara.SDK.models.EInvoicing.V1.WebhookInvocation](docs/EInvoicing/V1/WebhookInvocation.md)
 - [Avalara.SDK.models.EInvoicing.V1.WebhooksErrorInfo](docs/EInvoicing/V1/WebhooksErrorInfo.md)
 - [Avalara.SDK.models.EInvoicing.V1.WebhooksErrorResponse](docs/EInvoicing/V1/WebhooksErrorResponse.md)
 - [Avalara.SDK.models.EInvoicing.V1.WorkflowIds](docs/EInvoicing/V1/WorkflowIds.md)


<a name="documentation-for-A1099-V2-models"></a>
### A1099 V2 Model Documentation

 - [Avalara.SDK.models.A1099.V2.AuthorizedApiRequestModel](docs/A1099/V2/AuthorizedApiRequestModel.md)
 - [Avalara.SDK.models.A1099.V2.AuthorizedApiRequestV2DataModel](docs/A1099/V2/AuthorizedApiRequestV2DataModel.md)
 - [Avalara.SDK.models.A1099.V2.CompanyCreateUpdateRequestModel](docs/A1099/V2/CompanyCreateUpdateRequestModel.md)
 - [Avalara.SDK.models.A1099.V2.CompanyResponse](docs/A1099/V2/CompanyResponse.md)
 - [Avalara.SDK.models.A1099.V2.CoveredIndividual](docs/A1099/V2/CoveredIndividual.md)
 - [Avalara.SDK.models.A1099.V2.CreateAndSendW9FormEmailRequest](docs/A1099/V2/CreateAndSendW9FormEmailRequest.md)
 - [Avalara.SDK.models.A1099.V2.CreateCompanyRequest](docs/A1099/V2/CreateCompanyRequest.md)
 - [Avalara.SDK.models.A1099.V2.CreateIssuerRequest](docs/A1099/V2/CreateIssuerRequest.md)
 - [Avalara.SDK.models.A1099.V2.CreateW9Form201Response](docs/A1099/V2/CreateW9Form201Response.md)
 - [Avalara.SDK.models.A1099.V2.CreateW9FormRequest](docs/A1099/V2/CreateW9FormRequest.md)
 - [Avalara.SDK.models.A1099.V2.EntryStatusResponse](docs/A1099/V2/EntryStatusResponse.md)
 - [Avalara.SDK.models.A1099.V2.ErrorModel](docs/A1099/V2/ErrorModel.md)
 - [Avalara.SDK.models.A1099.V2.ErrorResponse](docs/A1099/V2/ErrorResponse.md)
 - [Avalara.SDK.models.A1099.V2.ErrorResponseItem](docs/A1099/V2/ErrorResponseItem.md)
 - [Avalara.SDK.models.A1099.V2.Form1042S](docs/A1099/V2/Form1042S.md)
 - [Avalara.SDK.models.A1099.V2.Form1095B](docs/A1099/V2/Form1095B.md)
 - [Avalara.SDK.models.A1099.V2.Form1095C](docs/A1099/V2/Form1095C.md)
 - [Avalara.SDK.models.A1099.V2.Form1099Base](docs/A1099/V2/Form1099Base.md)
 - [Avalara.SDK.models.A1099.V2.Form1099Div](docs/A1099/V2/Form1099Div.md)
 - [Avalara.SDK.models.A1099.V2.Form1099Int](docs/A1099/V2/Form1099Int.md)
 - [Avalara.SDK.models.A1099.V2.Form1099K](docs/A1099/V2/Form1099K.md)
 - [Avalara.SDK.models.A1099.V2.Form1099ListRequest](docs/A1099/V2/Form1099ListRequest.md)
 - [Avalara.SDK.models.A1099.V2.Form1099Misc](docs/A1099/V2/Form1099Misc.md)
 - [Avalara.SDK.models.A1099.V2.Form1099Nec](docs/A1099/V2/Form1099Nec.md)
 - [Avalara.SDK.models.A1099.V2.Form1099R](docs/A1099/V2/Form1099R.md)
 - [Avalara.SDK.models.A1099.V2.Form1099StatusDetail](docs/A1099/V2/Form1099StatusDetail.md)
 - [Avalara.SDK.models.A1099.V2.Get1099Form200Response](docs/A1099/V2/Get1099Form200Response.md)
 - [Avalara.SDK.models.A1099.V2.IW9FormDataModelsOneOf](docs/A1099/V2/IW9FormDataModelsOneOf.md)
 - [Avalara.SDK.models.A1099.V2.IntermediaryOrFlowThrough](docs/A1099/V2/IntermediaryOrFlowThrough.md)
 - [Avalara.SDK.models.A1099.V2.IrsResponse](docs/A1099/V2/IrsResponse.md)
 - [Avalara.SDK.models.A1099.V2.IssuerCommand](docs/A1099/V2/IssuerCommand.md)
 - [Avalara.SDK.models.A1099.V2.IssuerResponse](docs/A1099/V2/IssuerResponse.md)
 - [Avalara.SDK.models.A1099.V2.JobResponse](docs/A1099/V2/JobResponse.md)
 - [Avalara.SDK.models.A1099.V2.OfferAndCoverage](docs/A1099/V2/OfferAndCoverage.md)
 - [Avalara.SDK.models.A1099.V2.PaginatedQueryResultModelCompanyResponse](docs/A1099/V2/PaginatedQueryResultModelCompanyResponse.md)
 - [Avalara.SDK.models.A1099.V2.PaginatedQueryResultModelForm1099Base](docs/A1099/V2/PaginatedQueryResultModelForm1099Base.md)
 - [Avalara.SDK.models.A1099.V2.PaginatedQueryResultModelIssuerResponse](docs/A1099/V2/PaginatedQueryResultModelIssuerResponse.md)
 - [Avalara.SDK.models.A1099.V2.PaginatedQueryResultModelW9FormBaseResponse](docs/A1099/V2/PaginatedQueryResultModelW9FormBaseResponse.md)
 - [Avalara.SDK.models.A1099.V2.PrimaryWithholdingAgent](docs/A1099/V2/PrimaryWithholdingAgent.md)
 - [Avalara.SDK.models.A1099.V2.StateAndLocalWithholding](docs/A1099/V2/StateAndLocalWithholding.md)
 - [Avalara.SDK.models.A1099.V2.StateEfileStatusDetail](docs/A1099/V2/StateEfileStatusDetail.md)
 - [Avalara.SDK.models.A1099.V2.SubstantialUsOwnerRequest](docs/A1099/V2/SubstantialUsOwnerRequest.md)
 - [Avalara.SDK.models.A1099.V2.SubstantialUsOwnerResponse](docs/A1099/V2/SubstantialUsOwnerResponse.md)
 - [Avalara.SDK.models.A1099.V2.TinMatchStatusResponse](docs/A1099/V2/TinMatchStatusResponse.md)
 - [Avalara.SDK.models.A1099.V2.ValidationError](docs/A1099/V2/ValidationError.md)
 - [Avalara.SDK.models.A1099.V2.W4FormDataModel](docs/A1099/V2/W4FormDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W4FormMinimalRequest](docs/A1099/V2/W4FormMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W4FormRequest](docs/A1099/V2/W4FormRequest.md)
 - [Avalara.SDK.models.A1099.V2.W4FormResponse](docs/A1099/V2/W4FormResponse.md)
 - [Avalara.SDK.models.A1099.V2.W8BenEFormMinimalRequest](docs/A1099/V2/W8BenEFormMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8BenEFormRequest](docs/A1099/V2/W8BenEFormRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8BenEFormResponse](docs/A1099/V2/W8BenEFormResponse.md)
 - [Avalara.SDK.models.A1099.V2.W8BenESubstantialUsOwnerDataModel](docs/A1099/V2/W8BenESubstantialUsOwnerDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W8BenFormDataModel](docs/A1099/V2/W8BenFormDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W8BenFormMinimalRequest](docs/A1099/V2/W8BenFormMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8BenFormRequest](docs/A1099/V2/W8BenFormRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8BenFormResponse](docs/A1099/V2/W8BenFormResponse.md)
 - [Avalara.SDK.models.A1099.V2.W8BeneFormDataModel](docs/A1099/V2/W8BeneFormDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W8ImyFormDataModel](docs/A1099/V2/W8ImyFormDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W8ImyFormMinimalRequest](docs/A1099/V2/W8ImyFormMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8ImyFormRequest](docs/A1099/V2/W8ImyFormRequest.md)
 - [Avalara.SDK.models.A1099.V2.W8ImyFormResponse](docs/A1099/V2/W8ImyFormResponse.md)
 - [Avalara.SDK.models.A1099.V2.W9FormBaseMinimalRequest](docs/A1099/V2/W9FormBaseMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W9FormBaseRequest](docs/A1099/V2/W9FormBaseRequest.md)
 - [Avalara.SDK.models.A1099.V2.W9FormBaseResponse](docs/A1099/V2/W9FormBaseResponse.md)
 - [Avalara.SDK.models.A1099.V2.W9FormDataModel](docs/A1099/V2/W9FormDataModel.md)
 - [Avalara.SDK.models.A1099.V2.W9FormMinimalRequest](docs/A1099/V2/W9FormMinimalRequest.md)
 - [Avalara.SDK.models.A1099.V2.W9FormRequest](docs/A1099/V2/W9FormRequest.md)
 - [Avalara.SDK.models.A1099.V2.W9FormResponse](docs/A1099/V2/W9FormResponse.md)
