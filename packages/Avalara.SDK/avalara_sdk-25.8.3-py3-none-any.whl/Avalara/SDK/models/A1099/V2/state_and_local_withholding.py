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

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class StateAndLocalWithholding(BaseModel):
    """
    StateAndLocalWithholding
    """ # noqa: E501
    state_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount of state tax that was withheld", alias="stateTaxWithheld")
    state: Optional[StrictStr] = Field(default=None, description="US state")
    state_id_number: Optional[StrictStr] = Field(default=None, description="State ID number of the entity issuing the form", alias="stateIdNumber")
    state_income: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount of state income", alias="stateIncome")
    local_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount of local tax that was withheld", alias="localTaxWithheld")
    locality: Optional[StrictStr] = Field(default=None, description="Locality name")
    locality_id_number: Optional[StrictStr] = Field(default=None, description="Locality ID number of the entity issuing the form", alias="localityIdNumber")
    local_income: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount of local income", alias="localIncome")
    __properties: ClassVar[List[str]] = ["stateTaxWithheld", "state", "stateIdNumber", "stateIncome", "localTaxWithheld", "locality", "localityIdNumber", "localIncome"]

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
        """Create an instance of StateAndLocalWithholding from a JSON string"""
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
        # set to None if state_tax_withheld (nullable) is None
        # and model_fields_set contains the field
        if self.state_tax_withheld is None and "state_tax_withheld" in self.model_fields_set:
            _dict['stateTaxWithheld'] = None

        # set to None if state (nullable) is None
        # and model_fields_set contains the field
        if self.state is None and "state" in self.model_fields_set:
            _dict['state'] = None

        # set to None if state_id_number (nullable) is None
        # and model_fields_set contains the field
        if self.state_id_number is None and "state_id_number" in self.model_fields_set:
            _dict['stateIdNumber'] = None

        # set to None if state_income (nullable) is None
        # and model_fields_set contains the field
        if self.state_income is None and "state_income" in self.model_fields_set:
            _dict['stateIncome'] = None

        # set to None if local_tax_withheld (nullable) is None
        # and model_fields_set contains the field
        if self.local_tax_withheld is None and "local_tax_withheld" in self.model_fields_set:
            _dict['localTaxWithheld'] = None

        # set to None if locality (nullable) is None
        # and model_fields_set contains the field
        if self.locality is None and "locality" in self.model_fields_set:
            _dict['locality'] = None

        # set to None if locality_id_number (nullable) is None
        # and model_fields_set contains the field
        if self.locality_id_number is None and "locality_id_number" in self.model_fields_set:
            _dict['localityIdNumber'] = None

        # set to None if local_income (nullable) is None
        # and model_fields_set contains the field
        if self.local_income is None and "local_income" in self.model_fields_set:
            _dict['localIncome'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of StateAndLocalWithholding from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "stateTaxWithheld": obj.get("stateTaxWithheld"),
            "state": obj.get("state"),
            "stateIdNumber": obj.get("stateIdNumber"),
            "stateIncome": obj.get("stateIncome"),
            "localTaxWithheld": obj.get("localTaxWithheld"),
            "locality": obj.get("locality"),
            "localityIdNumber": obj.get("localityIdNumber"),
            "localIncome": obj.get("localIncome")
        })
        return _obj


