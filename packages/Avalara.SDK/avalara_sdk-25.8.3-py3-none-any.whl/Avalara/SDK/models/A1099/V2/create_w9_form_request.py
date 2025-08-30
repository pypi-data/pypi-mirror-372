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
import json
import pprint
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from Avalara.SDK.models.A1099.V2.w4_form_request import W4FormRequest
from Avalara.SDK.models.A1099.V2.w8_ben_e_form_request import W8BenEFormRequest
from Avalara.SDK.models.A1099.V2.w8_ben_form_request import W8BenFormRequest
from Avalara.SDK.models.A1099.V2.w8_imy_form_request import W8ImyFormRequest
from Avalara.SDK.models.A1099.V2.w9_form_request import W9FormRequest
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

CREATEW9FORMREQUEST_ONE_OF_SCHEMAS = ["W4FormRequest", "W8BenEFormRequest", "W8BenFormRequest", "W8ImyFormRequest", "W9FormRequest"]

class CreateW9FormRequest(BaseModel):
    """
    CreateW9FormRequest
    """
    # data type: W9FormRequest
    oneof_schema_1_validator: Optional[W9FormRequest] = None
    # data type: W8ImyFormRequest
    oneof_schema_2_validator: Optional[W8ImyFormRequest] = None
    # data type: W8BenEFormRequest
    oneof_schema_3_validator: Optional[W8BenEFormRequest] = None
    # data type: W8BenFormRequest
    oneof_schema_4_validator: Optional[W8BenFormRequest] = None
    # data type: W4FormRequest
    oneof_schema_5_validator: Optional[W4FormRequest] = None
    actual_instance: Optional[Union[W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest]] = None
    one_of_schemas: Set[str] = { "W4FormRequest", "W8BenEFormRequest", "W8BenFormRequest", "W8ImyFormRequest", "W9FormRequest" }

    model_config = ConfigDict(
        validate_assignment=True,
        protected_namespaces=(),
    )


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = CreateW9FormRequest.model_construct()
        error_messages = []
        match = 0
        # validate data type: W9FormRequest
        if not isinstance(v, W9FormRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `W9FormRequest`")
        else:
            match += 1
        # validate data type: W8ImyFormRequest
        if not isinstance(v, W8ImyFormRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `W8ImyFormRequest`")
        else:
            match += 1
        # validate data type: W8BenEFormRequest
        if not isinstance(v, W8BenEFormRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `W8BenEFormRequest`")
        else:
            match += 1
        # validate data type: W8BenFormRequest
        if not isinstance(v, W8BenFormRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `W8BenFormRequest`")
        else:
            match += 1
        # validate data type: W4FormRequest
        if not isinstance(v, W4FormRequest):
            error_messages.append(f"Error! Input type `{type(v)}` is not `W4FormRequest`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in CreateW9FormRequest with oneOf schemas: W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in CreateW9FormRequest with oneOf schemas: W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: Union[str, Dict[str, Any]]) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into W9FormRequest
        try:
            instance.actual_instance = W9FormRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into W8ImyFormRequest
        try:
            instance.actual_instance = W8ImyFormRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into W8BenEFormRequest
        try:
            instance.actual_instance = W8BenEFormRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into W8BenFormRequest
        try:
            instance.actual_instance = W8BenFormRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into W4FormRequest
        try:
            instance.actual_instance = W4FormRequest.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into CreateW9FormRequest with oneOf schemas: W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into CreateW9FormRequest with oneOf schemas: W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        if hasattr(self.actual_instance, "to_json") and callable(self.actual_instance.to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Optional[Union[Dict[str, Any], W4FormRequest, W8BenEFormRequest, W8BenFormRequest, W8ImyFormRequest, W9FormRequest]]:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        if hasattr(self.actual_instance, "to_dict") and callable(self.actual_instance.to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())


