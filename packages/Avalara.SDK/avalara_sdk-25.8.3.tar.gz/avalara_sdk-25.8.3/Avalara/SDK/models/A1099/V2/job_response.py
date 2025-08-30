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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.A1099.V2.get1099_form200_response import Get1099Form200Response
from typing import Optional, Set
from typing_extensions import Self

class JobResponse(BaseModel):
    """
    Response model for job operations
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="Unique identifier for the job")
    type: Optional[StrictStr] = Field(default=None, description="Job type identifier. Will always be \"update_job\" for bulk upsert operations")
    status: Optional[StrictStr] = Field(default=None, description="Current status of the job (e.g., Success, Failed, InProgress)")
    error_message: Optional[StrictStr] = Field(default=None, description="Error message if the job failed, null otherwise", alias="errorMessage")
    total_processed: Optional[StrictInt] = Field(default=None, description="Total number of forms processed. Value can be 0 or another value based on what the job has available", alias="totalProcessed")
    total_rows: Optional[StrictInt] = Field(default=None, description="Total number of forms in the request. Value can be 0 or another value based on what the job has available", alias="totalRows")
    updated_valid: Optional[StrictInt] = Field(default=None, description="Number of forms updated and valid for e-filing and e-delivery. Value can be 0 or another value based on what the job has available", alias="updatedValid")
    updated_no_email: Optional[StrictInt] = Field(default=None, description="Number of forms updated and valid for e-filing but missing email or email is undeliverable. Value can be 0 or another value based on what the job has available", alias="updatedNoEmail")
    updated_invalid: Optional[StrictInt] = Field(default=None, description="Number of forms updated but invalid for e-filing. Value can be 0 or another value based on what the job has available", alias="updatedInvalid")
    skipped_duplicate: Optional[StrictInt] = Field(default=None, description="Number of forms skipped because they would have updated a record already updated once in the request. Value can be 0 or another value based on what the job has available", alias="skippedDuplicate")
    skipped_invalid: Optional[StrictInt] = Field(default=None, description="Number of forms skipped because they would have made a form invalid and the form is already e-filed or scheduled for e-filing. Value can be 0 or another value based on what the job has available", alias="skippedInvalid")
    skipped_multiple_matches: Optional[StrictInt] = Field(default=None, description="Number of forms skipped because they matched multiple forms. Value can be 0 or another value based on what the job has available", alias="skippedMultipleMatches")
    not_found: Optional[StrictInt] = Field(default=None, description="Number of forms skipped because no matching form or issuer could be found. Value can be 0 or another value based on what the job has available", alias="notFound")
    created_invalid: Optional[StrictInt] = Field(default=None, description="Number of new forms created because no matching form could be found (and `upsert` was true) - with errors. Value can be 0 or another value based on what the job has available", alias="createdInvalid")
    created_no_email: Optional[StrictInt] = Field(default=None, description="Number of new forms created because no matching form could be found (and `upsert` was true) - valid for e-filing but missing email or email is undeliverable. Value can be 0 or another value based on what the job has available", alias="createdNoEmail")
    created_valid: Optional[StrictInt] = Field(default=None, description="Number of new forms created because no matching form could be found (and `upsert` was true) - valid for e-filing and e-delivery. Value can be 0 or another value based on what the job has available", alias="createdValid")
    dry_run: Optional[StrictBool] = Field(default=None, description="Dry run. If `true`, this job only simulates the changes but doesn't actually persist them.", alias="dryRun")
    upsert: Optional[StrictBool] = Field(default=None, description="Upsert. If `true`, this job will first attempt to update existing records if matches can be found. Matches are done in the following order: Form ID, Form Reference ID and tax year, Form TIN and tax year.")
    link: Optional[StrictStr] = Field(default=None, description="Link to access the job details")
    processed_forms: Optional[List[Get1099Form200Response]] = Field(default=None, description="List of processed forms returned when bulk-upsert processes ≤1000 records. Same format as GET /1099/forms response. Only available in bulk-upsert endpoint responses.", alias="processedForms")
    __properties: ClassVar[List[str]] = ["id", "type", "status", "errorMessage", "totalProcessed", "totalRows", "updatedValid", "updatedNoEmail", "updatedInvalid", "skippedDuplicate", "skippedInvalid", "skippedMultipleMatches", "notFound", "createdInvalid", "createdNoEmail", "createdValid", "dryRun", "upsert", "link", "processedForms"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['InProgress', 'Success', 'Failed']):
            raise ValueError("must be one of enum values ('InProgress', 'Success', 'Failed')")
        return value

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
        """Create an instance of JobResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in processed_forms (list)
        _items = []
        if self.processed_forms:
            for _item in self.processed_forms:
                if _item:
                    _items.append(_item.to_dict())
            _dict['processedForms'] = _items
        # set to None if error_message (nullable) is None
        # and model_fields_set contains the field
        if self.error_message is None and "error_message" in self.model_fields_set:
            _dict['errorMessage'] = None

        # set to None if link (nullable) is None
        # and model_fields_set contains the field
        if self.link is None and "link" in self.model_fields_set:
            _dict['link'] = None

        # set to None if processed_forms (nullable) is None
        # and model_fields_set contains the field
        if self.processed_forms is None and "processed_forms" in self.model_fields_set:
            _dict['processedForms'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of JobResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "type": obj.get("type"),
            "status": obj.get("status"),
            "errorMessage": obj.get("errorMessage"),
            "totalProcessed": obj.get("totalProcessed"),
            "totalRows": obj.get("totalRows"),
            "updatedValid": obj.get("updatedValid"),
            "updatedNoEmail": obj.get("updatedNoEmail"),
            "updatedInvalid": obj.get("updatedInvalid"),
            "skippedDuplicate": obj.get("skippedDuplicate"),
            "skippedInvalid": obj.get("skippedInvalid"),
            "skippedMultipleMatches": obj.get("skippedMultipleMatches"),
            "notFound": obj.get("notFound"),
            "createdInvalid": obj.get("createdInvalid"),
            "createdNoEmail": obj.get("createdNoEmail"),
            "createdValid": obj.get("createdValid"),
            "dryRun": obj.get("dryRun"),
            "upsert": obj.get("upsert"),
            "link": obj.get("link"),
            "processedForms": [Get1099Form200Response.from_dict(_item) for _item in obj["processedForms"]] if obj.get("processedForms") is not None else None
        })
        return _obj


