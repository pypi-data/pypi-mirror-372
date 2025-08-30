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
from pydantic import Field, StrictBytes, StrictStr, field_validator
from typing import Optional, Union
from typing_extensions import Annotated
from Avalara.SDK.models.EInvoicing.V1.submit_interop_document202_response import SubmitInteropDocument202Response
from Avalara.SDK.exceptions import ApiTypeError, ApiValueError, ApiException
from Avalara.SDK.oauth_helper.AvalaraSdkOauthUtils import avalara_retry_oauth

class InteropApi(object):

    def __init__(self, api_client):
        self.__set_configuration(api_client)
    
    def __verify_api_client(self,api_client):
        if api_client is None:
            raise ApiValueError("APIClient not defined")
    
    def __set_configuration(self, api_client):
        self.__verify_api_client(api_client)
        api_client.set_sdk_version("25.8.3")
        self.api_client = api_client
		
        self.submit_interop_document_endpoint = _Endpoint(
            settings={
                'response_type': (SubmitInteropDocument202Response,),
                'auth': [
                    'Bearer'
                ],
                'endpoint_path': '/einvoicing/interop/documents',
                'operation_id': 'submit_interop_document',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'document_type',
                    'interchange_type',
                    'avalara_version',
                    'x_avalara_client',
                    'x_correlation_id',
                    'file_name',
                ],
                'required': [
                    'document_type',
                    'interchange_type',
                    'avalara_version',
                ],
                'nullable': [
                ],
                'enum': [
                    'document_type',
                    'interchange_type',
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                    ('document_type',): {

                        "&#39;invoice-2.1&#39;": 'ubl-invoice-2.1',
                        "&#39;creditnote-2.1&#39;": 'ubl-creditnote-2.1',
                        "&#39;applicationresponse-2.1&#39;": 'ubl-applicationresponse-2.1'
                    },
                    ('interchange_type',): {

                        "&#39;B2B-TIEKE&#39;": 'FI-B2B-TIEKE',
                        "&#39;B2G-TIEKE&#39;": 'FI-B2G-TIEKE'
                    },
                },
                'openapi_types': {
                    'document_type':
                        (str,),
                    'interchange_type':
                        (str,),
                    'avalara_version':
                        (str,),
                    'x_avalara_client':
                        (str,),
                    'x_correlation_id':
                        (str,),
                    'file_name':
                        (bytearray,),
                },
                'attribute_map': {
                    'document_type': 'documentType',
                    'interchange_type': 'interchangeType',
                    'avalara_version': 'avalara-version',
                    'x_avalara_client': 'X-Avalara-Client',
                    'x_correlation_id': 'X-Correlation-ID',
                    'file_name': 'fileName',
                },
                'location_map': {
                    'document_type': 'query',
                    'interchange_type': 'query',
                    'avalara_version': 'header',
                    'x_avalara_client': 'header',
                    'x_correlation_id': 'header',
                    'file_name': 'form',
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

    @avalara_retry_oauth(max_retry_attempts=2)
    def submit_interop_document(
        self,
        document_type,
        interchange_type,
        avalara_version,
        **kwargs
    ):
        """Submit a document  # noqa: E501

        This API used by the interoperability partners to submit a document to  their trading partners in Avalara on behalf of their customers.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.submit_interop_document(document_type, interchange_type, avalara_version, async_req=True)
        >>> result = thread.get()

        Args:
            document_type (str): Type of the document being uploaded. Partners will be configured in Avalara system to send only certain types of documents.
            interchange_type (str): Type of interchange (codes in Avalara system that uniquely identifies a type of interchange). Partners will be configured in Avalara system to send documents belonging to certain types of interchanges.
            avalara_version (str): The HTTP Header meant to specify the version of the API intended to be used

        Keyword Args:
            x_avalara_client (str): You can freely use any text you wish for this value. This feature can help you diagnose and solve problems with your software. The header can be treated like a \"Fingerprint\". [optional]
            x_correlation_id (str): The caller can use this as an identifier to use as a correlation id to trace the call.. [optional]
            file_name (bytearray): The file to be uploaded (e.g., UBL XML, CII XML).. [optional]
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
            SubmitInteropDocument202Response
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
        kwargs['document_type'] = document_type
        kwargs['interchange_type'] = interchange_type
        kwargs['avalara_version'] = avalara_version
        return self.submit_interop_document_endpoint.call_with_http_info(**kwargs)

