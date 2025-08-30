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

from datetime import datetime
from importlib import import_module
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from Avalara.SDK.models.A1099.V2.entry_status_response import EntryStatusResponse
from typing import Optional, Set
from typing_extensions import Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Avalara.SDK.models.A1099.V2.w4_form_response import W4FormResponse
    from Avalara.SDK.models.A1099.V2.w8_ben_e_form_response import W8BenEFormResponse
    from Avalara.SDK.models.A1099.V2.w8_ben_form_response import W8BenFormResponse
    from Avalara.SDK.models.A1099.V2.w8_imy_form_response import W8ImyFormResponse
    from Avalara.SDK.models.A1099.V2.w9_form_response import W9FormResponse

class W9FormBaseResponse(BaseModel):
    """
    W9FormBaseResponse
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The unique identifier for the form.")
    entry_status: Optional[EntryStatusResponse] = Field(default=None, description="The entry status information for the form.", alias="entryStatus")
    reference_id: Optional[StrictStr] = Field(default=None, description="A reference identifier for the form.", alias="referenceId")
    company_id: Optional[StrictStr] = Field(default=None, description="The ID of the associated company.", alias="companyId")
    display_name: Optional[StrictStr] = Field(default=None, description="The display name associated with the form.", alias="displayName")
    email: Optional[StrictStr] = Field(default=None, description="The email address of the individual associated with the form.")
    archived: Optional[StrictBool] = Field(default=None, description="Indicates whether the form is archived.")
    ancestor_id: Optional[StrictStr] = Field(default=None, description="Form ID of previous version.", alias="ancestorId")
    signature: Optional[StrictStr] = Field(default=None, description="The signature of the form.")
    signed_date: Optional[datetime] = Field(default=None, description="The date the form was signed.", alias="signedDate")
    e_delivery_consented_at: Optional[datetime] = Field(default=None, description="The date when e-delivery was consented.", alias="eDeliveryConsentedAt")
    created_at: Optional[datetime] = Field(default=None, description="The creation date of the form.", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="The last updated date of the form.", alias="updatedAt")
    type: Optional[StrictStr] = Field(default=None, description="The type of the response object.")
    __properties: ClassVar[List[str]] = []

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    # JSON field name that stores the object type
    __discriminator_property_name: ClassVar[str] = 'type'

    # discriminator mappings
    __discriminator_value_class_map: ClassVar[Dict[str, str]] = {
        'W4FormResponse': 'W4FormResponse','W8BenEFormResponse': 'W8BenEFormResponse','W8BenFormResponse': 'W8BenFormResponse','W8ImyFormResponse': 'W8ImyFormResponse','W9FormResponse': 'W9FormResponse'
    }

    @classmethod
    def get_discriminator_value(cls, obj: Dict[str, Any]) -> Optional[str]:
        """Returns the discriminator value (object type) of the data"""
        discriminator_value = obj[cls.__discriminator_property_name]
        if discriminator_value:
            return cls.__discriminator_value_class_map.get(discriminator_value)
        else:
            return None

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Union[W4FormResponse, W8BenEFormResponse, W8BenFormResponse, W8ImyFormResponse, W9FormResponse]]:
        """Create an instance of W9FormBaseResponse from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> Optional[Union[W4FormResponse, W8BenEFormResponse, W8BenFormResponse, W8ImyFormResponse, W9FormResponse]]:
        """Create an instance of W9FormBaseResponse from a dict"""
        # look up the object type based on discriminator mapping
        object_type = cls.get_discriminator_value(obj)
        if object_type ==  'W4FormResponse':
            return import_module("Avalara.SDK.models.A1099.V2.w4_form_response").W4FormResponse.from_dict(obj)
        if object_type ==  'W8BenEFormResponse':
            return import_module("Avalara.SDK.models.A1099.V2.w8_ben_e_form_response").W8BenEFormResponse.from_dict(obj)
        if object_type ==  'W8BenFormResponse':
            return import_module("Avalara.SDK.models.A1099.V2.w8_ben_form_response").W8BenFormResponse.from_dict(obj)
        if object_type ==  'W8ImyFormResponse':
            return import_module("Avalara.SDK.models.A1099.V2.w8_imy_form_response").W8ImyFormResponse.from_dict(obj)
        if object_type ==  'W9FormResponse':
            return import_module("Avalara.SDK.models.A1099.V2.w9_form_response").W9FormResponse.from_dict(obj)

        raise ValueError("W9FormBaseResponse failed to lookup discriminator value from " +
                            json.dumps(obj) + ". Discriminator property name: " + cls.__discriminator_property_name +
                            ", mapping: " + json.dumps(cls.__discriminator_value_class_map))


