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
from Avalara.SDK.models.EInvoicing.V1.mandate_data_input_field_namespace import MandateDataInputFieldNamespace
from typing import Optional, Set
from typing_extensions import Self

class MandateDataInputField(BaseModel):
    """
    The Data Input Field
    """ # noqa: E501
    field_id: Optional[StrictStr] = Field(default=None, description="Field ID", alias="fieldId")
    document_type: Optional[StrictStr] = Field(default=None, description="The document type", alias="documentType")
    document_version: Optional[StrictStr] = Field(default=None, description="The document version", alias="documentVersion")
    path: Optional[StrictStr] = Field(default=None, description="Path to this field")
    path_type: Optional[StrictStr] = Field(default=None, description="The type of path", alias="pathType")
    field_name: Optional[StrictStr] = Field(default=None, description="Field name", alias="fieldName")
    namespace: Optional[MandateDataInputFieldNamespace] = None
    example_or_fixed_value: Optional[StrictStr] = Field(default=None, description="An example of the content for this field", alias="exampleOrFixedValue")
    accepted_values: Optional[List[StrictStr]] = Field(default=None, description="An Array representing the acceptable values for this field", alias="acceptedValues")
    documentation_link: Optional[StrictStr] = Field(default=None, description="An example of the content for this field", alias="documentationLink")
    data_type: Optional[StrictStr] = Field(default=None, description="The data type of this field.", alias="dataType")
    description: Optional[StrictStr] = Field(default=None, description="A description of this field")
    optionality: Optional[StrictStr] = Field(default=None, description="Determines if the field if Required/Conditional/Optional or not required.")
    cardinality: Optional[StrictStr] = Field(default=None, description="Represents the number of times an element can appear within the document")
    __properties: ClassVar[List[str]] = ["fieldId", "documentType", "documentVersion", "path", "pathType", "fieldName", "namespace", "exampleOrFixedValue", "acceptedValues", "documentationLink", "dataType", "description", "optionality", "cardinality"]

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
        """Create an instance of MandateDataInputField from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of namespace
        if self.namespace:
            _dict['namespace'] = self.namespace.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MandateDataInputField from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "fieldId": obj.get("fieldId"),
            "documentType": obj.get("documentType"),
            "documentVersion": obj.get("documentVersion"),
            "path": obj.get("path"),
            "pathType": obj.get("pathType"),
            "fieldName": obj.get("fieldName"),
            "namespace": MandateDataInputFieldNamespace.from_dict(obj["namespace"]) if obj.get("namespace") is not None else None,
            "exampleOrFixedValue": obj.get("exampleOrFixedValue"),
            "acceptedValues": obj.get("acceptedValues"),
            "documentationLink": obj.get("documentationLink"),
            "dataType": obj.get("dataType"),
            "description": obj.get("description"),
            "optionality": obj.get("optionality"),
            "cardinality": obj.get("cardinality")
        })
        return _obj


