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

class SubmitDocumentMetadata(BaseModel):
    """
    Key value pairs of metadata for a document submission <br><pre>{  \"workflowId\": \"partner-einvoicing\", \"dataFormat\": \"ubl-invoice\", \"dataFormatVersion\": \"2.1\", \"countryCode\": \"SA\", \"countryMandate\": \"SA-Phase1-B2B\" }</pre> <br> 
    """ # noqa: E501
    workflow_id: StrictStr = Field(description="Specifies a unique ID for this workflow.", alias="workflowId")
    data_format: StrictStr = Field(description="Specifies the data format for this workflow.", alias="dataFormat")
    data_format_version: StrictStr = Field(description="Specifies the data format version number.", alias="dataFormatVersion")
    output_data_format: Optional[StrictStr] = Field(default=None, description="Specifies the format of the output document to be generated for the recipient. This format should be chosen based on the recipient's preferences or requirements as defined by applicable e-invoicing regulations. When not specified for mandates that don't require a specific output format, the system will use the default format defined for that mandate.", alias="outputDataFormat")
    output_data_format_version: Optional[StrictStr] = Field(default=None, description="Specifies the version of the selected output document format", alias="outputDataFormatVersion")
    country_code: StrictStr = Field(description="The two-letter ISO-3166 country code for the country where the document is being submitted", alias="countryCode")
    country_mandate: StrictStr = Field(description="The e-invoicing mandate for the specified country.", alias="countryMandate")
    __properties: ClassVar[List[str]] = ["workflowId", "dataFormat", "dataFormatVersion", "outputDataFormat", "outputDataFormatVersion", "countryCode", "countryMandate"]

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
        """Create an instance of SubmitDocumentMetadata from a JSON string"""
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
        """Create an instance of SubmitDocumentMetadata from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "workflowId": obj.get("workflowId"),
            "dataFormat": obj.get("dataFormat"),
            "dataFormatVersion": obj.get("dataFormatVersion"),
            "outputDataFormat": obj.get("outputDataFormat"),
            "outputDataFormatVersion": obj.get("outputDataFormatVersion"),
            "countryCode": obj.get("countryCode"),
            "countryMandate": obj.get("countryMandate")
        })
        return _obj


