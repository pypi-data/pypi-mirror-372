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

    Avalara E-Invoicing API
    An API that supports sending data for an E-Invoicing compliance use-case. 

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
from pydantic import Field, StrictInt, StrictStr
from typing import Optional
from typing_extensions import Annotated
from Avalara.SDK.models.EInvoicing.V1.data_input_fields_response import DataInputFieldsResponse
from Avalara.SDK.exceptions import ApiTypeError, ApiValueError, ApiException
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import avalara_retry_oauth

class DataInputFieldsApi(object):

    def __init__(self, api_client):
        self.__set_configuration(api_client)
    
    def __verify_api_client(self,api_client):
        if api_client is None:
            raise ApiValueError("APIClient not defined")
    
    def __set_configuration(self, api_client):
        self.__verify_api_client(api_client)
        api_client.set_sdk_version("25.8.3")
        self.api_client = api_client
		
        self.get_data_input_fields_endpoint = _Endpoint(
            settings={
                'response_type': (DataInputFieldsResponse,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/data-input-fields',
                'operation_id': 'get_data_input_fields',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'x_avalara_client',
                    'filter',
                    'top',
                    'skip',
                    'count',
                    'count_only',
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
                    'x_avalara_client':
                        (str,),
                    'filter':
                        (str,),
                    'top':
                        (int,),
                    'skip':
                        (int,),
                    'count':
                        (bool,),
                    'count_only':
                        (bool,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'x_avalara_client': 'X-Avalara-Client',
                    'filter': '$filter',
                    'top': '$top',
                    'skip': '$skip',
                    'count': '$count',
                    'count_only': '$countOnly',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'x_avalara_client': 'header',
                    'filter': 'query',
                    'top': 'query',
                    'skip': 'query',
                    'count': 'query',
                    'count_only': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )

    @avalara_retry_oauth(max_retry_attempts=2)
    def get_data_input_fields(
        self,
        avalara_version,
        **kwargs
    ):
        """Returns the optionality of document fields for different country mandates  # noqa: E501

        This endpoint provides a list of required, conditional, and optional fields for each country mandate. You can use the <code>mandates</code> endpoint to retrieve all available country mandates. You can use the $filter query parameter to retrieve fields for a particular mandate  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_data_input_fields(avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a fingerprint.. [optional]
            filter (str): Filter by field name and value. This filter only supports <code>eq</code> and <code>contains</code>. Refer to [https://developer.avalara.com/avatax/filtering-in-rest/](https://developer.avalara.com/avatax/filtering-in-rest/) for more information on filtering.. [optional]
            top (int): The number of items to include in the result.. [optional]
            skip (int): The number of items to skip in the result.. [optional]
            count (bool): When set to true, the count of the collection is also returned in the response body. [optional]
            count_only (bool): When set to true, only the count of the collection is returned. [optional]
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
            DataInputFieldsResponse
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
        return self.get_data_input_fields_endpoint.call_with_http_info(**kwargs)

