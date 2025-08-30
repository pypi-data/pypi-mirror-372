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

from pydantic import ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from Avalara.SDK.models.A1099.V2.entry_status_response import EntryStatusResponse
from Avalara.SDK.models.A1099.V2.w9_form_base_response import W9FormBaseResponse
from typing import Optional, Set
from typing_extensions import Self

class W4FormResponse(W9FormBaseResponse):
    """
    W4FormResponse
    """ # noqa: E501
    employee_first_name: Optional[StrictStr] = Field(default=None, description="The first name of the employee.", alias="employeeFirstName")
    employee_middle_name: Optional[StrictStr] = Field(default=None, description="The middle name of the employee.", alias="employeeMiddleName")
    employee_last_name: Optional[StrictStr] = Field(default=None, description="The last name of the employee.", alias="employeeLastName")
    employee_name_suffix: Optional[StrictStr] = Field(default=None, description="The name suffix of the employee.", alias="employeeNameSuffix")
    tin_type: Optional[StrictStr] = Field(default=None, description="The type of TIN provided.", alias="tinType")
    tin: Optional[StrictStr] = Field(default=None, description="The taxpayer identification number (TIN).")
    address: Optional[StrictStr] = Field(default=None, description="The address of the employee.")
    city: Optional[StrictStr] = Field(default=None, description="The city of residence of the employee.")
    state: Optional[StrictStr] = Field(default=None, description="The state of residence of the employee.")
    zip: Optional[StrictStr] = Field(default=None, description="The ZIP code of residence of the employee.")
    marital_status: Optional[StrictStr] = Field(default=None, description="The marital status of the employee.", alias="maritalStatus")
    last_name_differs: Optional[StrictBool] = Field(default=None, description="Indicates whether the last name differs from prior records.", alias="lastNameDiffers")
    num_allowances: Optional[StrictInt] = Field(default=None, description="The number of allowances claimed by the employee.", alias="numAllowances")
    other_dependents: Optional[StrictInt] = Field(default=None, description="The number of dependents other than allowances.", alias="otherDependents")
    non_job_income: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of non-job income.", alias="nonJobIncome")
    deductions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of deductions claimed.")
    additional_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The additional amount withheld.", alias="additionalWithheld")
    exempt_from_withholding: Optional[StrictBool] = Field(default=None, description="Indicates whether the employee is exempt from withholding.", alias="exemptFromWithholding")
    office_code: Optional[StrictStr] = Field(default=None, description="The office code associated with the form.", alias="officeCode")
    __properties: ClassVar[List[str]] = ["id", "entryStatus", "referenceId", "companyId", "displayName", "email", "archived", "ancestorId", "signature", "signedDate", "eDeliveryConsentedAt", "createdAt", "updatedAt", "type"]

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
        """Create an instance of W4FormResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of entry_status
        if self.entry_status:
            _dict['entryStatus'] = self.entry_status.to_dict()
        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if ancestor_id (nullable) is None
        # and model_fields_set contains the field
        if self.ancestor_id is None and "ancestor_id" in self.model_fields_set:
            _dict['ancestorId'] = None

        # set to None if signature (nullable) is None
        # and model_fields_set contains the field
        if self.signature is None and "signature" in self.model_fields_set:
            _dict['signature'] = None

        # set to None if signed_date (nullable) is None
        # and model_fields_set contains the field
        if self.signed_date is None and "signed_date" in self.model_fields_set:
            _dict['signedDate'] = None

        # set to None if e_delivery_consented_at (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_consented_at is None and "e_delivery_consented_at" in self.model_fields_set:
            _dict['eDeliveryConsentedAt'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of W4FormResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "entryStatus": EntryStatusResponse.from_dict(obj["entryStatus"]) if obj.get("entryStatus") is not None else None,
            "referenceId": obj.get("referenceId"),
            "companyId": obj.get("companyId"),
            "displayName": obj.get("displayName"),
            "email": obj.get("email"),
            "archived": obj.get("archived"),
            "ancestorId": obj.get("ancestorId"),
            "signature": obj.get("signature"),
            "signedDate": obj.get("signedDate"),
            "eDeliveryConsentedAt": obj.get("eDeliveryConsentedAt"),
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt"),
            "type": obj.get("type")
        })
        return _obj


