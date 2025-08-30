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

class DocumentSummary(BaseModel):
    """
    Displays a summary of information about the document
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The unique ID for this document")
    company_id: Optional[StrictStr] = Field(default=None, description="Unique identifier that represents the company within the system.", alias="companyId")
    process_date_time: Optional[StrictStr] = Field(default=None, description="The date and time when the document was processed, displayed in the format YYYY-MM-DDThh:mm:ss", alias="processDateTime")
    status: Optional[StrictStr] = Field(default=None, description="The Document status")
    supplier_name: Optional[StrictStr] = Field(default=None, description="The name of the supplier in the transaction", alias="supplierName")
    customer_name: Optional[StrictStr] = Field(default=None, description="The name of the customer in the transaction", alias="customerName")
    document_type: Optional[StrictStr] = Field(default=None, description="The document type", alias="documentType")
    document_version: Optional[StrictStr] = Field(default=None, description="The document version", alias="documentVersion")
    document_number: Optional[StrictStr] = Field(default=None, description="The document number", alias="documentNumber")
    document_date: Optional[StrictStr] = Field(default=None, description="The document issue date", alias="documentDate")
    flow: Optional[StrictStr] = Field(default=None, description="The document direction, where issued = `out` and received = `in`")
    country_code: Optional[StrictStr] = Field(default=None, description="The two-letter ISO-3166 country code for the country where the document is being submitted", alias="countryCode")
    country_mandate: Optional[StrictStr] = Field(default=None, description="The e-invoicing mandate for the specified country", alias="countryMandate")
    interface: Optional[StrictStr] = Field(default=None, description="The interface where the document is sent")
    receiver: Optional[StrictStr] = Field(default=None, description="The document recipient based on the interface")
    __properties: ClassVar[List[str]] = ["id", "companyId", "processDateTime", "status", "supplierName", "customerName", "documentType", "documentVersion", "documentNumber", "documentDate", "flow", "countryCode", "countryMandate", "interface", "receiver"]

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
        """Create an instance of DocumentSummary from a JSON string"""
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
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DocumentSummary from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "companyId": obj.get("companyId"),
            "processDateTime": obj.get("processDateTime"),
            "status": obj.get("status"),
            "supplierName": obj.get("supplierName"),
            "customerName": obj.get("customerName"),
            "documentType": obj.get("documentType"),
            "documentVersion": obj.get("documentVersion"),
            "documentNumber": obj.get("documentNumber"),
            "documentDate": obj.get("documentDate"),
            "flow": obj.get("flow"),
            "countryCode": obj.get("countryCode"),
            "countryMandate": obj.get("countryMandate"),
            "interface": obj.get("interface"),
            "receiver": obj.get("receiver")
        })
        return _obj


