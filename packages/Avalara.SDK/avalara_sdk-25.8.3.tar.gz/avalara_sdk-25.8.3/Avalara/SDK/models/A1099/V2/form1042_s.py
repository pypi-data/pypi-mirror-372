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
from Avalara.SDK.models.A1099.V2.intermediary_or_flow_through import IntermediaryOrFlowThrough
from Avalara.SDK.models.A1099.V2.primary_withholding_agent import PrimaryWithholdingAgent
from Avalara.SDK.models.A1099.V2.state_and_local_withholding import StateAndLocalWithholding
from Avalara.SDK.models.A1099.V2.state_efile_status_detail import StateEfileStatusDetail
from Avalara.SDK.models.A1099.V2.validation_error import ValidationError
from typing import Optional, Set
from typing_extensions import Self

class Form1042S(BaseModel):
    """
    Form 1042-S: Foreign Person's U.S. Source Income Subject to Withholding
    """ # noqa: E501
    tin_type: Optional[StrictStr] = Field(default=None, alias="tinType")
    unique_form_id: Optional[StrictStr] = Field(description="Unique form identifier", alias="uniqueFormId")
    recipient_date_of_birth: Optional[date] = Field(default=None, description="Recipient's date of birth", alias="recipientDateOfBirth")
    recipient_giin: Optional[StrictStr] = Field(default=None, description="Recipient's Global Intermediary Identification Number (GIIN). A valid GIIN looks like 'XXXXXX.XXXXX.XX.XXX'.", alias="recipientGiin")
    recipient_foreign_tin: Optional[StrictStr] = Field(default=None, description="Recipient's foreign TIN. Required if email is specified, must fill either this or Chap3StatusCode.", alias="recipientForeignTin")
    lob_code: Optional[StrictStr] = Field(default=None, description="Limitation on Benefits (LOB) code for tax treaty purposes.  Available values:  - 01: Individual (Deprecated - valid only for tax years prior to 2019)  - 02: Government - contracting state/political subdivision/local authority  - 03: Tax exempt pension trust/Pension fund  - 04: Tax exempt/Charitable organization  - 05: Publicly-traded corporation  - 06: Subsidiary of publicly-traded corporation  - 07: Company that meets the ownership and base erosion test  - 08: Company that meets the derivative benefits test  - 09: Company with an item of income that meets the active trade or business test  - 10: Discretionary determination  - 11: Other  - 12: No LOB article in treaty", alias="lobCode")
    income_code: Optional[StrictStr] = Field(description="Income code.  Available values:    Interest:  - 01: Interest paid by US obligors - general  - 02: Interest paid on real property mortgages  - 03: Interest paid to controlling foreign corporations  - 04: Interest paid by foreign corporations  - 05: Interest on tax-free covenant bonds  - 22: Interest paid on deposit with a foreign branch of a domestic corporation or partnership  - 29: Deposit interest  - 30: Original issue discount (OID)  - 31: Short-term OID  - 33: Substitute payment - interest  - 51: Interest paid on certain actively traded or publicly offered securities(1)  - 54: Substitute payments - interest from certain actively traded or publicly offered securities(1)    Dividend:  - 06: Dividends paid by U.S. corporations - general  - 07: Dividends qualifying for direct dividend rate  - 08: Dividends paid by foreign corporations  - 34: Substitute payment - dividends  - 40: Other dividend equivalents under IRC section 871(m) (formerly 871(l))  - 52: Dividends paid on certain actively traded or publicly offered securities(1)  - 53: Substitute payments - dividends from certain actively traded or publicly offered securities(1)  - 56: Dividend equivalents under IRC section 871(m) as a result of applying the combined transaction rules    Other:  - 09: Capital gains  - 10: Industrial royalties  - 11: Motion picture or television copyright royalties  - 12: Other royalties (for example, copyright, software, broadcasting, endorsement payments)  - 13: Royalties paid on certain publicly offered securities(1)  - 14: Real property income and natural resources royalties  - 15: Pensions, annuities, alimony, and/or insurance premiums  - 16: Scholarship or fellowship grants  - 17: Compensation for independent personal services(2)  - 18: Compensation for dependent personal services(2)  - 19: Compensation for teaching(2)  - 20: Compensation during studying and training(2)  - 23: Other income  - 24: Qualified investment entity (QIE) distributions of capital gains  - 25: Trust distributions subject to IRC section 1445  - 26: Unsevered growing crops and timber distributions by a trust subject to IRC section 1445  - 27: Publicly traded partnership distributions subject to IRC section 1446  - 28: Gambling winnings(3)  - 32: Notional principal contract income(4)  - 35: Substitute payment - other  - 36: Capital gains distributions  - 37: Return of capital  - 38: Eligible deferred compensation items subject to IRC section 877A(d)(1)  - 39: Distributions from a nongrantor trust subject to IRC section 877A(f)(1)  - 41: Guarantee of indebtedness  - 42: Earnings as an artist or athlete - no central withholding agreement(5)  - 43: Earnings as an artist or athlete - central withholding agreement(5)  - 44: Specified Federal procurement payments  - 50: Income previously reported under escrow procedure(6)  - 55: Taxable death benefits on life insurance contracts  - 57: Amount realized under IRC section 1446(f)  - 58: Publicly traded partnership distributions-undetermined", alias="incomeCode")
    gross_income: Optional[Union[StrictFloat, StrictInt]] = Field(description="Gross income", alias="grossIncome")
    withholding_indicator: Optional[StrictStr] = Field(description="Withholding indicator  Available values:  - 3: Chapter 3  - 4: Chapter 4", alias="withholdingIndicator")
    tax_country_code: Optional[StrictStr] = Field(description="Country code", alias="taxCountryCode")
    exemption_code_chap3: Optional[StrictStr] = Field(default=None, description="Exemption code (Chapter 3). Required if WithholdingIndicator is 3 (Chapter 3). Required when using TaxRateChap3.  Available values:  - Empty: Tax rate is due to backup withholding  - 00: Not exempt  - 01: Effectively connected income  - 02: Exempt under IRC (other than portfolio interest)  - 03: Income is not from US sources  - 04: Exempt under tax treaty  - 05: Portfolio interest exempt under IRC  - 06: QI that assumes primary withholding responsibility  - 07: WFP or WFT  - 08: U.S. branch treated as U.S. Person  - 09: Territory FI treated as U.S. Person  - 10: QI represents that income is exempt  - 11: QSL that assumes primary withholding responsibility  - 12: Payee subjected to chapter 4 withholding  - 22: QDD that assumes primary withholding responsibility  - 23: Exempt under section 897(l)  - 24: Exempt under section 892", alias="exemptionCodeChap3")
    exemption_code_chap4: Optional[StrictStr] = Field(default=None, description="Exemption code (Chapter 4). Required if WithholdingIndicator is 4 (Chapter 4).  Available values:  - 00: Not exempt  - 13: Grandfathered payment  - 14: Effectively connected income  - 15: Payee not subject to chapter 4 withholding  - 16: Excluded nonfinancial payment  - 17: Foreign Entity that assumes primary withholding responsibility  - 18: U.S. Payees - of participating FFI or registered deemed - compliant FFI  - 19: Exempt from withholding under IGA(6)  - 20: Dormant account(7)  - 21: Other - payment not subject to chapter 4 withholding", alias="exemptionCodeChap4")
    tax_rate_chap3: Optional[StrictStr] = Field(default=None, description="Tax rate (Chapter 3) - Required if WithholdingIndicator is 3 (Chapter 3).  Available values:  - 00.00: 0.00%  - 02.00: 2.00%  - 04.00: 4.00%  - 04.90: 4.90%  - 04.95: 4.95%  - 05.00: 5.00%  - 07.00: 7.00%  - 08.00: 8.00%  - 10.00: 10.00%  - 12.00: 12.00%  - 12.50: 12.50%  - 14.00: 14.00%  - 15.00: 15.00%  - 17.50: 17.50%  - 20.00: 20.00%  - 21.00: 21.00%  - 24.00: 24.00%  - 25.00: 25.00%  - 27.50: 27.50%  - 28.00: 28.00%  - 30.00: 30.00%  - 37.00: 37.00%", alias="taxRateChap3")
    withholding_allowance: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Withholding allowance", alias="withholdingAllowance")
    federal_tax_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Federal tax withheld", alias="federalTaxWithheld")
    tax_not_deposited_indicator: Optional[StrictBool] = Field(default=None, description="Tax not deposited indicator", alias="taxNotDepositedIndicator")
    academic_indicator: Optional[StrictBool] = Field(default=None, description="Academic indicator", alias="academicIndicator")
    tax_withheld_other_agents: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Tax withheld by other agents", alias="taxWithheldOtherAgents")
    amount_repaid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Amount repaid to recipient", alias="amountRepaid")
    tax_paid_agent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Tax paid by withholding agent", alias="taxPaidAgent")
    chap3_status_code: Optional[StrictStr] = Field(default=None, description="Chapter 3 status code - Required if WithholdingIndicator is 3 (Chapter 3)  Available values:  - 01: U.S. Withholding Agent - FI (Deprecated - valid only for tax years prior to 2020)  - 02: U.S. Withholding Agent - Other (Deprecated - valid only for tax years prior to 2020)  - 03: Territory FI - treated as U.S. Person  - 04: Territory FI - not treated as U.S. Person  - 05: U.S. branch - treated as U.S. Person  - 06: U.S. branch - not treated as U.S. Person  - 07: U.S. branch - ECI presumption applied  - 08: Partnership other than Withholding Foreign Partnership  - 09: Withholding Foreign Partnership  - 10: Trust other than Withholding Foreign Trust  - 11: Withholding Foreign Trust  - 12: Qualified Intermediary  - 13: Qualified Securities Lender - Qualified Intermediary  - 14: Qualified Securities Lender - Other  - 15: Corporation  - 16: Individual  - 17: Estate  - 18: Private Foundation  - 19: Government or International Organization  - 20: Tax Exempt Organization (Section 501(c) entities)  - 21: Unknown Recipient  - 22: Artist or Athlete  - 23: Pension  - 24: Foreign Central Bank of Issue  - 25: Nonqualified Intermediary  - 26: Hybrid entity making Treaty Claim  - 27: Withholding Rate Pool - General  - 28: Withholding Rate Pool - Exempt Organization  - 29: PAI Withholding Rate Pool - General  - 30: PAI Withholding Rate Pool - Exempt Organization  - 31: Agency Withholding Rate Pool - General  - 32: Agency Withholding Rate Pool - Exempt Organization  - 34: U.S. Withholding Agent-Foreign branch of FI (Deprecated - valid only for tax years prior to 2020)  - 35: Qualified Derivatives Dealer  - 36: Foreign Government - Integral Part  - 37: Foreign Government - Controlled Entity  - 38: Publicly Traded Partnership  - 39: Disclosing Qualified Intermediary", alias="chap3StatusCode")
    chap4_status_code: Optional[StrictStr] = Field(default=None, description="Chapter 4 status code. Required if WithholdingIndicator is 4 (Chapter 4). Required if email is specified, must fill either this or RecipientForeignTin.  Available values:  - 01: U.S. Withholding Agent - FI  - 02: U.S. Withholding Agent - Other  - 03: Territory FI - not treated as U.S. Person  - 04: Territory FI - treated as U.S. Person  - 05: Participating FFI - Other  - 06: Participating FFI - Reporting Model 2 FFI  - 07: Registered Deemed - Compliant FFI-Reporting Model 1 FFI  - 08: Registered Deemed - Compliant FFI-Sponsored Entity  - 09: Registered Deemed - Compliant FFI-Other  - 10: Certified Deemed - Compliant FFI-Other  - 11: Certified Deemed - Compliant FFI-FFI with Low Value Accounts  - 12: Certified Deemed - Compliant FFI-Non-Registering Local Bank  - 13: Certified Deemed - Compliant FFI-Sponsored Entity  - 14: Certified Deemed - Compliant FFI-Investment Advisor or Investment Manager  - 15: Nonparticipating FFI  - 16: Owner-Documented FFI  - 17: U.S. Branch - treated as U.S. person  - 18: U.S. Branch - not treated as U.S. person (reporting under section 1471)  - 19: Passive NFFE identifying Substantial U.S. Owners  - 20: Passive NFFE with no Substantial U.S. Owners  - 21: Publicly Traded NFFE or Affiliate of Publicly Traded NFFE  - 22: Active NFFE  - 23: Individual  - 24: Section 501(c) Entities  - 25: Excepted Territory NFFE  - 26: Excepted NFFE - Other  - 27: Exempt Beneficial Owner  - 28: Entity Wholly Owned by Exempt Beneficial Owners  - 29: Unknown Recipient  - 30: Recalcitrant Account Holder  - 31: Nonreporting IGA FFI  - 32: Direct reporting NFFE  - 33: U.S. reportable account  - 34: Non-consenting U.S. account  - 35: Sponsored direct reporting NFFE  - 36: Excepted Inter-affiliate FFI  - 37: Undocumented Preexisting Obligation  - 38: U.S. Branch - ECI presumption applied  - 39: Account Holder of Excluded Financial Account  - 40: Passive NFFE reported by FFI  - 41: NFFE subject to 1472 withholding  - 42: Recalcitrant Pool - No U.S. Indicia  - 43: Recalcitrant Pool - U.S. Indicia  - 44: Recalcitrant Pool - Dormant Account  - 45: Recalcitrant Pool - U.S. Persons  - 46: Recalcitrant Pool - Passive NFFEs  - 47: Nonparticipating FFI Pool  - 48: U.S. Payees Pool  - 49: QI - Recalcitrant Pool-General  - 50: U.S. Withholding Agent-Foreign branch of FI", alias="chap4StatusCode")
    primary_withholding_agent: Optional[PrimaryWithholdingAgent] = Field(default=None, description="Primary withholding agent information", alias="primaryWithholdingAgent")
    intermediary_or_flow_through: Optional[IntermediaryOrFlowThrough] = Field(default=None, description="Intermediary or flow-through entity information", alias="intermediaryOrFlowThrough")
    type: StrictStr = Field(description="Form type")
    id: Optional[StrictStr] = Field(default=None, description="Form ID. Unique identifier set when the record is created.")
    issuer_id: Optional[StrictStr] = Field(default=None, description="Issuer ID - only required when creating forms", alias="issuerId")
    issuer_reference_id: Optional[StrictStr] = Field(default=None, description="Issuer Reference ID - only required when creating forms", alias="issuerReferenceId")
    issuer_tin: Optional[StrictStr] = Field(default=None, description="Issuer TIN - readonly", alias="issuerTin")
    tax_year: Optional[StrictInt] = Field(default=None, description="Tax Year - only required when creating forms", alias="taxYear")
    reference_id: Optional[StrictStr] = Field(default=None, description="Internal reference ID. Never shown to any agency or recipient.", alias="referenceId")
    tin: Optional[StrictStr] = Field(default=None, description="Recipient's Federal Tax Identification Number (TIN).")
    recipient_name: Optional[StrictStr] = Field(description="Recipient name", alias="recipientName")
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

    @field_validator('tin_type')
    def tin_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Empty', 'EIN', 'SSN', 'ITIN', 'ATIN']):
            raise ValueError("must be one of enum values ('Empty', 'EIN', 'SSN', 'ITIN', 'ATIN')")
        return value

    @field_validator('lob_code')
    def lob_code_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']):
            raise ValueError("must be one of enum values ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')")
        return value

    @field_validator('income_code')
    def income_code_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['01', '02', '03', '04', '05', '22', '29', '30', '31', '33', '51', '54', '06', '07', '08', '34', '40', '52', '53', '56', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '23', '24', '25', '26', '27', '28', '32', '35', '36', '37', '38', '39', '41', '42', '43', '44', '50', '55', '57', '58']):
            raise ValueError("must be one of enum values ('01', '02', '03', '04', '05', '22', '29', '30', '31', '33', '51', '54', '06', '07', '08', '34', '40', '52', '53', '56', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '23', '24', '25', '26', '27', '28', '32', '35', '36', '37', '38', '39', '41', '42', '43', '44', '50', '55', '57', '58')")
        return value

    @field_validator('withholding_indicator')
    def withholding_indicator_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['3', '4']):
            raise ValueError("must be one of enum values ('3', '4')")
        return value

    @field_validator('exemption_code_chap3')
    def exemption_code_chap3_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '22', '23', '24']):
            raise ValueError("must be one of enum values ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '22', '23', '24')")
        return value

    @field_validator('exemption_code_chap4')
    def exemption_code_chap4_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['00', '13', '14', '15', '16', '17', '18', '19', '20', '21']):
            raise ValueError("must be one of enum values ('00', '13', '14', '15', '16', '17', '18', '19', '20', '21')")
        return value

    @field_validator('tax_rate_chap3')
    def tax_rate_chap3_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['00.00', '02.00', '04.00', '04.90', '04.95', '05.00', '07.00', '08.00', '10.00', '12.00', '12.50', '14.00', '15.00', '17.50', '20.00', '21.00', '24.00', '25.00', '27.50', '28.00', '30.00', '37.00']):
            raise ValueError("must be one of enum values ('00.00', '02.00', '04.00', '04.90', '04.95', '05.00', '07.00', '08.00', '10.00', '12.00', '12.50', '14.00', '15.00', '17.50', '20.00', '21.00', '24.00', '25.00', '27.50', '28.00', '30.00', '37.00')")
        return value

    @field_validator('chap3_status_code')
    def chap3_status_code_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['01', '02', '34', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '35', '36', '37', '38', '39']):
            raise ValueError("must be one of enum values ('01', '02', '34', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '35', '36', '37', '38', '39')")
        return value

    @field_validator('chap4_status_code')
    def chap4_status_code_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50']):
            raise ValueError("must be one of enum values ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50')")
        return value

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT']):
            raise ValueError("must be one of enum values ('1099-NEC', '1099-MISC', '1099-DIV', '1099-R', '1099-K', '1095-B', '1042-S', '1095-C', '1099-INT')")
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
        """Create an instance of Form1042S from a JSON string"""
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
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "tin_type",
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
        """Create an instance of Form1042S from a dict"""
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


