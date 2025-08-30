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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class CompanyCreateUpdateRequestModel(BaseModel):
    """
    CompanyCreateUpdateRequestModel
    """ # noqa: E501
    name: Optional[StrictStr] = Field(description="Legal name. Not the DBA name.")
    dba_name: Optional[StrictStr] = Field(default=None, description="Doing Business As (DBA) name or continuation of a long legal name.", alias="dbaName")
    email: Optional[StrictStr] = Field(description="Contact email address. For inquiries by vendors/employees.")
    address: Optional[StrictStr] = Field(description="Address.")
    city: Optional[StrictStr] = Field(description="City.")
    state: Optional[StrictStr] = Field(default=None, description="Two-letter US state or Canadian province code (required for US/CA addresses).")
    zip: Optional[StrictStr] = Field(description="ZIP/postal code.")
    telephone: Optional[StrictStr] = Field(description="Contact phone number (must contain at least 10 digits, max 15 characters).")
    tin: Optional[StrictStr] = Field(description="Federal Tax Identification Number (TIN). EIN/Tax ID (required for US companies).")
    reference_id: Optional[StrictStr] = Field(default=None, description="Internal reference ID. Never shown to any agency or recipient.", alias="referenceId")
    do_tin_match: Optional[StrictBool] = Field(default=None, description="Indicates whether the company authorizes IRS TIN matching.", alias="doTinMatch")
    group_name: Optional[StrictStr] = Field(default=None, description="Group name for organizing companies (creates or finds group by name).", alias="groupName")
    foreign_province: Optional[StrictStr] = Field(default=None, description="Province or region for non-US/CA addresses.", alias="foreignProvince")
    country_code: Optional[StrictStr] = Field(description="Two-letter IRS country code (e.g., 'US', 'CA'), as defined at https://www.irs.gov/e-file-providers/country-codes.", alias="countryCode")
    resend_requests: Optional[StrictBool] = Field(default=None, description="Boolean to enable automatic reminder emails (default: false).", alias="resendRequests")
    resend_interval_days: Optional[StrictInt] = Field(default=None, description="Days between reminder emails (7-365, required if resendRequests is true).", alias="resendIntervalDays")
    max_reminder_attempts: Optional[StrictInt] = Field(default=None, description="Maximum number of reminder attempts (1-52, required if resendRequests is true).", alias="maxReminderAttempts")
    __properties: ClassVar[List[str]] = ["name", "dbaName", "email", "address", "city", "state", "zip", "telephone", "tin", "referenceId", "doTinMatch", "groupName", "foreignProvince", "countryCode", "resendRequests", "resendIntervalDays", "maxReminderAttempts"]

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
        """Create an instance of CompanyCreateUpdateRequestModel from a JSON string"""
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
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if dba_name (nullable) is None
        # and model_fields_set contains the field
        if self.dba_name is None and "dba_name" in self.model_fields_set:
            _dict['dbaName'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

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

        # set to None if telephone (nullable) is None
        # and model_fields_set contains the field
        if self.telephone is None and "telephone" in self.model_fields_set:
            _dict['telephone'] = None

        # set to None if tin (nullable) is None
        # and model_fields_set contains the field
        if self.tin is None and "tin" in self.model_fields_set:
            _dict['tin'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if do_tin_match (nullable) is None
        # and model_fields_set contains the field
        if self.do_tin_match is None and "do_tin_match" in self.model_fields_set:
            _dict['doTinMatch'] = None

        # set to None if group_name (nullable) is None
        # and model_fields_set contains the field
        if self.group_name is None and "group_name" in self.model_fields_set:
            _dict['groupName'] = None

        # set to None if foreign_province (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_province is None and "foreign_province" in self.model_fields_set:
            _dict['foreignProvince'] = None

        # set to None if country_code (nullable) is None
        # and model_fields_set contains the field
        if self.country_code is None and "country_code" in self.model_fields_set:
            _dict['countryCode'] = None

        # set to None if resend_requests (nullable) is None
        # and model_fields_set contains the field
        if self.resend_requests is None and "resend_requests" in self.model_fields_set:
            _dict['resendRequests'] = None

        # set to None if resend_interval_days (nullable) is None
        # and model_fields_set contains the field
        if self.resend_interval_days is None and "resend_interval_days" in self.model_fields_set:
            _dict['resendIntervalDays'] = None

        # set to None if max_reminder_attempts (nullable) is None
        # and model_fields_set contains the field
        if self.max_reminder_attempts is None and "max_reminder_attempts" in self.model_fields_set:
            _dict['maxReminderAttempts'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CompanyCreateUpdateRequestModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "dbaName": obj.get("dbaName"),
            "email": obj.get("email"),
            "address": obj.get("address"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "telephone": obj.get("telephone"),
            "tin": obj.get("tin"),
            "referenceId": obj.get("referenceId"),
            "doTinMatch": obj.get("doTinMatch"),
            "groupName": obj.get("groupName"),
            "foreignProvince": obj.get("foreignProvince"),
            "countryCode": obj.get("countryCode"),
            "resendRequests": obj.get("resendRequests"),
            "resendIntervalDays": obj.get("resendIntervalDays"),
            "maxReminderAttempts": obj.get("maxReminderAttempts")
        })
        return _obj


