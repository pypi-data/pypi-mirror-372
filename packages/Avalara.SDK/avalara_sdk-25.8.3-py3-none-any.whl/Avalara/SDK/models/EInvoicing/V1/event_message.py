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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.EInvoicing.V1.signature_value_signature import SignatureValueSignature
from typing import Optional, Set
from typing_extensions import Self

class EventMessage(BaseModel):
    """
    EventMessage
    """ # noqa: E501
    message: Dict[str, Any] = Field(description="Event-specific information")
    signature: SignatureValueSignature
    tenant_id: StrictStr = Field(description="Tenant ID of the event", alias="tenantId")
    correlation_id: Optional[StrictStr] = Field(default=None, description="The correlation ID used by Avalara to aid in tracing through to provenance of this event massage.", alias="correlationId")
    system_code: StrictStr = Field(description="The Avalara registered code for the system. See <a href=\"https://avalara.atlassian.net/wiki/spaces/AIM/pages/637250338966/Taxonomy+Avalara+Systems\">Taxonomy&#58; Avalara Systems</a>", alias="systemCode")
    event_name: StrictStr = Field(description="Type of the event", alias="eventName")
    event_version: Optional[StrictStr] = Field(default=None, description="Version of the included payload.", alias="eventVersion")
    receipt_timestamp: Optional[datetime] = Field(default=None, description="Timestamp when the event was received by the dispatch service.", alias="receiptTimestamp")
    __properties: ClassVar[List[str]] = ["message", "signature", "tenantId", "correlationId", "systemCode", "eventName", "eventVersion", "receiptTimestamp"]

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
        """Create an instance of EventMessage from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of signature
        if self.signature:
            _dict['signature'] = self.signature.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EventMessage from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "message": obj.get("message"),
            "signature": SignatureValueSignature.from_dict(obj["signature"]) if obj.get("signature") is not None else None,
            "tenantId": obj.get("tenantId"),
            "correlationId": obj.get("correlationId"),
            "systemCode": obj.get("systemCode"),
            "eventName": obj.get("eventName"),
            "eventVersion": obj.get("eventVersion"),
            "receiptTimestamp": obj.get("receiptTimestamp")
        })
        return _obj


