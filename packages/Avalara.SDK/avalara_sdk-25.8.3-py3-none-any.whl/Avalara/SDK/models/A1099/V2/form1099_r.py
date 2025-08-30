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

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from Avalara.SDK.models.A1099.V2.form1099_status_detail import Form1099StatusDetail
from Avalara.SDK.models.A1099.V2.state_and_local_withholding import StateAndLocalWithholding
from Avalara.SDK.models.A1099.V2.state_efile_status_detail import StateEfileStatusDetail
from Avalara.SDK.models.A1099.V2.validation_error import ValidationError
from typing import Optional, Set
from typing_extensions import Self

class Form1099R(BaseModel):
    """
    Form 1099-R: Distributions From Pensions, Annuities, Retirement or Profit-Sharing Plans, IRAs, Insurance Contracts, etc.
    """ # noqa: E501
    gross_distribution: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Gross distribution", alias="grossDistribution")
    taxable_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Taxable amount", alias="taxableAmount")
    taxable_amount_not_determined: Optional[StrictBool] = Field(default=None, description="Taxable amount not determined", alias="taxableAmountNotDetermined")
    total_distribution_determined: Optional[StrictBool] = Field(default=None, description="Total distribution", alias="totalDistributionDetermined")
    capital_gain: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Capital gain (included in Box 2a)", alias="capitalGain")
    federal_income_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Federal income tax withheld", alias="federalIncomeTaxWithheld")
    employee_contributions_or_designated_roth_or_insurance_premiums: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Employee contributions/Designated Roth contributions or insurance premiums", alias="employeeContributionsOrDesignatedRothOrInsurancePremiums")
    net_unrealized_appreciation_in_employer_securities: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Net unrealized appreciation in employer's securities", alias="netUnrealizedAppreciationInEmployerSecurities")
    distribution_code: Optional[StrictStr] = Field(default=None, description="Distribution code", alias="distributionCode")
    second_distribution_code: Optional[StrictStr] = Field(default=None, description="Second distribution code", alias="secondDistributionCode")
    ira_sep_simple: Optional[StrictBool] = Field(default=None, description="IRA/SEP/SIMPLE", alias="iraSepSimple")
    traditional_ira_sep_simple_or_roth_conversion_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Traditional IRA/SEP/SIMPLE or Roth conversion amount", alias="traditionalIraSepSimpleOrRothConversionAmount")
    other_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Other amount", alias="otherAmount")
    other_percentage: Optional[StrictStr] = Field(default=None, description="Other percentage", alias="otherPercentage")
    total_distribution_percentage: Optional[StrictStr] = Field(default=None, description="Total distribution percentage", alias="totalDistributionPercentage")
    total_employee_contributions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Total employee contributions", alias="totalEmployeeContributions")
    amount_allocable_to_irr_within5_years: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount allocable to IRR within 5 years", alias="amountAllocableToIrrWithin5Years")
    first_year_of_designated_roth_contribution: Optional[StrictStr] = Field(default=None, description="First year of designated Roth contribution", alias="firstYearOfDesignatedRothContribution")
    date_of_payment: Optional[date] = Field(default=None, description="Date of payment", alias="dateOfPayment")
    fatca_filing_requirement: Optional[StrictBool] = Field(default=None, description="FATCA filing requirement", alias="fatcaFilingRequirement")
    type: StrictStr = Field(description="Form type")
    id: Optional[StrictStr] = Field(default=None, description="Form ID. Unique identifier set when the record is created.")
    issuer_id: Optional[StrictStr] = Field(default=None, description="Issuer ID - only required when creating forms", alias="issuerId")
    issuer_reference_id: Optional[StrictStr] = Field(default=None, description="Issuer Reference ID - only required when creating forms", alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, description="Issuer TIN - readonly", alias="issuerTin")
    tax_year: Optional[StrictInt] = Field(default=None, description="Tax Year - only required when creating forms", alias="taxYear")
    reference_id: Optional[StrictStr] = Field(default=None, description="Internal reference ID. Never shown to any agency or recipient.", alias="referenceId")
    tin: Optional[StrictStr] = Field(default=None, description="Recipient's Federal Tax Identification Number (TIN).")
    recipient_name: Optional[StrictStr] = Field(description="Recipient name", alias="recipientName")
    tin_type: Optional[StrictStr] = Field(default=None, description="Type of TIN (Tax ID Number)", alias="tinType")
    recipient_second_name: Optional[StrictStr] = Field(default=None, description="Recipient second name", alias="recipientSecondName")
    address: Optional[StrictStr] = Field(description="Address.")
    address2: Optional[StrictStr] = Field(default=None, description="Address line 2.")
    city: Optional[StrictStr] = Field(description="City.")
    state: Optional[StrictStr] = Field(default=None, description="Two-letter US state or Canadian province code (required for US/CA addresses).")
    zip: Optional[StrictStr] = Field(default=None, description="ZIP/postal code.")
    email: Optional[StrictStr] = Field(default=None, description="Recipient's Contact email address.")
    account_number: Optional[StrictStr] = Field(default=None, description="Account number", alias="accountNumber")
    office_code: Optional[StrictStr] = Field(default=None, description="Office code", alias="officeCode")
    non_us_province: Optional[StrictStr] = Field(default=None, description="Province or region for non-US/CA addresses.", alias="nonUsProvince")
    country_code: Optional[StrictStr] = Field(description="Two-letter IRS country code (e.g., 'US', 'CA'), as defined at https://www.irs.gov/e-file-providers/country-codes.", alias="countryCode")
    federal_efile_date: Optional[date] = Field(default=None, description="Date when federal e-filing should be scheduled for this form", alias="federalEfileDate")
    postal_mail: Optional[StrictBool] = Field(default=None, description="Boolean indicating that postal mailing to the recipient should be scheduled for this form", alias="postalMail")
    state_efile_date: Optional[date] = Field(default=None, description="Date when state e-filing should be scheduled for this form", alias="stateEfileDate")
    recipient_edelivery_date: Optional[date] = Field(default=None, description="Date when recipient e-delivery should be scheduled for this form", alias="recipientEdeliveryDate")
    tin_match: Optional[StrictBool] = Field(default=None, description="Boolean indicating that TIN Matching should be scheduled for this form", alias="tinMatch")
    no_tin: Optional[StrictBool] = Field(default=None, description="No TIN indicator", alias="noTin")
    address_verification: Optional[StrictBool] = Field(default=None, description="Boolean indicating that address verification should be scheduled for this form", alias="addressVerification")
    state_and_local_withholding: Optional[StateAndLocalWithholding] = Field(default=None, description="State and local withholding information", alias="stateAndLocalWithholding")
    second_tin_notice: Optional[StrictBool] = Field(default=None, description="Second TIN notice", alias="secondTinNotice")
    federal_efile_status: Optional[Form1099StatusDetail] = Field(default=None, description="Federal e-file status", alias="federalEfileStatus")
    state_efile_status: Optional[List[StateEfileStatusDetail]] = Field(default=None, description="State e-file status", alias="stateEfileStatus")
    postal_mail_status: Optional[Form1099StatusDetail] = Field(default=None, description="Postal mail to recipient status", alias="postalMailStatus")
    tin_match_status: Optional[Form1099StatusDetail] = Field(default=None, description="TIN Match status", alias="tinMatchStatus")
    address_verification_status: Optional[Form1099StatusDetail] = Field(default=None, description="Address verification status", alias="addressVerificationStatus")
    e_delivery_status: Optional[Form1099StatusDetail] = Field(default=None, description="EDelivery status", alias="eDeliveryStatus")
    validation_errors: Optional[List[ValidationError]] = Field(default=None, description="Validation errors", alias="validationErrors")
    created_at: Optional[datetime] = Field(default=None, description="Date time when the record was created.", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="Date time when the record was last updated.", alias="updatedAt")
    __properties: ClassVar[List[str]] = ["type", "id", "issuerId", "issuerReferenceId", "issuerTin", "taxYear", "referenceId", "tin", "recipientName", "tinType", "recipientSecondName", "address", "address2", "city", "state", "zip", "email", "accountNumber", "officeCode", "nonUsProvince", "countryCode", "federalEfileDate", "postalMail", "stateEfileDate", "recipientEdeliveryDate", "tinMatch", "noTin", "addressVerification", "stateAndLocalWithholding", "secondTinNotice", "federalEfileStatus", "stateEfileStatus", "postalMailStatus", "tinMatchStatus", "addressVerificationStatus", "eDeliveryStatus", "validationErrors", "createdAt", "updatedAt"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT']):
            raise ValueError("must be one of enum values ('1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT')")
        return value

    @field_validator('tin_type')
    def tin_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Empty', 'EIN', 'SSN', 'ITIN', 'ATIN']):
            raise ValueError("must be one of enum values ('Empty', 'EIN', 'SSN', 'ITIN', 'ATIN')")
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
        """Create an instance of Form1099R from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "id",
            "federal_efile_status",
            "state_efile_status",
            "postal_mail_status",
            "tin_match_status",
            "address_verification_status",
            "e_delivery_status",
            "validation_errors",
            "created_at",
            "updated_at",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of state_and_local_withholding
        if self.state_and_local_withholding:
            _dict['stateAndLocalWithholding'] = self.state_and_local_withholding.to_dict()
        # override the default output from pydantic by calling `to_dict()` of federal_efile_status
        if self.federal_efile_status:
            _dict['federalEfileStatus'] = self.federal_efile_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in state_efile_status (list)
        _items = []
        if self.state_efile_status:
            for _item in self.state_efile_status:
                if _item:
                    _items.append(_item.to_dict())
            _dict['stateEfileStatus'] = _items
        # override the default output from pydantic by calling `to_dict()` of postal_mail_status
        if self.postal_mail_status:
            _dict['postalMailStatus'] = self.postal_mail_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of tin_match_status
        if self.tin_match_status:
            _dict['tinMatchStatus'] = self.tin_match_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of address_verification_status
        if self.address_verification_status:
            _dict['addressVerificationStatus'] = self.address_verification_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of e_delivery_status
        if self.e_delivery_status:
            _dict['eDeliveryStatus'] = self.e_delivery_status.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in validation_errors (list)
        _items = []
        if self.validation_errors:
            for _item in self.validation_errors:
                if _item:
                    _items.append(_item.to_dict())
            _dict['validationErrors'] = _items
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if issuer_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_id is None and "issuer_id" in self.model_fields_set:
            _dict['issuerId'] = None

        # set to None if issuer_reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_reference_id is None and "issuer_reference_id" in self.model_fields_set:
            _dict['issuerReferenceId'] = None

        # set to None if issuer_tin (nullable) is None
        # and model_fields_set contains the field
        if self.issuer_tin is None and "issuer_tin" in self.model_fields_set:
            _dict['issuerTin'] = None

        # set to None if tax_year (nullable) is None
        # and model_fields_set contains the field
        if self.tax_year is None and "tax_year" in self.model_fields_set:
            _dict['taxYear'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if tin (nullable) is None
        # and model_fields_set contains the field
        if self.tin is None and "tin" in self.model_fields_set:
            _dict['tin'] = None

        # set to None if recipient_name (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_name is None and "recipient_name" in self.model_fields_set:
            _dict['recipientName'] = None

        # set to None if tin_type (nullable) is None
        # and model_fields_set contains the field
        if self.tin_type is None and "tin_type" in self.model_fields_set:
            _dict['tinType'] = None

        # set to None if recipient_second_name (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_second_name is None and "recipient_second_name" in self.model_fields_set:
            _dict['recipientSecondName'] = None

        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

        # set to None if address2 (nullable) is None
        # and model_fields_set contains the field
        if self.address2 is None and "address2" in self.model_fields_set:
            _dict['address2'] = None

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

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if account_number (nullable) is None
        # and model_fields_set contains the field
        if self.account_number is None and "account_number" in self.model_fields_set:
            _dict['accountNumber'] = None

        # set to None if office_code (nullable) is None
        # and model_fields_set contains the field
        if self.office_code is None and "office_code" in self.model_fields_set:
            _dict['officeCode'] = None

        # set to None if non_us_province (nullable) is None
        # and model_fields_set contains the field
        if self.non_us_province is None and "non_us_province" in self.model_fields_set:
            _dict['nonUsProvince'] = None

        # set to None if country_code (nullable) is None
        # and model_fields_set contains the field
        if self.country_code is None and "country_code" in self.model_fields_set:
            _dict['countryCode'] = None

        # set to None if federal_efile_date (nullable) is None
        # and model_fields_set contains the field
        if self.federal_efile_date is None and "federal_efile_date" in self.model_fields_set:
            _dict['federalEfileDate'] = None

        # set to None if postal_mail (nullable) is None
        # and model_fields_set contains the field
        if self.postal_mail is None and "postal_mail" in self.model_fields_set:
            _dict['postalMail'] = None

        # set to None if state_efile_date (nullable) is None
        # and model_fields_set contains the field
        if self.state_efile_date is None and "state_efile_date" in self.model_fields_set:
            _dict['stateEfileDate'] = None

        # set to None if recipient_edelivery_date (nullable) is None
        # and model_fields_set contains the field
        if self.recipient_edelivery_date is None and "recipient_edelivery_date" in self.model_fields_set:
            _dict['recipientEdeliveryDate'] = None

        # set to None if tin_match (nullable) is None
        # and model_fields_set contains the field
        if self.tin_match is None and "tin_match" in self.model_fields_set:
            _dict['tinMatch'] = None

        # set to None if no_tin (nullable) is None
        # and model_fields_set contains the field
        if self.no_tin is None and "no_tin" in self.model_fields_set:
            _dict['noTin'] = None

        # set to None if address_verification (nullable) is None
        # and model_fields_set contains the field
        if self.address_verification is None and "address_verification" in self.model_fields_set:
            _dict['addressVerification'] = None

        # set to None if state_and_local_withholding (nullable) is None
        # and model_fields_set contains the field
        if self.state_and_local_withholding is None and "state_and_local_withholding" in self.model_fields_set:
            _dict['stateAndLocalWithholding'] = None

        # set to None if federal_efile_status (nullable) is None
        # and model_fields_set contains the field
        if self.federal_efile_status is None and "federal_efile_status" in self.model_fields_set:
            _dict['federalEfileStatus'] = None

        # set to None if state_efile_status (nullable) is None
        # and model_fields_set contains the field
        if self.state_efile_status is None and "state_efile_status" in self.model_fields_set:
            _dict['stateEfileStatus'] = None

        # set to None if postal_mail_status (nullable) is None
        # and model_fields_set contains the field
        if self.postal_mail_status is None and "postal_mail_status" in self.model_fields_set:
            _dict['postalMailStatus'] = None

        # set to None if tin_match_status (nullable) is None
        # and model_fields_set contains the field
        if self.tin_match_status is None and "tin_match_status" in self.model_fields_set:
            _dict['tinMatchStatus'] = None

        # set to None if address_verification_status (nullable) is None
        # and model_fields_set contains the field
        if self.address_verification_status is None and "address_verification_status" in self.model_fields_set:
            _dict['addressVerificationStatus'] = None

        # set to None if e_delivery_status (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_status is None and "e_delivery_status" in self.model_fields_set:
            _dict['eDeliveryStatus'] = None

        # set to None if validation_errors (nullable) is None
        # and model_fields_set contains the field
        if self.validation_errors is None and "validation_errors" in self.model_fields_set:
            _dict['validationErrors'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Form1099R from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "type": obj.get("type"),
            "id": obj.get("id"),
            "issuerId": obj.get("issuerId"),
            "issuerReferenceId": obj.get("issuerReferenceId"),
            "issuerTin": obj.get("issuerTin"),
            "taxYear": obj.get("taxYear"),
            "referenceId": obj.get("referenceId"),
            "tin": obj.get("tin"),
            "recipientName": obj.get("recipientName"),
            "tinType": obj.get("tinType"),
            "recipientSecondName": obj.get("recipientSecondName"),
            "address": obj.get("address"),
            "address2": obj.get("address2"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "email": obj.get("email"),
            "accountNumber": obj.get("accountNumber"),
            "officeCode": obj.get("officeCode"),
            "nonUsProvince": obj.get("nonUsProvince"),
            "countryCode": obj.get("countryCode"),
            "federalEfileDate": obj.get("federalEfileDate"),
            "postalMail": obj.get("postalMail"),
            "stateEfileDate": obj.get("stateEfileDate"),
            "recipientEdeliveryDate": obj.get("recipientEdeliveryDate"),
            "tinMatch": obj.get("tinMatch"),
            "noTin": obj.get("noTin"),
            "addressVerification": obj.get("addressVerification"),
            "stateAndLocalWithholding": StateAndLocalWithholding.from_dict(obj["stateAndLocalWithholding"]) if obj.get("stateAndLocalWithholding") is not None else None,
            "secondTinNotice": obj.get("secondTinNotice"),
            "federalEfileStatus": Form1099StatusDetail.from_dict(obj["federalEfileStatus"]) if obj.get("federalEfileStatus") is not None else None,
            "stateEfileStatus": [StateEfileStatusDetail.from_dict(_item) for _item in obj["stateEfileStatus"]] if obj.get("stateEfileStatus") is not None else None,
            "postalMailStatus": Form1099StatusDetail.from_dict(obj["postalMailStatus"]) if obj.get("postalMailStatus") is not None else None,
            "tinMatchStatus": Form1099StatusDetail.from_dict(obj["tinMatchStatus"]) if obj.get("tinMatchStatus") is not None else None,
            "addressVerificationStatus": Form1099StatusDetail.from_dict(obj["addressVerificationStatus"]) if obj.get("addressVerificationStatus") is not None else None,
            "eDeliveryStatus": Form1099StatusDetail.from_dict(obj["eDeliveryStatus"]) if obj.get("eDeliveryStatus") is not None else None,
            "validationErrors": [ValidationError.from_dict(_item) for _item in obj["validationErrors"]] if obj.get("validationErrors") is not None else None,
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt")
        })
        return _obj


