# coding: utf-8

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

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.EInvoicing.V1.input_data_formats import InputDataFormats
from Avalara.SDK.models.EInvoicing.V1.output_data_formats import OutputDataFormats
from Avalara.SDK.models.EInvoicing.V1.workflow_ids import WorkflowIds
from typing import Optional, Set
from typing_extensions import Self

class Mandate(BaseModel):
    """
    Mandate
    """ # noqa: E501
    mandate_id: Optional[StrictStr] = Field(default=None, description="The `mandateId` is comprised of the country code, mandate type, and the network or regulation type (for example, AU-B2G-PEPPOL). Keep in mind the following when specifying a `mandateId`. - A country can have multiple mandate types (B2C, B2B, B2G). - A entity/company can opt in for multiple mandates. - A `mandateId` is the combination of country + mandate type + network/regulation.", alias="mandateId")
    country_mandate: Optional[StrictStr] = Field(default=None, description="**[LEGACY]** This field is retained for backward compatibility. It is recommended to use `mandateId` instead. The `countryMandate` similar to the `mandateId` is comprised of the country code, mandate type, and the network or regulation type (for example, AU-B2G-PEPPOL). ", alias="countryMandate")
    country_code: Optional[StrictStr] = Field(default=None, description="Country code", alias="countryCode")
    description: Optional[StrictStr] = Field(default=None, description="Mandate description")
    supported_by_elrapi: Optional[StrictBool] = Field(default=None, description="Indicates whether this mandate supported by the ELR API", alias="supportedByELRAPI")
    mandate_format: Optional[StrictStr] = Field(default=None, description="Mandate format", alias="mandateFormat")
    e_invoicing_flow: Optional[StrictStr] = Field(default=None, description="The type of e-invoicing flow for this mandate", alias="eInvoicingFlow")
    e_invoicing_flow_documentation_link: Optional[StrictStr] = Field(default=None, description="Link to the documentation for this mandate's e-invoicing flow", alias="eInvoicingFlowDocumentationLink")
    get_invoice_available_media_type: Optional[List[StrictStr]] = Field(default=None, description="List of available media types for downloading invoices for this mandate", alias="getInvoiceAvailableMediaType")
    supports_inbound_digital_document: Optional[StrictStr] = Field(default=None, description="Indicates whether this mandate supports inbound digital documents", alias="supportsInboundDigitalDocument")
    input_data_formats: Optional[List[InputDataFormats]] = Field(default=None, description="Format and version used when inputting the data", alias="inputDataFormats")
    output_data_formats: Optional[List[OutputDataFormats]] = Field(default=None, description="Lists the supported output document formats for the country mandate. For countries where specifying an output document format is required (e.g., France), this array will contain the applicable formats. For other countries where output format selection is not necessary, the array will be empty.", alias="outputDataFormats")
    workflow_ids: Optional[List[WorkflowIds]] = Field(default=None, description="Workflow ID list", alias="workflowIds")
    __properties: ClassVar[List[str]] = ["mandateId", "countryMandate", "countryCode", "description", "supportedByELRAPI", "mandateFormat", "eInvoicingFlow", "eInvoicingFlowDocumentationLink", "getInvoiceAvailableMediaType", "supportsInboundDigitalDocument", "inputDataFormats", "outputDataFormats", "workflowIds"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Mandate from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in input_data_formats (list)
        _items = []
        if self.input_data_formats:
            for _item in self.input_data_formats:
                if _item:
                    _items.append(_item.to_dict())
            _dict['inputDataFormats'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in output_data_formats (list)
        _items = []
        if self.output_data_formats:
            for _item in self.output_data_formats:
                if _item:
                    _items.append(_item.to_dict())
            _dict['outputDataFormats'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in workflow_ids (list)
        _items = []
        if self.workflow_ids:
            for _item in self.workflow_ids:
                if _item:
                    _items.append(_item.to_dict())
            _dict['workflowIds'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Mandate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "mandateId": obj.get("mandateId"),
            "countryMandate": obj.get("countryMandate"),
            "countryCode": obj.get("countryCode"),
            "description": obj.get("description"),
            "supportedByELRAPI": obj.get("supportedByELRAPI"),
            "mandateFormat": obj.get("mandateFormat"),
            "eInvoicingFlow": obj.get("eInvoicingFlow"),
            "eInvoicingFlowDocumentationLink": obj.get("eInvoicingFlowDocumentationLink"),
            "getInvoiceAvailableMediaType": obj.get("getInvoiceAvailableMediaType"),
            "supportsInboundDigitalDocument": obj.get("supportsInboundDigitalDocument"),
            "inputDataFormats": [InputDataFormats.from_dict(_item) for _item in obj["inputDataFormats"]] if obj.get("inputDataFormats") is not None else None,
            "outputDataFormats": [OutputDataFormats.from_dict(_item) for _item in obj["outputDataFormats"]] if obj.get("outputDataFormats") is not None else None,
            "workflowIds": [WorkflowIds.from_dict(_item) for _item in obj["workflowIds"]] if obj.get("workflowIds") is not None else None
        })
        return _obj


