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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from Avalara.SDK.models.EInvoicing.V1.address import Address
from Avalara.SDK.models.EInvoicing.V1.consents import Consents
from Avalara.SDK.models.EInvoicing.V1.extension import Extension
from Avalara.SDK.models.EInvoicing.V1.identifier import Identifier
from Avalara.SDK.models.EInvoicing.V1.supported_document_types import SupportedDocumentTypes
from typing import Optional, Set
from typing_extensions import Self

class TradingPartner(BaseModel):
    """
    Represents a participant in the Avalara directory.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Avalara unique ID of the participant in the directory.")
    name: Annotated[str, Field(min_length=3, strict=True, max_length=250)] = Field(description="Name of the participant (typically, the name of the business entity).")
    network: Optional[StrictStr] = Field(default=None, description="The network where the participant is present. When creating or updating a trading partner, the value provided for the attribute 'network' will be ignored.")
    registration_date: Optional[StrictStr] = Field(default=None, description="Registration date of the participant if available.", alias="registrationDate")
    identifiers: Annotated[List[Identifier], Field(min_length=1)] = Field(description="A list of identifiers associated with the trading partner. Each identifier should consistently include the fields name, and value to maintain clarity and ensure consistent structure across entries. When creating or updating a trading partner, the attribute 'name' must be agreed upon with Avalara to ensure consistency. Failing to adhere to the agreed values will result in a validation error. Further, when creating or updating a trading partner, the value provided for the attribute 'displayName' will be ignored and instead retrieved from the standard set of display names maintained.")
    addresses: Annotated[List[Address], Field(min_length=1)]
    supported_document_types: Annotated[List[SupportedDocumentTypes], Field(min_length=1)] = Field(description="A list of document types supported by the trading partner for exchange. Each document type identifier value must match the standard list maintained by Avalara, which includes Peppol and other public network document type identifier schemes and values, as well as any approved partner-specific identifiers. The 'value' field must exactly match an entry from the provided document identifier list. Any attempt to submit unsupported document types will result in a validation error. Further, when creating or updating a trading partner, the value provided for the attributes 'name' and 'supportedByAvalara' will be ignored.", alias="supportedDocumentTypes")
    consents: Optional[Consents] = None
    extensions: Optional[List[Extension]] = Field(default=None, description="Optional array used to carry additional metadata or configuration values that may be required by specific networks. When creating or updating a trading partner, the keys provided in the 'extensions' attribute must be selected from a predefined list of supported extensions. Using any unsupported keys will result in a validation error.")
    __properties: ClassVar[List[str]] = ["id", "name", "network", "registrationDate", "identifiers", "addresses", "supportedDocumentTypes", "consents", "extensions"]

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
        """Create an instance of TradingPartner from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "id",
            "network",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in identifiers (list)
        _items = []
        if self.identifiers:
            for _item in self.identifiers:
                if _item:
                    _items.append(_item.to_dict())
            _dict['identifiers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in addresses (list)
        _items = []
        if self.addresses:
            for _item in self.addresses:
                if _item:
                    _items.append(_item.to_dict())
            _dict['addresses'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in supported_document_types (list)
        _items = []
        if self.supported_document_types:
            for _item in self.supported_document_types:
                if _item:
                    _items.append(_item.to_dict())
            _dict['supportedDocumentTypes'] = _items
        # override the default output from pydantic by calling `to_dict()` of consents
        if self.consents:
            _dict['consents'] = self.consents.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in extensions (list)
        _items = []
        if self.extensions:
            for _item in self.extensions:
                if _item:
                    _items.append(_item.to_dict())
            _dict['extensions'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of TradingPartner from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "network": obj.get("network"),
            "registrationDate": obj.get("registrationDate"),
            "identifiers": [Identifier.from_dict(_item) for _item in obj["identifiers"]] if obj.get("identifiers") is not None else None,
            "addresses": [Address.from_dict(_item) for _item in obj["addresses"]] if obj.get("addresses") is not None else None,
            "supportedDocumentTypes": [SupportedDocumentTypes.from_dict(_item) for _item in obj["supportedDocumentTypes"]] if obj.get("supportedDocumentTypes") is not None else None,
            "consents": Consents.from_dict(obj["consents"]) if obj.get("consents") is not None else None,
            "extensions": [Extension.from_dict(_item) for _item in obj["extensions"]] if obj.get("extensions") is not None else None
        })
        return _obj


