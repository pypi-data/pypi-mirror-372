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

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from Avalara.SDK.models.EInvoicing.V1.extension import Extension
from typing import Optional, Set
from typing_extensions import Self

class SupportedDocumentTypes(BaseModel):
    """
    SupportedDocumentTypes
    """ # noqa: E501
    name: Optional[Annotated[str, Field(strict=True, max_length=250)]] = Field(default=None, description="Document type name.")
    value: Annotated[str, Field(strict=True, max_length=500)] = Field(description="Document type value.")
    supported_by_trading_partner: StrictBool = Field(description="Does trading partner support receiving this document type.", alias="supportedByTradingPartner")
    supported_by_avalara: Optional[StrictBool] = Field(default=None, description="Does avalara support exchanging this document type.", alias="supportedByAvalara")
    extensions: Optional[List[Extension]] = Field(default=None, description="Optional array used to carry additional metadata or configuration values that may be required by specific document types. When creating or updating a trading partner, the keys provided in the 'extensions' attribute must be selected from a predefined list of supported extensions. Using any unsupported keys will result in a validation error.")
    __properties: ClassVar[List[str]] = ["name", "value", "supportedByTradingPartner", "supportedByAvalara", "extensions"]

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
        """Create an instance of SupportedDocumentTypes from a JSON string"""
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
        """Create an instance of SupportedDocumentTypes from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "value": obj.get("value"),
            "supportedByTradingPartner": obj.get("supportedByTradingPartner"),
            "supportedByAvalara": obj.get("supportedByAvalara"),
            "extensions": [Extension.from_dict(_item) for _item in obj["extensions"]] if obj.get("extensions") is not None else None
        })
        return _obj


