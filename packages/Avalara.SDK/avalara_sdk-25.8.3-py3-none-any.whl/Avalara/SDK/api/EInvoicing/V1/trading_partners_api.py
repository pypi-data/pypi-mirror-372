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
from pydantic import Field, StrictBool, StrictBytes, StrictInt, StrictStr
from typing import Optional, Union
from typing_extensions import Annotated
from Avalara.SDK.models.EInvoicing.V1.batch_search import BatchSearch
from Avalara.SDK.models.EInvoicing.V1.batch_search_list_response import BatchSearchListResponse
from Avalara.SDK.models.EInvoicing.V1.batch_search_participants202_response import BatchSearchParticipants202Response
from Avalara.SDK.models.EInvoicing.V1.create_trading_partner201_response import CreateTradingPartner201Response
from Avalara.SDK.models.EInvoicing.V1.create_trading_partners_batch200_response import CreateTradingPartnersBatch200Response
from Avalara.SDK.models.EInvoicing.V1.create_trading_partners_batch_request import CreateTradingPartnersBatchRequest
from Avalara.SDK.models.EInvoicing.V1.search_participants200_response import SearchParticipants200Response
from Avalara.SDK.models.EInvoicing.V1.trading_partner import TradingPartner
from Avalara.SDK.models.EInvoicing.V1.update_trading_partner200_response import UpdateTradingPartner200Response
from Avalara.SDK.exceptions import ApiTypeError, ApiValueError, ApiException
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import avalara_retry_oauth

class TradingPartnersApi(object):

    def __init__(self, api_client):
        self.__set_configuration(api_client)
    
    def __verify_api_client(self,api_client):
        if api_client is None:
            raise ApiValueError("APIClient not defined")
    
    def __set_configuration(self, api_client):
        self.__verify_api_client(api_client)
        api_client.set_sdk_version("25.8.3")
        self.api_client = api_client
		
        self.batch_search_participants_endpoint = _Endpoint(
            settings={
                'response_type': (BatchSearchParticipants202Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/batch-searches',
                'operation_id': 'batch_search_participants',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'name',
                    'notification_email',
                    'file',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'name',
                    'notification_email',
                    'file',
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
                    'name':
                        (str,),
                    'notification_email':
                        (str,),
                    'file':
                        (bytearray,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'name': 'name',
                    'notification_email': 'notificationEmail',
                    'file': 'file',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'name': 'query',
                    'notification_email': 'query',
                    'file': 'form',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'multipart/form-data'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )
        self.create_trading_partner_endpoint = _Endpoint(
            settings={
                'response_type': (CreateTradingPartner201Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners',
                'operation_id': 'create_trading_partner',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'trading_partner',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'trading_partner',
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
                    'trading_partner':
                        (TradingPartner,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'trading_partner': 'body',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )
        self.create_trading_partners_batch_endpoint = _Endpoint(
            settings={
                'response_type': (CreateTradingPartnersBatch200Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/batch',
                'operation_id': 'create_trading_partners_batch',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'create_trading_partners_batch_request',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'create_trading_partners_batch_request',
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
                    'create_trading_partners_batch_request':
                        (CreateTradingPartnersBatchRequest,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'create_trading_partners_batch_request': 'body',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )
        self.delete_trading_partner_endpoint = _Endpoint(
            settings={
                'response_type': None,
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/{id}',
                'operation_id': 'delete_trading_partner',
                'http_method': 'DELETE',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'id',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'id',
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
                    'id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'id': 'id',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'id': 'path',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
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
        self.download_batch_search_report_endpoint = _Endpoint(
            settings={
                'response_type': (bytearray,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/batch-searches/{id}/$download-results',
                'operation_id': 'download_batch_search_report',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'id',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'id',
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
                    'id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'id': 'id',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'id': 'path',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'text/csv',
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )
        self.get_batch_search_detail_endpoint = _Endpoint(
            settings={
                'response_type': (BatchSearch,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/batch-searches/{id}',
                'operation_id': 'get_batch_search_detail',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'id',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'id',
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
                    'id':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'id': 'id',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'id': 'path',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
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
        self.list_batch_searches_endpoint = _Endpoint(
            settings={
                'response_type': (BatchSearchListResponse,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/batch-searches',
                'operation_id': 'list_batch_searches',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'x_avalara_client',
                    'filter',
                    'count',
                    'top',
                    'skip',
                    'order_by',
                    'x_correlation_id',
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
                    'count':
                        (bool,),
                    'top':
                        (int,),
                    'skip':
                        (int,),
                    'order_by':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'x_avalara_client': 'X-Avalara-Client',
                    'filter': '$filter',
                    'count': 'count',
                    'top': '$top',
                    'skip': '$skip',
                    'order_by': '$orderBy',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'x_avalara_client': 'header',
                    'filter': 'query',
                    'count': 'query',
                    'top': 'query',
                    'skip': 'query',
                    'order_by': 'query',
                    'x_correlation_id': 'header',
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
        self.search_participants_endpoint = _Endpoint(
            settings={
                'response_type': (SearchParticipants200Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners',
                'operation_id': 'search_participants',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'search',
                    'x_avalara_client',
                    'count',
                    'filter',
                    'top',
                    'skip',
                    'order_by',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'search',
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
                    'search':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'count':
                        (bool,),
                    'filter':
                        (str,),
                    'top':
                        (int,),
                    'skip':
                        (int,),
                    'order_by':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'search': '$search',
                    'x_avalara_client': 'X-Avalara-Client',
                    'count': 'count',
                    'filter': '$filter',
                    'top': '$top',
                    'skip': '$skip',
                    'order_by': '$orderBy',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'search': 'query',
                    'x_avalara_client': 'header',
                    'count': 'query',
                    'filter': 'query',
                    'top': 'query',
                    'skip': 'query',
                    'order_by': 'query',
                    'x_correlation_id': 'header',
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
        self.update_trading_partner_endpoint = _Endpoint(
            settings={
                'response_type': (UpdateTradingPartner200Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/trading-partners/{id}',
                'operation_id': 'update_trading_partner',
                'http_method': 'PUT',
                'servers': None,
            },
            params_map={
                'all': [
                    'avalara_version',
                    'id',
                    'trading_partner',
                    'x_avalara_client',
                    'x_correlation_id',
                ],
                'required': [
                    'avalara_version',
                    'id',
                    'trading_partner',
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
                    'id':
                        (str,),
                    'trading_partner':
                        (TradingPartner,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                },
                'attribute_map': {
                    'avalara_version': 'avalara-version',
                    'id': 'id',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                },
                'location_map': {
                    'avalara_version': 'header',
                    'id': 'path',
                    'trading_partner': 'body',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'avalara-version': '1.4',
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client,
            required_scopes='',
            microservice='EInvoicing'
        )

    @avalara_retry_oauth(max_retry_attempts=2)
    def batch_search_participants(
        self,
        avalara_version,
        name,
        notification_email,
        file,
        **kwargs
    ):
        """Handles batch search requests by uploading a file containing search parameters.  # noqa: E501

        This endpoint creates a batch search and performs a batch search in the directory for participants in the background.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.batch_search_participants(avalara_version, name, notification_email, file, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            name (str): A <b>human-readable</b> name for the batch search.
            notification_email (str): The email address to which a notification will be sent once the batch search is complete.
            file (bytearray): CSV file containing search parameters.  Input Constraints: - Maximum file size: 1 MB - File Header: Must be less than 500 KB - Total number of lines (including header): Must be 101 or fewer

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            BatchSearchParticipants202Response
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
        kwargs['name'] = name
        kwargs['notification_email'] = notification_email
        kwargs['file'] = file
        return self.batch_search_participants_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def create_trading_partner(
        self,
        avalara_version,
        trading_partner,
        **kwargs
    ):
        """Creates a new trading partner.  # noqa: E501

        This endpoint creates a new trading partner with the provided details. The request body must include the necessary information as defined in the `TradingPartner` schema.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_trading_partner(avalara_version, trading_partner, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            trading_partner (TradingPartner):

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            CreateTradingPartner201Response
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
        kwargs['trading_partner'] = trading_partner
        return self.create_trading_partner_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def create_trading_partners_batch(
        self,
        avalara_version,
        create_trading_partners_batch_request,
        **kwargs
    ):
        """Creates a batch of multiple trading partners.  # noqa: E501

        This endpoint creates multiple trading partners in a single batch request. It accepts an array of trading partners and processes them synchronously. Supports a maximum of 100 records or 1 MB request payload. The batch is processed atomically and partial success is not allowed.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_trading_partners_batch(avalara_version, create_trading_partners_batch_request, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            create_trading_partners_batch_request (CreateTradingPartnersBatchRequest):

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            CreateTradingPartnersBatch200Response
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
        kwargs['create_trading_partners_batch_request'] = create_trading_partners_batch_request
        return self.create_trading_partners_batch_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def delete_trading_partner(
        self,
        avalara_version,
        id,
        **kwargs
    ):
        """Deletes a trading partner using ID.  # noqa: E501

        This endpoint deletes an existing trading partner identified by the provided ID.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_trading_partner(avalara_version, id, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            id (str): The ID of the trading partner which is being deleted.

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
        kwargs['avalara_version'] = avalara_version
        kwargs['id'] = id
        return self.delete_trading_partner_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def download_batch_search_report(
        self,
        avalara_version,
        id,
        **kwargs
    ):
        """Downloads batch search results in a csv file.  # noqa: E501

        This endpoint downloads the report for a specific batch search using the batch search ID. It returns a CSV file containing up to 1,000 query results.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.download_batch_search_report(avalara_version, id, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            id (str): The ID of the batch search for which the report should be downloaded.

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
        kwargs['avalara_version'] = avalara_version
        kwargs['id'] = id
        return self.download_batch_search_report_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def get_batch_search_detail(
        self,
        avalara_version,
        id,
        **kwargs
    ):
        """Returns the batch search details using ID.  # noqa: E501

        This endpoint returns detailed information for a specific batch search using the provided ID. It is useful for tracking the status and progress of a previously initiated batch search operation.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_batch_search_detail(avalara_version, id, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            id (str): The ID of the batch search that was submitted earlier.

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            BatchSearch
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
        kwargs['id'] = id
        return self.get_batch_search_detail_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def list_batch_searches(
        self,
        avalara_version,
        **kwargs
    ):
        """Lists all batch searches that were previously submitted.  # noqa: E501

        This endpoint retrieves a list of all batch search operations that have been previously submitted. It returns details such as the batch search ID, status, creation date, and associated metadata. It is useful for tracking the progress of a previously initiated batch search operations.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_batch_searches(avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            filter (str): Filters the results by field name. Only the <code>eq</code> operator and the name field is supported. For more information, refer to [AvaTax filtering guide](https://developer.avalara.com/avatax/filtering-in-rest/).. [optional]
            count (bool): When set to <code>true</code>, returns the total count of matching records included as <code>@recordSetCount</code> in the response body.. [optional]
            top (int): The number of items to include in the result.. [optional]
            skip (int): The number of items to skip in the result.. [optional]
            order_by (str): The <code>$orderBy</code> query parameter specifies the field and sorting direction for ordering the result set. The value is a string that combines a field name and a sorting direction (asc for ascending or desc for descending), separated by a space.. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            BatchSearchListResponse
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
        return self.list_batch_searches_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def search_participants(
        self,
        avalara_version,
        search,
        **kwargs
    ):
        """Returns a list of participants matching the input query.  # noqa: E501

        This endpoint retrieves a list of trading partners that match the specified search criteria. It supports filtering, search text, and other relevant query parameters to narrow down the results.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.search_participants(avalara_version, search, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            search (str): Search by value supports logical <code>AND</code> / <code>OR</code> operators. Search is performed only over the name and identifier value fields. For more information, refer to [Query options overview - OData.](https://learn.microsoft.com/en-us/odata/concepts/queryoptions-overview#search).

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            count (bool): When set to <code>true</code>, returns the total count of matching records included as <code>@recordSetCount</code> in the response body.. [optional]
            filter (str): Filters the results using the <code>eq</code> operator. Supported fields: <code>network</code>, <code>country</code>, <code>documentType</code>, <code>idType</code>. For more information, refer to [AvaTax filtering guide](https://developer.avalara.com/avatax/filtering-in-rest/).. [optional]
            top (int): The number of items to include in the result.. [optional]
            skip (int): The number of items to skip in the result.. [optional]
            order_by (str): The <code>$orderBy</code> query parameter specifies the field and sorting direction for ordering the result set. The value is a string that combines a field name and a sorting direction (asc for ascending or desc for descending), separated by a space.. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            SearchParticipants200Response
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
        kwargs['search'] = search
        return self.search_participants_endpoint.call_with_http_info(**kwargs)

    @avalara_retry_oauth(max_retry_attempts=2)
    def update_trading_partner(
        self,
        avalara_version,
        id,
        trading_partner,
        **kwargs
    ):
        """Updates a trading partner using ID.  # noqa: E501

        This endpoint updates the details of an existing trading partner specified by the provided ID. It performs a full update, and the request body must include all required fields.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.update_trading_partner(avalara_version, id, trading_partner, async_req=True)
        >>> result = thread.get()

        Args:
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used.
            id (str): The ID of the trading partner which is being updated.
            trading_partner (TradingPartner):

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\".. [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
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
            UpdateTradingPartner200Response
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
        kwargs['id'] = id
        kwargs['trading_partner'] = trading_partner
        return self.update_trading_partner_endpoint.call_with_http_info(**kwargs)

