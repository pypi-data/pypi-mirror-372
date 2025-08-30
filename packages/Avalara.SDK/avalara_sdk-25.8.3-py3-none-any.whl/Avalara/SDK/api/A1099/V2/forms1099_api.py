"""
AvaTax Software Development Kit for Python.

   Copyright 2022 Avalara, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

    Avalara 1099 & W-9 API Definition
    ## 🔐 Authentication  Generate a **license key** from: *[Avalara Portal](https://www.avalara.com/us/en/signin.html) → Settings → License and API Keys*.  [More on authentication methods](https://developer.avalara.com/avatax-dm-combined-erp/common-setup/authentication/authentication-methods/)  [Test your credentials](https://developer.avalara.com/avatax/test-credentials/)  ## 📘 API & SDK Documentation  [Avalara SDK (.NET) on GitHub](https://github.com/avadev/Avalara-SDK-DotNet#avalarasdk--the-unified-c-library-for-next-gen-avalara-services)  [Code Examples – 1099 API](https://github.com/avadev/Avalara-SDK-DotNet/blob/main/docs/A1099/V2/Class1099IssuersApi.md#call1099issuersget) 

@author     Sachin Baijal <sachin.baijal@avalara.com>
@author     Jonathan Wenger <jonathan.wenger@avalara.com>
@copyright  2022 Avalara, Inc.
@license    https://www.apache.org/licenses/LICENSE-2.0
@version    25.8.3
@link       https://github.com/avadev/AvaTax-REST-V3-Python-SDK
"""

import re  # noqa: F401
import sys  # noqa: F401
import decimal

from Avalara.SDK.api_client import ApiClient, Endpoint as _Endpoint
from Avalara.SDK.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from pydantic import Field, StrictBool, StrictBytes, StrictInt, StrictStr
from typing import Optional, Union
from typing_extensions import Annotated
from Avalara.SDK.models.A1099.V2.form1099_list_request import Form1099ListRequest
from Avalara.SDK.models.A1099.V2.get1099_form200_response import Get1099Form200Response
from Avalara.SDK.models.A1099.V2.job_response import JobResponse
from Avalara.SDK.models.A1099.V2.paginated_query_result_model_form1099_base import PaginatedQueryResultModelForm1099Base
from Avalara.SDK.exceptions import ApiTypeError, ApiValueError, ApiException
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import avalara_retry_oauth

class Forms1099Api(object):

    def __init__(self, api_client):
        self.__set_configuration(api_client)
    
    def __verify_api_client(self,api_client):
        if api_client is None:
            raise ApiValueError("APIClient not defined")
    
    def __set_configuration(self, api_client):
        self.__verify_api_client(api_client)
        api_client.set_sdk_version("25.8.3")
        self.api_client = api_client
		
        self.bulk_upsert1099_forms_endpoint = _Endpoint(
            settings={
                'response_type': (JobResponse,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms/$bulk-upsert',
                'operation_id': 'bulk_upsert1099_forms',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'dry_run',
                    'x_correlation_id',
                    'x_avalara_client',
                    'form1099_list_request',
                ],
                'required': [
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'avalara_version':
                        (str,),
                    'dry_run':
                        (bool,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'form1099_list_request':
                        (Form1099ListRequest,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'dry_run': 'dryRun',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'dry_run': 'query',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                    'form1099_list_request': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json',
                    'text/json',
                    'application/*+json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.create1099_form_endpoint = _Endpoint(
            settings={
                'response_type': (Get1099Form200Response,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms',
                'operation_id': 'create1099_form',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'x_correlation_id',
                    'x_avalara_client',
                    'get1099_form200_response',
                ],
                'required': [
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'avalara_version':
                        (str,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'get1099_form200_response':
                        (Get1099Form200Response,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                    'get1099_form200_response': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json',
                    'text/json',
                    'application/*+json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.delete1099_form_endpoint = _Endpoint(
            settings={
                'response_type': None,
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms/{id}',
                'operation_id': 'delete1099_form',
                'http_method': 'DELETE',
                'servers': None,
            },
            params_map={
                'all': [
                    'id',
                    'avalara_version',
                    'x_correlation_id',
                    'x_avalara_client',
                ],
                'required': [
                    'id',
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'id':
                        (str,),
                    'avalara_version':
                        (str,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                },
                'attribute_map': {
                    'id': 'id',
                    'avalara_version': 'avalara-version',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'id': 'path',
                    'avalara_version': 'header',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.get1099_form_endpoint = _Endpoint(
            settings={
                'response_type': (Get1099Form200Response,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms/{id}',
                'operation_id': 'get1099_form',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'id',
                    'avalara_version',
                    'x_correlation_id',
                    'x_avalara_client',
                ],
                'required': [
                    'id',
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'id':
                        (str,),
                    'avalara_version':
                        (str,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                },
                'attribute_map': {
                    'id': 'id',
                    'avalara_version': 'avalara-version',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'id': 'path',
                    'avalara_version': 'header',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.get1099_form_pdf_endpoint = _Endpoint(
            settings={
                'response_type': (bytearray,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms/{id}/pdf',
                'operation_id': 'get1099_form_pdf',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'id',
                    'avalara_version',
                    'mark_edelivered',
                    'x_correlation_id',
                    'x_avalara_client',
                ],
                'required': [
                    'id',
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'id':
                        (str,),
                    'avalara_version':
                        (str,),
                    'mark_edelivered':
                        (bool,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                },
                'attribute_map': {
                    'id': 'id',
                    'avalara_version': 'avalara-version',
                    'mark_edelivered': 'markEdelivered',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'id': 'path',
                    'avalara_version': 'header',
                    'mark_edelivered': 'query',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/pdf',
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.list1099_forms_endpoint = _Endpoint(
            settings={
                'response_type': (PaginatedQueryResultModelForm1099Base,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms',
                'operation_id': 'list1099_forms',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'filter',
                    'top',
                    'skip',
                    'order_by',
                    'count',
                    'count_only',
                    'x_correlation_id',
                    'x_avalara_client',
                ],
                'required': [
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'avalara_version':
                        (str,),
                    'filter':
                        (str,),
                    'top':
                        (int,),
                    'skip':
                        (int,),
                    'order_by':
                        (str,),
                    'count':
                        (bool,),
                    'count_only':
                        (bool,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'filter': '$filter',
                    'top': '$top',
                    'skip': '$skip',
                    'order_by': '$orderBy',
                    'count': 'count',
                    'count_only': 'countOnly',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'filter': 'query',
                    'top': 'query',
                    'skip': 'query',
                    'order_by': 'query',
                    'count': 'query',
                    'count_only': 'query',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )
        self.update1099_form_endpoint = _Endpoint(
            settings={
                'response_type': (Get1099Form200Response,),
                'auth': [
                    'bearer'
                ],
                'endpoint_path': '/1099/forms/{id}',
                'operation_id': 'update1099_form',
                'http_method': 'PUT',
                'servers': None,
            },
            params_map={
                'all': [
                    'id',
                    'avalara_version',
                    'x_correlation_id',
                    'x_avalara_client',
                    'get1099_form200_response',
                ],
                'required': [
                    'id',
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'id':
                        (str,),
                    'avalara_version':
                        (str,),
                    'x_correlation_id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'get1099_form200_response':
                        (Get1099Form200Response,),
                },
                'attribute_map': {
                    'id': 'id',
                    'avalara_version': 'avalara-version',
                    'x_correlation_id': 'X-Correlation-Id',
                    'x_avalara_client': 'X-Avalara-Client',
                },
                'location_map': {
                    'id': 'path',
                    'avalara_version': 'header',
                    'x_correlation_id': 'header',
                    'x_avalara_client': 'header',
                    'get1099_form200_response': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '2.0',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json',
                    'text/json',
                    'application/*+json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='A1099'
        )

    @avalara_retry_oauth(max_retry_attempts=2)
    def bulk_upsert1099_forms(
        self,
        avalara_version,
        **kwargs
    ):
        """Create or update multiple 1099/1095/W2/1042S forms  # noqa: E501

        This endpoint allows you to create or update multiple 1099/1095/W2/1042S forms.  Maximum of 5000 forms can be processed in a single bulk request.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.bulk_upsert1099_forms(avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): API version

        Keyword Args:
            dry_run (bool): defaults to false. If true, it will NOT change the DB. It will just return a report of what would've have been changed in the DB. [optional] if omitted the server will use the default value of False
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            form1099_list_request (Form1099ListRequest): . [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            JobResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['avalara_version'] = avalara_version
        return self.bulk_upsert1099_forms_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def create1099_form(
        self,
        avalara_version,
        **kwargs
    ):
        """Create a 1099/1095/W2/1042S form  # noqa: E501

        Create a 1099/1095/W2/1042S form.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create1099_form(avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): API version

        Keyword Args:
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            get1099_form200_response (Get1099Form200Response): [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Get1099Form200Response
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['avalara_version'] = avalara_version
        return self.create1099_form_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def delete1099_form(
        self,
        id,
        avalara_version,
        **kwargs
    ):
        """Delete a 1099/1095/W2/1042S form  # noqa: E501

        Delete a 1099/1095/W2/1042S form.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete1099_form(id, avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            id (str): The unique identifier of the desired form to delete.
            avalara_version (str): API version

        Keyword Args:
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            None
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['id'] = id
        kwargs['avalara_version'] = avalara_version
        return self.delete1099_form_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def get1099_form(
        self,
        id,
        avalara_version,
        **kwargs
    ):
        """Retrieve a 1099/1095/W2/1042S form  # noqa: E501

        Retrieve a 1099/1095/W2/1042S form.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get1099_form(id, avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            id (str):
            avalara_version (str): API version

        Keyword Args:
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Get1099Form200Response
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['id'] = id
        kwargs['avalara_version'] = avalara_version
        return self.get1099_form_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def get1099_form_pdf(
        self,
        id,
        avalara_version,
        **kwargs
    ):
        """Retrieve the PDF file for a 1099/1095/W2/1042S form  # noqa: E501

        Retrieve the PDF file for a 1099/1095/W2/1042S form.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get1099_form_pdf(id, avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            id (str): The ID of the form
            avalara_version (str): API version

        Keyword Args:
            mark_edelivered (bool): Optional boolean that if set indicates that the form should be marked as having been successfully edelivered. [optional]
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            bytearray
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['id'] = id
        kwargs['avalara_version'] = avalara_version
        return self.get1099_form_pdf_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def list1099_forms(
        self,
        avalara_version,
        **kwargs
    ):
        """List 1099/1095/W2/1042S forms  # noqa: E501

        List 1099/1095/W2/1042S forms.                Collections support filtering only on certain fields. An attempt to filter on an unsupported field will receive a 400 Bad Request response.                Supported filtering fields are as follows:                - issuerId  - issuerReferenceId  - taxYear  - addressVerificationStatus - possible values are: unknown, pending, failed, incomplete, unchanged, verified  - createdAt  - edeliveryStatus - possible values are: sent, unscheduled, bad_verify, bad_verify_limit, scheduled, bounced, accepted  - email  - federalEfileStatus - possible values are: unscheduled, scheduled, sent, corrected_scheduled, accepted, corrected, corrected_accepted, held  - recipientName  - mailStatus - possible values are: sent, unscheduled, pending, delivered  - referenceId  - tinMatchStatus - possible values are: none, pending, matched, failed  - type - possible values are: 940, 941, 943, 944, 945, 1042, 1042-S, 1095-B, 1095-C, 1097-BTC, 1098, 1098-C, 1098-E, 1098-Q, 1098-T, 3921, 3922, 5498, 5498-ESA, 5498-SA, 1099-MISC, 1099-A, 1099-B, 1099-C, 1099-CAP, 1099-DIV, 1099-G, 1099-INT, 1099-K, 1099-LS, 1099-LTC, 1099-NEC, 1099-OID, 1099-PATR, 1099-Q, 1099-R, 1099-S, 1099-SA, T4A, W-2, W-2G, 1099-HC  - updatedAt  - validity - possible values are: true, false                For more information on filtering, see <see href=\"https://developer.avalara.com/avatax/filtering-in-rest/\">Filtering in REST</see>.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list1099_forms(avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): API version

        Keyword Args:
            filter (str): A filter statement to identify specific records to retrieve.  For more information on filtering, see <a href=\"https://developer.avalara.com/avatax/filtering-in-rest/\">Filtering in REST</a>.. [optional]
            top (int): If zero or greater than 1000, return at most 1000 results.  Otherwise, return this number of results.  Used with skip to provide pagination for large datasets.. [optional]
            skip (int): If nonzero, skip this number of results before returning data. Used with top to provide pagination for large datasets.. [optional]
            order_by (str): A comma separated list of sort statements in the format (fieldname) [ASC|DESC], for example id ASC.. [optional]
            count (bool): If true, return the global count of elements in the collection.. [optional]
            count_only (bool): If true, return ONLY the global count of elements in the collection.  It only applies when count=true.. [optional]
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            PaginatedQueryResultModelForm1099Base
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['avalara_version'] = avalara_version
        return self.list1099_forms_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def update1099_form(
        self,
        id,
        avalara_version,
        **kwargs
    ):
        """Update a 1099/1095/W2/1042S form  # noqa: E501

        Update a 1099/1095/W2/1042S form.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.update1099_form(id, avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            id (str):
            avalara_version (str): API version

        Keyword Args:
            x_correlation_id (str): Unique correlation Id in a GUID format. [optional]
            x_avalara_client (str): Identifies the software you are using to call this API. For more information on the client header, see [Client Headers](https://developer.avalara.com/avatax/client-headers/) .. [optional]
            get1099_form200_response (Get1099Form200Response): [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Get1099Form200Response
                If the method is called asynchronously, returns the request
                thread.
        """
        self.__verify_api_client(self.api_client)
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['id'] = id
        kwargs['avalara_version'] = avalara_version
        return self.update1099_form_endpoint.call_with_http_info(**kwargs)

