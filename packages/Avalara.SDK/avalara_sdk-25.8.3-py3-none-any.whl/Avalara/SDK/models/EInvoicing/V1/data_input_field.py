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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.EInvoicing.V1.conditional_for_field import ConditionalForField
from Avalara.SDK.models.EInvoicing.V1.data_input_field_not_used_for import DataInputFieldNotUsedFor
from Avalara.SDK.models.EInvoicing.V1.data_input_field_optional_for import DataInputFieldOptionalFor
from Avalara.SDK.models.EInvoicing.V1.data_input_field_required_for import DataInputFieldRequiredFor
from typing import Optional, Set
from typing_extensions import Self

class DataInputField(BaseModel):
    """
    The Data Input Field
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Field UUID")
    field_id: Optional[StrictStr] = Field(default=None, description="Field ID", alias="fieldId")
    applicable_document_roots: Optional[List[Dict[str, Any]]] = Field(default=None, alias="applicableDocumentRoots")
    path: Optional[StrictStr] = Field(default=None, description="Path to this field")
    namespace: Optional[StrictStr] = Field(default=None, description="Namespace of this field")
    field_name: Optional[StrictStr] = Field(default=None, description="Field name", alias="fieldName")
    example_or_fixed_value: Optional[StrictStr] = Field(default=None, description="An example of the content for this field", alias="exampleOrFixedValue")
    accepted_values: Optional[Dict[str, Any]] = Field(default=None, description="An object representing the acceptable values for this field", alias="acceptedValues")
    documentation_link: Optional[StrictStr] = Field(default=None, description="An example of the content for this field", alias="documentationLink")
    description: Optional[StrictStr] = Field(default=None, description="A description of this field")
    is_segment: Optional[StrictBool] = Field(default=None, description="Is this a segment of the schema", alias="isSegment")
    required_for: Optional[DataInputFieldRequiredFor] = Field(default=None, alias="requiredFor")
    conditional_for: Optional[List[ConditionalForField]] = Field(default=None, alias="conditionalFor")
    not_used_for: Optional[DataInputFieldNotUsedFor] = Field(default=None, alias="notUsedFor")
    optional_for: Optional[DataInputFieldOptionalFor] = Field(default=None, alias="optionalFor")
    __properties: ClassVar[List[str]] = ["id", "fieldId", "applicableDocumentRoots", "path", "namespace", "fieldName", "exampleOrFixedValue", "acceptedValues", "documentationLink", "description", "isSegment", "requiredFor", "conditionalFor", "notUsedFor", "optionalFor"]

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
        """Create an instance of DataInputField from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of required_for
        if self.required_for:
            _dict['requiredFor'] = self.required_for.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in conditional_for (list)
        _items = []
        if self.conditional_for:
            for _item in self.conditional_for:
                if _item:
                    _items.append(_item.to_dict())
            _dict['conditionalFor'] = _items
        # override the default output from pydantic by calling `to_dict()` of not_used_for
        if self.not_used_for:
            _dict['notUsedFor'] = self.not_used_for.to_dict()
        # override the default output from pydantic by calling `to_dict()` of optional_for
        if self.optional_for:
            _dict['optionalFor'] = self.optional_for.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DataInputField from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "fieldId": obj.get("fieldId"),
            "applicableDocumentRoots": obj.get("applicableDocumentRoots"),
            "path": obj.get("path"),
            "namespace": obj.get("namespace"),
            "fieldName": obj.get("fieldName"),
            "exampleOrFixedValue": obj.get("exampleOrFixedValue"),
            "acceptedValues": obj.get("acceptedValues"),
            "documentationLink": obj.get("documentationLink"),
            "description": obj.get("description"),
            "isSegment": obj.get("isSegment"),
            "requiredFor": DataInputFieldRequiredFor.from_dict(obj["requiredFor"]) if obj.get("requiredFor") is not None else None,
            "conditionalFor": [ConditionalForField.from_dict(_item) for _item in obj["conditionalFor"]] if obj.get("conditionalFor") is not None else None,
            "notUsedFor": DataInputFieldNotUsedFor.from_dict(obj["notUsedFor"]) if obj.get("notUsedFor") is not None else None,
            "optionalFor": DataInputFieldOptionalFor.from_dict(obj["optionalFor"]) if obj.get("optionalFor") is not None else None
        })
        return _obj


