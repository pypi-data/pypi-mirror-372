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

    Avalara 1099 & W-9 API Definition
    ## 🔐 Authentication  Generate a **license key** from: *[Avalara Portal](https://www.avalara.com/us/en/signin.html) → Settings → License and API Keys*.  [More on authentication methods](https://developer.avalara.com/avatax-dm-combined-erp/common-setup/authentication/authentication-methods/)  [Test your credentials](https://developer.avalara.com/avatax/test-credentials/)  ## 📘 API & SDK Documentation  [Avalara SDK (.NET) on GitHub](https://github.com/avadev/Avalara-SDK-DotNet#avalarasdk--the-unified-c-library-for-next-gen-avalara-services)  [Code Examples – 1099 API](https://github.com/avadev/Avalara-SDK-DotNet/blob/main/docs/A1099/V2/Class1099IssuersApi.md#call1099issuersget) 

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
from typing import Optional, Set
from typing_extensions import Self

class IntermediaryOrFlowThrough(BaseModel):
    """
    Intermediary or flow-through entity information for tax forms
    """ # noqa: E501
    ein: Optional[StrictStr] = Field(default=None, description="EIN (Employer Identification Number) of the intermediary or flow-through entity")
    chap3_status_code: Optional[StrictStr] = Field(default=None, description="Chapter 3 status code for the intermediary or flow-through entity", alias="chap3StatusCode")
    chap4_status_code: Optional[StrictStr] = Field(default=None, description="Chapter 4 status code for the intermediary or flow-through entity", alias="chap4StatusCode")
    name: Optional[StrictStr] = Field(default=None, description="Name of the intermediary or flow-through entity")
    giin: Optional[StrictStr] = Field(default=None, description="GIIN (Global Intermediary Identification Number) of the intermediary or flow-through entity")
    country_code: Optional[StrictStr] = Field(default=None, description="Country code for the intermediary or flow-through entity", alias="countryCode")
    foreign_tin: Optional[StrictStr] = Field(default=None, description="Foreign TIN of the intermediary or flow-through entity", alias="foreignTin")
    address: Optional[StrictStr] = Field(default=None, description="Address of the intermediary or flow-through entity")
    city: Optional[StrictStr] = Field(default=None, description="City of the intermediary or flow-through entity")
    state: Optional[StrictStr] = Field(default=None, description="State of the intermediary or flow-through entity")
    zip: Optional[StrictStr] = Field(default=None, description="Zip code of the intermediary or flow-through entity")
    __properties: ClassVar[List[str]] = ["ein", "chap3StatusCode", "chap4StatusCode", "name", "giin", "countryCode", "foreignTin", "address", "city", "state", "zip"]

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
        """Create an instance of IntermediaryOrFlowThrough from a JSON string"""
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
        # set to None if ein (nullable) is None
        # and model_fields_set contains the field
        if self.ein is None and "ein" in self.model_fields_set:
            _dict['ein'] = None

        # set to None if chap3_status_code (nullable) is None
        # and model_fields_set contains the field
        if self.chap3_status_code is None and "chap3_status_code" in self.model_fields_set:
            _dict['chap3StatusCode'] = None

        # set to None if chap4_status_code (nullable) is None
        # and model_fields_set contains the field
        if self.chap4_status_code is None and "chap4_status_code" in self.model_fields_set:
            _dict['chap4StatusCode'] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if giin (nullable) is None
        # and model_fields_set contains the field
        if self.giin is None and "giin" in self.model_fields_set:
            _dict['giin'] = None

        # set to None if country_code (nullable) is None
        # and model_fields_set contains the field
        if self.country_code is None and "country_code" in self.model_fields_set:
            _dict['countryCode'] = None

        # set to None if foreign_tin (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_tin is None and "foreign_tin" in self.model_fields_set:
            _dict['foreignTin'] = None

        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

        # set to None if city (nullable) is None
        # and model_fields_set contains the field
        if self.city is None and "city" in self.model_fields_set:
            _dict['city'] = None

        # set to None if state (nullable) is None
        # and model_fields_set contains the field
        if self.state is None and "state" in self.model_fields_set:
            _dict['state'] = None

        # set to None if zip (nullable) is None
        # and model_fields_set contains the field
        if self.zip is None and "zip" in self.model_fields_set:
            _dict['zip'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IntermediaryOrFlowThrough from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "ein": obj.get("ein"),
            "chap3StatusCode": obj.get("chap3StatusCode"),
            "chap4StatusCode": obj.get("chap4StatusCode"),
            "name": obj.get("name"),
            "giin": obj.get("giin"),
            "countryCode": obj.get("countryCode"),
            "foreignTin": obj.get("foreignTin"),
            "address": obj.get("address"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip")
        })
        return _obj


