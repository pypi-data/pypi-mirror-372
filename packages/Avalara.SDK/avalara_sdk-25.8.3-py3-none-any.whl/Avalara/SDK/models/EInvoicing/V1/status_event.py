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
from typing import Optional, Set
from typing_extensions import Self

class StatusEvent(BaseModel):
    """
    Displays when a status event occurred
    """ # noqa: E501
    event_date_time: Optional[StrictStr] = Field(default=None, description="The date and time when the status event occured, displayed in the format YYYY-MM-DDThh:mm:ss", alias="eventDateTime")
    message: Optional[StrictStr] = Field(default=None, description="A message describing the status event")
    response_key: Optional[StrictStr] = Field(default=None, description=" The type of number or acknowledgement returned by the tax authority (if applicable). For example, it could be an identification key, acknowledgement code, or any other relevant identifier.", alias="responseKey")
    response_value: Optional[StrictStr] = Field(default=None, description="The corresponding value associated with the response key. This value is provided by the tax authority in response to the event.", alias="responseValue")
    __properties: ClassVar[List[str]] = ["eventDateTime", "message", "responseKey", "responseValue"]

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
        """Create an instance of StatusEvent from a JSON string"""
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
        # set to None if response_key (nullable) is None
        # and model_fields_set contains the field
        if self.response_key is None and "response_key" in self.model_fields_set:
            _dict['responseKey'] = None

        # set to None if response_value (nullable) is None
        # and model_fields_set contains the field
        if self.response_value is None and "response_value" in self.model_fields_set:
            _dict['responseValue'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of StatusEvent from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "eventDateTime": obj.get("eventDateTime"),
            "message": obj.get("message"),
            "responseKey": obj.get("responseKey"),
            "responseValue": obj.get("responseValue")
        })
        return _obj


