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
from Avalara.SDK.models.A1099.V2.w8_ben_e_substantial_us_owner_data_model import W8BenESubstantialUsOwnerDataModel
from typing import Optional, Set
from typing_extensions import Self

class W8BenFormDataModel(BaseModel):
    """
    W-8 BEN form
    """ # noqa: E501
    type: Optional[StrictStr] = Field(default=None, description="Type of the form, always W8ben for this model.")
    signed_date: Optional[datetime] = Field(default=None, description="The date the form was signed.", alias="signedDate")
    birthday: Optional[StrictStr] = Field(default=None, description="The birthday of the individual associated with the form.")
    foreign_tin_not_required: Optional[StrictBool] = Field(default=None, description="Indicates whether a foreign TIN is not required.", alias="foreignTinNotRequired")
    archived: Optional[StrictBool] = Field(default=None, description="Indicates whether the form is archived.")
    reference_id: Optional[StrictStr] = Field(default=None, description="A reference identifier for the form.", alias="referenceId")
    company_id: Optional[StrictInt] = Field(default=None, description="The ID of the associated company.", alias="companyId")
    display_name: Optional[StrictStr] = Field(default=None, description="The display name associated with the form.", alias="displayName")
    email: Optional[StrictStr] = Field(default=None, description="The email address of the individual associated with the form.")
    type_of_tin: Optional[StrictStr] = Field(default=None, description="The type of TIN provided.", alias="typeOfTin")
    name: Optional[StrictStr] = Field(default=None, description="The name of the individual or entity associated with the form.")
    residence_address: Optional[StrictStr] = Field(default=None, description="The residential address of the individual or entity.", alias="residenceAddress")
    residence_city: Optional[StrictStr] = Field(default=None, description="The city of residence.", alias="residenceCity")
    residence_state: Optional[StrictStr] = Field(default=None, description="The state of residence.", alias="residenceState")
    residence_postal_code: Optional[StrictStr] = Field(default=None, description="The postal code of the residence.", alias="residencePostalCode")
    residence_country: Optional[StrictStr] = Field(default=None, description="The country of residence.", alias="residenceCountry")
    residence_is_mailing: Optional[StrictBool] = Field(default=None, alias="residenceIsMailing")
    mailing_address: Optional[StrictStr] = Field(default=None, description="The mailing address.", alias="mailingAddress")
    mailing_city: Optional[StrictStr] = Field(default=None, description="The city of the mailing address.", alias="mailingCity")
    mailing_state: Optional[StrictStr] = Field(default=None, description="The state of the mailing address.", alias="mailingState")
    mailing_postal_code: Optional[StrictStr] = Field(default=None, description="The postal code of the mailing address.", alias="mailingPostalCode")
    mailing_country: Optional[StrictStr] = Field(default=None, description="The country of the mailing address.", alias="mailingCountry")
    tin: Optional[StrictStr] = Field(default=None, description="The taxpayer identification number (TIN).")
    foreign_tin: Optional[StrictStr] = Field(default=None, description="The foreign taxpayer identification number (TIN).", alias="foreignTin")
    reference_number: Optional[StrictStr] = Field(default=None, description="A reference number for the form.", alias="referenceNumber")
    citizenship_country: Optional[StrictStr] = Field(default=None, description="The country of citizenship.", alias="citizenshipCountry")
    treaty_country: Optional[StrictStr] = Field(default=None, description="The country for which the treaty applies.", alias="treatyCountry")
    treaty_article: Optional[StrictStr] = Field(default=None, description="The specific article of the treaty being claimed.", alias="treatyArticle")
    withholding_rate: Optional[StrictStr] = Field(default=None, description="The withholding rate applied as per the treaty.", alias="withholdingRate")
    income_type: Optional[StrictStr] = Field(default=None, description="The type of income covered by the treaty.", alias="incomeType")
    treaty_reasons: Optional[StrictStr] = Field(default=None, description="The reasons for claiming treaty benefits.", alias="treatyReasons")
    signer_name: Optional[StrictStr] = Field(default=None, description="The name of the signer of the form.", alias="signerName")
    signer_capacity: Optional[StrictStr] = Field(default=None, description="The capacity in which the signer is signing the form.", alias="signerCapacity")
    e_delivery_consented_at: Optional[datetime] = Field(default=None, description="The date when e-delivery was consented.", alias="eDeliveryConsentedAt")
    created_at: Optional[datetime] = Field(default=None, description="The creation date of the form.", alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, description="The last updated date of the form.", alias="updatedAt")
    employee_first_name: Optional[StrictStr] = Field(default=None, description="The first name of the employee.", alias="employeeFirstName")
    employee_middle_name: Optional[StrictStr] = Field(default=None, description="The middle name of the employee.", alias="employeeMiddleName")
    employee_last_name: Optional[StrictStr] = Field(default=None, description="The last name of the employee.", alias="employeeLastName")
    employee_name_suffix: Optional[StrictStr] = Field(default=None, description="The name suffix of the employee.", alias="employeeNameSuffix")
    address: Optional[StrictStr] = Field(default=None, description="The address of the individual or entity.")
    city: Optional[StrictStr] = Field(default=None, description="The city of the address.")
    state: Optional[StrictStr] = Field(default=None, description="The state of the address.")
    zip: Optional[StrictStr] = Field(default=None, description="The ZIP code of the address.")
    box3_marital_status: Optional[StrictStr] = Field(default=None, description="The marital status of the employee.", alias="box3MaritalStatus")
    box4_last_name_differs: Optional[StrictBool] = Field(default=None, description="Indicates whether the last name differs from prior records.", alias="box4LastNameDiffers")
    box5_num_allowances: Optional[StrictInt] = Field(default=None, description="The number of allowances claimed by the employee.", alias="box5NumAllowances")
    other_dependents: Optional[StrictInt] = Field(default=None, description="The number of dependents other than allowances.", alias="otherDependents")
    non_job_income: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of non-job income.", alias="nonJobIncome")
    deductions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of deductions claimed.")
    box6_additional_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The additional amount withheld.", alias="box6AdditionalWithheld")
    box7_exempt_from_withholding: Optional[StrictBool] = Field(default=None, description="Indicates whether the employee is exempt from withholding.", alias="box7ExemptFromWithholding")
    office_code: Optional[StrictStr] = Field(default=None, description="The office code associated with the form.", alias="officeCode")
    disregarded_entity_chapter4_fatca_status: Optional[StrictStr] = Field(default=None, description="The FATCA status for disregarded entities under Chapter 4.", alias="disregardedEntityChapter4FatcaStatus")
    disregarded_address: Optional[StrictStr] = Field(default=None, description="The address for disregarded entities.", alias="disregardedAddress")
    disregarded_city: Optional[StrictStr] = Field(default=None, description="The city for disregarded entities.", alias="disregardedCity")
    disregarded_state: Optional[StrictStr] = Field(default=None, description="The state for disregarded entities.", alias="disregardedState")
    disregarded_postal_code: Optional[StrictStr] = Field(default=None, description="The postal code for disregarded entities.", alias="disregardedPostalCode")
    disregarded_country: Optional[StrictStr] = Field(default=None, description="The country for disregarded entities.", alias="disregardedCountry")
    ftin_not_required: Optional[StrictBool] = Field(default=None, description="Indicates whether a foreign TIN is not required.", alias="ftinNotRequired")
    giin: Optional[StrictStr] = Field(default=None, description="The global intermediary identification number (GIIN).")
    chapter3_entity_type: Optional[StrictStr] = Field(default=None, description="The Chapter 3 entity type.", alias="chapter3EntityType")
    chapter4_fatca_status: Optional[StrictStr] = Field(default=None, description="The Chapter 4 FATCA status.", alias="chapter4FatcaStatus")
    disregarded_entity: Optional[StrictStr] = Field(default=None, description="The disregarded entity information.", alias="disregardedEntity")
    disregarded_entity_giin: Optional[StrictStr] = Field(default=None, description="The GIIN for disregarded entities.", alias="disregardedEntityGiin")
    benefit_limitation: Optional[StrictStr] = Field(default=None, description="The benefit limitation for tax treaty claims.", alias="benefitLimitation")
    part4_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The sponsoring entity information for Part 4.", alias="part4SponsoringEntity")
    part4_sponsoring_entity_giin: Optional[StrictStr] = Field(default=None, description="The GIIN for the sponsoring entity in Part 4.", alias="part4SponsoringEntityGiin")
    part7_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The sponsoring entity information for Part 7.", alias="part7SponsoringEntity")
    part12_iga_country: Optional[StrictStr] = Field(default=None, description="The IGA country information for Part 12.", alias="part12IgaCountry")
    part12_iga_type: Optional[StrictStr] = Field(default=None, description="The IGA type information for Part 12.", alias="part12IgaType")
    part12_fatca_status_under_iga_annex_ii: Optional[StrictStr] = Field(default=None, description="The FATCA status under IGA Annex II for Part 12.", alias="part12FatcaStatusUnderIgaAnnexIi")
    part12_trustee_name: Optional[StrictStr] = Field(default=None, description="The trustee name for Part 12.", alias="part12TrusteeName")
    part12_trustee_is_foreign: Optional[StrictBool] = Field(default=None, description="Indicates whether the trustee is foreign for Part 12.", alias="part12TrusteeIsForeign")
    part12_model2_iga_giin: Optional[StrictStr] = Field(default=None, description="The GIIN for Model 2 IGA in Part 12.", alias="part12Model2IgaGiin")
    box37_a_exchange: Optional[StrictStr] = Field(default=None, description="The exchange information for Box 37A.", alias="box37AExchange")
    box37_b_exchange: Optional[StrictStr] = Field(default=None, description="The exchange information for Box 37B.", alias="box37BExchange")
    box37_b_entity: Optional[StrictStr] = Field(default=None, description="The entity information for Box 37B.", alias="box37BEntity")
    part28_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The sponsoring entity information for Part 28.", alias="part28SponsoringEntity")
    part28_sponsoring_entity_giin: Optional[StrictStr] = Field(default=None, description="The GIIN for the sponsoring entity in Part 28.", alias="part28SponsoringEntityGiin")
    making_treaty_claim: Optional[StrictBool] = Field(default=None, alias="makingTreatyClaim")
    certify_box14_a: Optional[StrictBool] = Field(default=None, alias="certifyBox14A")
    certify_box14_b: Optional[StrictBool] = Field(default=None, alias="certifyBox14B")
    certify_box14_c: Optional[StrictBool] = Field(default=None, alias="certifyBox14C")
    certify_box17_1: Optional[StrictBool] = Field(default=None, alias="certifyBox17_1")
    certify_box17_2: Optional[StrictBool] = Field(default=None, alias="certifyBox17_2")
    certify_box18: Optional[StrictBool] = Field(default=None, alias="certifyBox18")
    certify_box19: Optional[StrictBool] = Field(default=None, alias="certifyBox19")
    certify_box21: Optional[StrictBool] = Field(default=None, alias="certifyBox21")
    certify_box22: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 22.", alias="certifyBox22")
    certify_box23: Optional[StrictBool] = Field(default=None, alias="certifyBox23")
    certify_box24_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 24A.", alias="certifyBox24A")
    certify_box24_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 24B.", alias="certifyBox24B")
    certify_box24_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 24C.", alias="certifyBox24C")
    certify_box24_d: Optional[StrictBool] = Field(default=None, alias="certifyBox24D")
    certify_box25_a: Optional[StrictBool] = Field(default=None, alias="certifyBox25A")
    certify_box25_b: Optional[StrictBool] = Field(default=None, alias="certifyBox25B")
    certify_box25_c: Optional[StrictBool] = Field(default=None, alias="certifyBox25C")
    certify_box26: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 26.", alias="certifyBox26")
    certify_box27: Optional[StrictBool] = Field(default=None, alias="certifyBox27")
    certify_box28_a: Optional[StrictBool] = Field(default=None, alias="certifyBox28A")
    certify_box28_b: Optional[StrictBool] = Field(default=None, alias="certifyBox28B")
    certify_box29_a: Optional[StrictBool] = Field(default=None, alias="certifyBox29A")
    certify_box29_b: Optional[StrictBool] = Field(default=None, alias="certifyBox29B")
    certify_box29_c: Optional[StrictBool] = Field(default=None, alias="certifyBox29C")
    certify_box29_d: Optional[StrictBool] = Field(default=None, alias="certifyBox29D")
    certify_box29_e: Optional[StrictBool] = Field(default=None, alias="certifyBox29E")
    certify_box29_f: Optional[StrictBool] = Field(default=None, alias="certifyBox29F")
    certify_box30: Optional[StrictBool] = Field(default=None, alias="certifyBox30")
    certify_box31: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 31.", alias="certifyBox31")
    certify_box32: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 32.", alias="certifyBox32")
    certify_box33: Optional[StrictBool] = Field(default=None, alias="certifyBox33")
    certify_box34: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 34.", alias="certifyBox34")
    certify_box35: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 35.", alias="certifyBox35")
    certify_box36: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 36.", alias="certifyBox36")
    certify_box37_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 37A.", alias="certifyBox37A")
    certify_box37_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 37B.", alias="certifyBox37B")
    certify_box38: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 38.", alias="certifyBox38")
    certify_box39: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 39.", alias="certifyBox39")
    certify_box40_a: Optional[StrictBool] = Field(default=None, alias="certifyBox40A")
    certify_box40_b: Optional[StrictBool] = Field(default=None, alias="certifyBox40B")
    certify_box40_c: Optional[StrictBool] = Field(default=None, alias="certifyBox40C")
    certify_box41: Optional[StrictBool] = Field(default=None, alias="certifyBox41")
    certify_box43: Optional[StrictBool] = Field(default=None, alias="certifyBox43")
    certify_part29_signature: Optional[StrictBool] = Field(default=None, alias="certifyPart29Signature")
    part19_formation_or_resolution_date: Optional[date] = Field(default=None, alias="part19FormationOrResolutionDate")
    part20_filing_date: Optional[date] = Field(default=None, alias="part20FilingDate")
    part21_determination_date: Optional[date] = Field(default=None, alias="part21DeterminationDate")
    substantial_us_owners: Optional[List[W8BenESubstantialUsOwnerDataModel]] = Field(default=None, alias="substantialUsOwners")
    ein: Optional[StrictStr] = Field(default=None, description="The employer identification number (EIN).")
    ein_type: Optional[StrictStr] = Field(default=None, description="The type of employer identification number (EIN).", alias="einType")
    certify_box14: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 14.", alias="certifyBox14")
    certify_box15_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15A.", alias="certifyBox15A")
    certify_box15_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15B.", alias="certifyBox15B")
    certify_box15_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15C.", alias="certifyBox15C")
    certify_box15_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15D.", alias="certifyBox15D")
    certify_box15_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15E.", alias="certifyBox15E")
    certify_box15_f: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15F.", alias="certifyBox15F")
    certify_box15_g: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15G.", alias="certifyBox15G")
    certify_box15_h: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15H.", alias="certifyBox15H")
    certify_box15_i: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 15I.", alias="certifyBox15I")
    certify_box16_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 16A.", alias="certifyBox16A")
    box16_b_qdd_corporate: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 16B as a QDD corporate entity.", alias="box16BQddCorporate")
    box16_b_qdd_partnership: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 16B as a QDD partnership.", alias="box16BQddPartnership")
    box16_b_qdd_disregarded_entity: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 16B as a QDD disregarded entity.", alias="box16BQddDisregardedEntity")
    certify_box17_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 17A.", alias="certifyBox17A")
    certify_box17_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 17B.", alias="certifyBox17B")
    certify_box17_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 17C.", alias="certifyBox17C")
    certify_box17_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 17D.", alias="certifyBox17D")
    certify_box17_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 17E.", alias="certifyBox17E")
    certify_box18_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18A.", alias="certifyBox18A")
    certify_box18_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18B.", alias="certifyBox18B")
    certify_box18_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18C.", alias="certifyBox18C")
    certify_box18_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18D.", alias="certifyBox18D")
    certify_box18_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18E.", alias="certifyBox18E")
    certify_box18_f: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 18F.", alias="certifyBox18F")
    certify_box19_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19A.", alias="certifyBox19A")
    certify_box19_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19B.", alias="certifyBox19B")
    certify_box19_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19C.", alias="certifyBox19C")
    certify_box19_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19D.", alias="certifyBox19D")
    certify_box19_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19E.", alias="certifyBox19E")
    certify_box19_f: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 19F.", alias="certifyBox19F")
    certify_box20: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 20.", alias="certifyBox20")
    certify_box21_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21A.", alias="certifyBox21A")
    certify_box21_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21B.", alias="certifyBox21B")
    certify_box21_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21C.", alias="certifyBox21C")
    certify_box21_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21D.", alias="certifyBox21D")
    certify_box21_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21E.", alias="certifyBox21E")
    certify_box21_f: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 21F.", alias="certifyBox21F")
    box23_a_name_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The name of the sponsoring entity for box 23A.", alias="box23ANameSponsoringEntity")
    certify_box23_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 23B.", alias="certifyBox23B")
    certify_box23_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 23C.", alias="certifyBox23C")
    certify_box25: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 25.", alias="certifyBox25")
    box27_a_name_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The name of the sponsoring entity for box 27A.", alias="box27ANameSponsoringEntity")
    certify_box27_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 27B.", alias="certifyBox27B")
    certify_box28: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 28.", alias="certifyBox28")
    certify_box29: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 29.", alias="certifyBox29")
    certify_box30_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 30A.", alias="certifyBox30A")
    certify_box30_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 30B.", alias="certifyBox30B")
    certify_box30_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 30C.", alias="certifyBox30C")
    box32_iga_country: Optional[StrictStr] = Field(default=None, description="The IGA country information for box 32.", alias="box32IgaCountry")
    box32_iga_type: Optional[StrictStr] = Field(default=None, description="The IGA type information for box 32.", alias="box32IgaType")
    box32_iga_treated_as: Optional[StrictStr] = Field(default=None, description="The IGA treatment information for box 32.", alias="box32IgaTreatedAs")
    box32_trustee_or_sponsor: Optional[StrictStr] = Field(default=None, description="The trustee or sponsor information for box 32.", alias="box32TrusteeOrSponsor")
    box32_trustee_is_foreign: Optional[StrictBool] = Field(default=None, description="Indicates whether the trustee is foreign for box 32.", alias="box32TrusteeIsForeign")
    certify_box33_a: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33A.", alias="certifyBox33A")
    certify_box33_b: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33B.", alias="certifyBox33B")
    certify_box33_c: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33C.", alias="certifyBox33C")
    certify_box33_d: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33D.", alias="certifyBox33D")
    certify_box33_e: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33E.", alias="certifyBox33E")
    certify_box33_f: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 33F.", alias="certifyBox33F")
    box37_a_securities_market: Optional[StrictStr] = Field(default=None, description="The securities market information for box 37A.", alias="box37ASecuritiesMarket")
    box37_b_name_of_entity: Optional[StrictStr] = Field(default=None, description="The name of the entity for box 37B.", alias="box37BNameOfEntity")
    box37_b_securities_market: Optional[StrictStr] = Field(default=None, description="The securities market information for box 37B.", alias="box37BSecuritiesMarket")
    certify_box40: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 40.", alias="certifyBox40")
    box41_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The sponsoring entity information for box 41.", alias="box41SponsoringEntity")
    certify_box42: Optional[StrictBool] = Field(default=None, description="Indicates certification for box 42.", alias="certifyBox42")
    box35_formed_on_date: Optional[date] = Field(default=None, alias="box35FormedOnDate")
    box36_filed_on_date: Optional[date] = Field(default=None, alias="box36FiledOnDate")
    tin_match_status: Optional[StrictStr] = Field(default=None, description="The status of the TIN match.", alias="tinMatchStatus")
    signature: Optional[StrictStr] = Field(default=None, description="The signature itself")
    business_classification: Optional[StrictStr] = Field(default=None, description="The classification of the business.", alias="businessClassification")
    business_name: Optional[StrictStr] = Field(default=None, description="The name of the business associated with the form.", alias="businessName")
    business_other: Optional[StrictStr] = Field(default=None, alias="businessOther")
    exempt_payee_code: Optional[StrictStr] = Field(default=None, alias="exemptPayeeCode")
    exempt_fatca_code: Optional[StrictStr] = Field(default=None, alias="exemptFatcaCode")
    account_number: Optional[StrictStr] = Field(default=None, description="The account number associated with the form.", alias="accountNumber")
    foreign_country_indicator: Optional[StrictBool] = Field(default=None, description="Indicates whether the individual or entity is in a foreign country.", alias="foreignCountryIndicator")
    foreign_address: Optional[StrictStr] = Field(default=None, description="The foreign address of the individual or entity.", alias="foreignAddress")
    backup_withholding: Optional[StrictBool] = Field(default=None, description="Indicates whether backup withholding applies.", alias="backupWithholding")
    is1099able: Optional[StrictBool] = None
    foreign_partner_owner_or_beneficiary: Optional[StrictBool] = Field(default=None, description="Indicates whether the individual is a foreign partner, owner, or beneficiary.", alias="foreignPartnerOwnerOrBeneficiary")
    __properties: ClassVar[List[str]] = ["type", "signedDate", "createdAt", "employeeFirstName", "employeeMiddleName", "employeeLastName", "employeeNameSuffix", "address", "city", "state", "zip", "typeOfTin", "tin", "box3MaritalStatus", "box4LastNameDiffers", "box5NumAllowances", "otherDependents", "nonJobIncome", "deductions", "box6AdditionalWithheld", "box7ExemptFromWithholding", "officeCode", "eDeliveryConsentedAt", "disregardedEntityChapter4FatcaStatus", "name", "residenceAddress", "residenceCity", "residenceState", "residencePostalCode", "residenceCountry", "mailingAddress", "mailingCity", "mailingState", "mailingPostalCode", "mailingCountry", "disregardedAddress", "disregardedCity", "disregardedState", "disregardedPostalCode", "disregardedCountry", "foreignTin", "ftinNotRequired", "referenceNumber", "giin", "chapter3EntityType", "chapter4FatcaStatus", "disregardedEntity", "disregardedEntityGiin", "benefitLimitation", "part4SponsoringEntity", "part4SponsoringEntityGiin", "part7SponsoringEntity", "part12IgaCountry", "part12IgaType", "part12FatcaStatusUnderIgaAnnexIi", "part12TrusteeName", "part12TrusteeIsForeign", "part12Model2IgaGiin", "box37AExchange", "box37BExchange", "box37BEntity", "part28SponsoringEntity", "part28SponsoringEntityGiin", "signerName", "residenceIsMailing", "citizenshipCountry", "makingTreatyClaim", "treatyCountry", "treatyArticle", "withholdingRate", "incomeType", "treatyReasons", "certifyBox14A", "certifyBox14B", "certifyBox14C", "certifyBox17_1", "certifyBox17_2", "certifyBox18", "certifyBox19", "certifyBox21", "certifyBox22", "certifyBox23", "certifyBox24A", "certifyBox24B", "certifyBox24C", "certifyBox24D", "certifyBox25A", "certifyBox25B", "certifyBox25C", "certifyBox26", "certifyBox27", "certifyBox28A", "certifyBox28B", "certifyBox29A", "certifyBox29B", "certifyBox29C", "certifyBox29D", "certifyBox29E", "certifyBox29F", "certifyBox30", "certifyBox31", "certifyBox32", "certifyBox33", "certifyBox34", "certifyBox35", "certifyBox36", "certifyBox37A", "certifyBox37B", "certifyBox38", "certifyBox39", "certifyBox40A", "certifyBox40B", "certifyBox40C", "certifyBox41", "certifyBox43", "certifyPart29Signature", "part19FormationOrResolutionDate", "part20FilingDate", "part21DeterminationDate", "substantialUsOwners", "birthday", "foreignTinNotRequired", "archived", "referenceId", "companyId", "displayName", "email", "signerCapacity", "updatedAt", "ein", "einType", "certifyBox14", "certifyBox15A", "certifyBox15B", "certifyBox15C", "certifyBox15D", "certifyBox15E", "certifyBox15F", "certifyBox15G", "certifyBox15H", "certifyBox15I", "certifyBox16A", "box16BQddCorporate", "box16BQddPartnership", "box16BQddDisregardedEntity", "certifyBox17A", "certifyBox17B", "certifyBox17C", "certifyBox17D", "certifyBox17E", "certifyBox18A", "certifyBox18B", "certifyBox18C", "certifyBox18D", "certifyBox18E", "certifyBox18F", "certifyBox19A", "certifyBox19B", "certifyBox19C", "certifyBox19D", "certifyBox19E", "certifyBox19F", "certifyBox20", "certifyBox21A", "certifyBox21B", "certifyBox21C", "certifyBox21D", "certifyBox21E", "certifyBox21F", "box23ANameSponsoringEntity", "certifyBox23B", "certifyBox23C", "certifyBox25", "box27ANameSponsoringEntity", "certifyBox27B", "certifyBox28", "certifyBox29", "certifyBox30A", "certifyBox30B", "certifyBox30C", "box32IgaCountry", "box32IgaType", "box32IgaTreatedAs", "box32TrusteeOrSponsor", "box32TrusteeIsForeign", "certifyBox33A", "certifyBox33B", "certifyBox33C", "certifyBox33D", "certifyBox33E", "certifyBox33F", "box37ASecuritiesMarket", "box37BNameOfEntity", "box37BSecuritiesMarket", "certifyBox40", "box41SponsoringEntity", "certifyBox42", "box35FormedOnDate", "box36FiledOnDate", "tinMatchStatus", "signature", "businessClassification", "businessName", "businessOther", "exemptPayeeCode", "exemptFatcaCode", "accountNumber", "foreignCountryIndicator", "foreignAddress", "backupWithholding", "is1099able", "foreignPartnerOwnerOrBeneficiary"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['w9', 'w4', 'w8imy', 'w8ben', 'w8bene']):
            raise ValueError("must be one of enum values ('w9', 'w4', 'w8imy', 'w8ben', 'w8bene')")
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
        """Create an instance of W8BenFormDataModel from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "type",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in substantial_us_owners (list)
        _items = []
        if self.substantial_us_owners:
            for _item in self.substantial_us_owners:
                if _item:
                    _items.append(_item.to_dict())
            _dict['substantialUsOwners'] = _items
        # set to None if signed_date (nullable) is None
        # and model_fields_set contains the field
        if self.signed_date is None and "signed_date" in self.model_fields_set:
            _dict['signedDate'] = None

        # set to None if created_at (nullable) is None
        # and model_fields_set contains the field
        if self.created_at is None and "created_at" in self.model_fields_set:
            _dict['createdAt'] = None

        # set to None if employee_first_name (nullable) is None
        # and model_fields_set contains the field
        if self.employee_first_name is None and "employee_first_name" in self.model_fields_set:
            _dict['employeeFirstName'] = None

        # set to None if employee_middle_name (nullable) is None
        # and model_fields_set contains the field
        if self.employee_middle_name is None and "employee_middle_name" in self.model_fields_set:
            _dict['employeeMiddleName'] = None

        # set to None if employee_last_name (nullable) is None
        # and model_fields_set contains the field
        if self.employee_last_name is None and "employee_last_name" in self.model_fields_set:
            _dict['employeeLastName'] = None

        # set to None if employee_name_suffix (nullable) is None
        # and model_fields_set contains the field
        if self.employee_name_suffix is None and "employee_name_suffix" in self.model_fields_set:
            _dict['employeeNameSuffix'] = None

        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

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

        # set to None if type_of_tin (nullable) is None
        # and model_fields_set contains the field
        if self.type_of_tin is None and "type_of_tin" in self.model_fields_set:
            _dict['typeOfTin'] = None

        # set to None if tin (nullable) is None
        # and model_fields_set contains the field
        if self.tin is None and "tin" in self.model_fields_set:
            _dict['tin'] = None

        # set to None if box3_marital_status (nullable) is None
        # and model_fields_set contains the field
        if self.box3_marital_status is None and "box3_marital_status" in self.model_fields_set:
            _dict['box3MaritalStatus'] = None

        # set to None if box4_last_name_differs (nullable) is None
        # and model_fields_set contains the field
        if self.box4_last_name_differs is None and "box4_last_name_differs" in self.model_fields_set:
            _dict['box4LastNameDiffers'] = None

        # set to None if box5_num_allowances (nullable) is None
        # and model_fields_set contains the field
        if self.box5_num_allowances is None and "box5_num_allowances" in self.model_fields_set:
            _dict['box5NumAllowances'] = None

        # set to None if other_dependents (nullable) is None
        # and model_fields_set contains the field
        if self.other_dependents is None and "other_dependents" in self.model_fields_set:
            _dict['otherDependents'] = None

        # set to None if non_job_income (nullable) is None
        # and model_fields_set contains the field
        if self.non_job_income is None and "non_job_income" in self.model_fields_set:
            _dict['nonJobIncome'] = None

        # set to None if deductions (nullable) is None
        # and model_fields_set contains the field
        if self.deductions is None and "deductions" in self.model_fields_set:
            _dict['deductions'] = None

        # set to None if box6_additional_withheld (nullable) is None
        # and model_fields_set contains the field
        if self.box6_additional_withheld is None and "box6_additional_withheld" in self.model_fields_set:
            _dict['box6AdditionalWithheld'] = None

        # set to None if box7_exempt_from_withholding (nullable) is None
        # and model_fields_set contains the field
        if self.box7_exempt_from_withholding is None and "box7_exempt_from_withholding" in self.model_fields_set:
            _dict['box7ExemptFromWithholding'] = None

        # set to None if office_code (nullable) is None
        # and model_fields_set contains the field
        if self.office_code is None and "office_code" in self.model_fields_set:
            _dict['officeCode'] = None

        # set to None if e_delivery_consented_at (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_consented_at is None and "e_delivery_consented_at" in self.model_fields_set:
            _dict['eDeliveryConsentedAt'] = None

        # set to None if disregarded_entity_chapter4_fatca_status (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_entity_chapter4_fatca_status is None and "disregarded_entity_chapter4_fatca_status" in self.model_fields_set:
            _dict['disregardedEntityChapter4FatcaStatus'] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if residence_address (nullable) is None
        # and model_fields_set contains the field
        if self.residence_address is None and "residence_address" in self.model_fields_set:
            _dict['residenceAddress'] = None

        # set to None if residence_city (nullable) is None
        # and model_fields_set contains the field
        if self.residence_city is None and "residence_city" in self.model_fields_set:
            _dict['residenceCity'] = None

        # set to None if residence_state (nullable) is None
        # and model_fields_set contains the field
        if self.residence_state is None and "residence_state" in self.model_fields_set:
            _dict['residenceState'] = None

        # set to None if residence_postal_code (nullable) is None
        # and model_fields_set contains the field
        if self.residence_postal_code is None and "residence_postal_code" in self.model_fields_set:
            _dict['residencePostalCode'] = None

        # set to None if residence_country (nullable) is None
        # and model_fields_set contains the field
        if self.residence_country is None and "residence_country" in self.model_fields_set:
            _dict['residenceCountry'] = None

        # set to None if mailing_address (nullable) is None
        # and model_fields_set contains the field
        if self.mailing_address is None and "mailing_address" in self.model_fields_set:
            _dict['mailingAddress'] = None

        # set to None if mailing_city (nullable) is None
        # and model_fields_set contains the field
        if self.mailing_city is None and "mailing_city" in self.model_fields_set:
            _dict['mailingCity'] = None

        # set to None if mailing_state (nullable) is None
        # and model_fields_set contains the field
        if self.mailing_state is None and "mailing_state" in self.model_fields_set:
            _dict['mailingState'] = None

        # set to None if mailing_postal_code (nullable) is None
        # and model_fields_set contains the field
        if self.mailing_postal_code is None and "mailing_postal_code" in self.model_fields_set:
            _dict['mailingPostalCode'] = None

        # set to None if mailing_country (nullable) is None
        # and model_fields_set contains the field
        if self.mailing_country is None and "mailing_country" in self.model_fields_set:
            _dict['mailingCountry'] = None

        # set to None if disregarded_address (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_address is None and "disregarded_address" in self.model_fields_set:
            _dict['disregardedAddress'] = None

        # set to None if disregarded_city (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_city is None and "disregarded_city" in self.model_fields_set:
            _dict['disregardedCity'] = None

        # set to None if disregarded_state (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_state is None and "disregarded_state" in self.model_fields_set:
            _dict['disregardedState'] = None

        # set to None if disregarded_postal_code (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_postal_code is None and "disregarded_postal_code" in self.model_fields_set:
            _dict['disregardedPostalCode'] = None

        # set to None if disregarded_country (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_country is None and "disregarded_country" in self.model_fields_set:
            _dict['disregardedCountry'] = None

        # set to None if foreign_tin (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_tin is None and "foreign_tin" in self.model_fields_set:
            _dict['foreignTin'] = None

        # set to None if ftin_not_required (nullable) is None
        # and model_fields_set contains the field
        if self.ftin_not_required is None and "ftin_not_required" in self.model_fields_set:
            _dict['ftinNotRequired'] = None

        # set to None if reference_number (nullable) is None
        # and model_fields_set contains the field
        if self.reference_number is None and "reference_number" in self.model_fields_set:
            _dict['referenceNumber'] = None

        # set to None if giin (nullable) is None
        # and model_fields_set contains the field
        if self.giin is None and "giin" in self.model_fields_set:
            _dict['giin'] = None

        # set to None if chapter3_entity_type (nullable) is None
        # and model_fields_set contains the field
        if self.chapter3_entity_type is None and "chapter3_entity_type" in self.model_fields_set:
            _dict['chapter3EntityType'] = None

        # set to None if chapter4_fatca_status (nullable) is None
        # and model_fields_set contains the field
        if self.chapter4_fatca_status is None and "chapter4_fatca_status" in self.model_fields_set:
            _dict['chapter4FatcaStatus'] = None

        # set to None if disregarded_entity (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_entity is None and "disregarded_entity" in self.model_fields_set:
            _dict['disregardedEntity'] = None

        # set to None if disregarded_entity_giin (nullable) is None
        # and model_fields_set contains the field
        if self.disregarded_entity_giin is None and "disregarded_entity_giin" in self.model_fields_set:
            _dict['disregardedEntityGiin'] = None

        # set to None if benefit_limitation (nullable) is None
        # and model_fields_set contains the field
        if self.benefit_limitation is None and "benefit_limitation" in self.model_fields_set:
            _dict['benefitLimitation'] = None

        # set to None if part4_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.part4_sponsoring_entity is None and "part4_sponsoring_entity" in self.model_fields_set:
            _dict['part4SponsoringEntity'] = None

        # set to None if part4_sponsoring_entity_giin (nullable) is None
        # and model_fields_set contains the field
        if self.part4_sponsoring_entity_giin is None and "part4_sponsoring_entity_giin" in self.model_fields_set:
            _dict['part4SponsoringEntityGiin'] = None

        # set to None if part7_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.part7_sponsoring_entity is None and "part7_sponsoring_entity" in self.model_fields_set:
            _dict['part7SponsoringEntity'] = None

        # set to None if part12_iga_country (nullable) is None
        # and model_fields_set contains the field
        if self.part12_iga_country is None and "part12_iga_country" in self.model_fields_set:
            _dict['part12IgaCountry'] = None

        # set to None if part12_iga_type (nullable) is None
        # and model_fields_set contains the field
        if self.part12_iga_type is None and "part12_iga_type" in self.model_fields_set:
            _dict['part12IgaType'] = None

        # set to None if part12_fatca_status_under_iga_annex_ii (nullable) is None
        # and model_fields_set contains the field
        if self.part12_fatca_status_under_iga_annex_ii is None and "part12_fatca_status_under_iga_annex_ii" in self.model_fields_set:
            _dict['part12FatcaStatusUnderIgaAnnexIi'] = None

        # set to None if part12_trustee_name (nullable) is None
        # and model_fields_set contains the field
        if self.part12_trustee_name is None and "part12_trustee_name" in self.model_fields_set:
            _dict['part12TrusteeName'] = None

        # set to None if part12_trustee_is_foreign (nullable) is None
        # and model_fields_set contains the field
        if self.part12_trustee_is_foreign is None and "part12_trustee_is_foreign" in self.model_fields_set:
            _dict['part12TrusteeIsForeign'] = None

        # set to None if part12_model2_iga_giin (nullable) is None
        # and model_fields_set contains the field
        if self.part12_model2_iga_giin is None and "part12_model2_iga_giin" in self.model_fields_set:
            _dict['part12Model2IgaGiin'] = None

        # set to None if box37_a_exchange (nullable) is None
        # and model_fields_set contains the field
        if self.box37_a_exchange is None and "box37_a_exchange" in self.model_fields_set:
            _dict['box37AExchange'] = None

        # set to None if box37_b_exchange (nullable) is None
        # and model_fields_set contains the field
        if self.box37_b_exchange is None and "box37_b_exchange" in self.model_fields_set:
            _dict['box37BExchange'] = None

        # set to None if box37_b_entity (nullable) is None
        # and model_fields_set contains the field
        if self.box37_b_entity is None and "box37_b_entity" in self.model_fields_set:
            _dict['box37BEntity'] = None

        # set to None if part28_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.part28_sponsoring_entity is None and "part28_sponsoring_entity" in self.model_fields_set:
            _dict['part28SponsoringEntity'] = None

        # set to None if part28_sponsoring_entity_giin (nullable) is None
        # and model_fields_set contains the field
        if self.part28_sponsoring_entity_giin is None and "part28_sponsoring_entity_giin" in self.model_fields_set:
            _dict['part28SponsoringEntityGiin'] = None

        # set to None if signer_name (nullable) is None
        # and model_fields_set contains the field
        if self.signer_name is None and "signer_name" in self.model_fields_set:
            _dict['signerName'] = None

        # set to None if citizenship_country (nullable) is None
        # and model_fields_set contains the field
        if self.citizenship_country is None and "citizenship_country" in self.model_fields_set:
            _dict['citizenshipCountry'] = None

        # set to None if making_treaty_claim (nullable) is None
        # and model_fields_set contains the field
        if self.making_treaty_claim is None and "making_treaty_claim" in self.model_fields_set:
            _dict['makingTreatyClaim'] = None

        # set to None if treaty_country (nullable) is None
        # and model_fields_set contains the field
        if self.treaty_country is None and "treaty_country" in self.model_fields_set:
            _dict['treatyCountry'] = None

        # set to None if treaty_article (nullable) is None
        # and model_fields_set contains the field
        if self.treaty_article is None and "treaty_article" in self.model_fields_set:
            _dict['treatyArticle'] = None

        # set to None if withholding_rate (nullable) is None
        # and model_fields_set contains the field
        if self.withholding_rate is None and "withholding_rate" in self.model_fields_set:
            _dict['withholdingRate'] = None

        # set to None if income_type (nullable) is None
        # and model_fields_set contains the field
        if self.income_type is None and "income_type" in self.model_fields_set:
            _dict['incomeType'] = None

        # set to None if treaty_reasons (nullable) is None
        # and model_fields_set contains the field
        if self.treaty_reasons is None and "treaty_reasons" in self.model_fields_set:
            _dict['treatyReasons'] = None

        # set to None if part19_formation_or_resolution_date (nullable) is None
        # and model_fields_set contains the field
        if self.part19_formation_or_resolution_date is None and "part19_formation_or_resolution_date" in self.model_fields_set:
            _dict['part19FormationOrResolutionDate'] = None

        # set to None if part20_filing_date (nullable) is None
        # and model_fields_set contains the field
        if self.part20_filing_date is None and "part20_filing_date" in self.model_fields_set:
            _dict['part20FilingDate'] = None

        # set to None if part21_determination_date (nullable) is None
        # and model_fields_set contains the field
        if self.part21_determination_date is None and "part21_determination_date" in self.model_fields_set:
            _dict['part21DeterminationDate'] = None

        # set to None if birthday (nullable) is None
        # and model_fields_set contains the field
        if self.birthday is None and "birthday" in self.model_fields_set:
            _dict['birthday'] = None

        # set to None if foreign_tin_not_required (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_tin_not_required is None and "foreign_tin_not_required" in self.model_fields_set:
            _dict['foreignTinNotRequired'] = None

        # set to None if archived (nullable) is None
        # and model_fields_set contains the field
        if self.archived is None and "archived" in self.model_fields_set:
            _dict['archived'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if company_id (nullable) is None
        # and model_fields_set contains the field
        if self.company_id is None and "company_id" in self.model_fields_set:
            _dict['companyId'] = None

        # set to None if display_name (nullable) is None
        # and model_fields_set contains the field
        if self.display_name is None and "display_name" in self.model_fields_set:
            _dict['displayName'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if signer_capacity (nullable) is None
        # and model_fields_set contains the field
        if self.signer_capacity is None and "signer_capacity" in self.model_fields_set:
            _dict['signerCapacity'] = None

        # set to None if updated_at (nullable) is None
        # and model_fields_set contains the field
        if self.updated_at is None and "updated_at" in self.model_fields_set:
            _dict['updatedAt'] = None

        # set to None if ein (nullable) is None
        # and model_fields_set contains the field
        if self.ein is None and "ein" in self.model_fields_set:
            _dict['ein'] = None

        # set to None if ein_type (nullable) is None
        # and model_fields_set contains the field
        if self.ein_type is None and "ein_type" in self.model_fields_set:
            _dict['einType'] = None

        # set to None if box23_a_name_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.box23_a_name_sponsoring_entity is None and "box23_a_name_sponsoring_entity" in self.model_fields_set:
            _dict['box23ANameSponsoringEntity'] = None

        # set to None if box27_a_name_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.box27_a_name_sponsoring_entity is None and "box27_a_name_sponsoring_entity" in self.model_fields_set:
            _dict['box27ANameSponsoringEntity'] = None

        # set to None if box32_iga_country (nullable) is None
        # and model_fields_set contains the field
        if self.box32_iga_country is None and "box32_iga_country" in self.model_fields_set:
            _dict['box32IgaCountry'] = None

        # set to None if box32_iga_type (nullable) is None
        # and model_fields_set contains the field
        if self.box32_iga_type is None and "box32_iga_type" in self.model_fields_set:
            _dict['box32IgaType'] = None

        # set to None if box32_iga_treated_as (nullable) is None
        # and model_fields_set contains the field
        if self.box32_iga_treated_as is None and "box32_iga_treated_as" in self.model_fields_set:
            _dict['box32IgaTreatedAs'] = None

        # set to None if box32_trustee_or_sponsor (nullable) is None
        # and model_fields_set contains the field
        if self.box32_trustee_or_sponsor is None and "box32_trustee_or_sponsor" in self.model_fields_set:
            _dict['box32TrusteeOrSponsor'] = None

        # set to None if box37_a_securities_market (nullable) is None
        # and model_fields_set contains the field
        if self.box37_a_securities_market is None and "box37_a_securities_market" in self.model_fields_set:
            _dict['box37ASecuritiesMarket'] = None

        # set to None if box37_b_name_of_entity (nullable) is None
        # and model_fields_set contains the field
        if self.box37_b_name_of_entity is None and "box37_b_name_of_entity" in self.model_fields_set:
            _dict['box37BNameOfEntity'] = None

        # set to None if box37_b_securities_market (nullable) is None
        # and model_fields_set contains the field
        if self.box37_b_securities_market is None and "box37_b_securities_market" in self.model_fields_set:
            _dict['box37BSecuritiesMarket'] = None

        # set to None if box41_sponsoring_entity (nullable) is None
        # and model_fields_set contains the field
        if self.box41_sponsoring_entity is None and "box41_sponsoring_entity" in self.model_fields_set:
            _dict['box41SponsoringEntity'] = None

        # set to None if box35_formed_on_date (nullable) is None
        # and model_fields_set contains the field
        if self.box35_formed_on_date is None and "box35_formed_on_date" in self.model_fields_set:
            _dict['box35FormedOnDate'] = None

        # set to None if box36_filed_on_date (nullable) is None
        # and model_fields_set contains the field
        if self.box36_filed_on_date is None and "box36_filed_on_date" in self.model_fields_set:
            _dict['box36FiledOnDate'] = None

        # set to None if tin_match_status (nullable) is None
        # and model_fields_set contains the field
        if self.tin_match_status is None and "tin_match_status" in self.model_fields_set:
            _dict['tinMatchStatus'] = None

        # set to None if signature (nullable) is None
        # and model_fields_set contains the field
        if self.signature is None and "signature" in self.model_fields_set:
            _dict['signature'] = None

        # set to None if business_classification (nullable) is None
        # and model_fields_set contains the field
        if self.business_classification is None and "business_classification" in self.model_fields_set:
            _dict['businessClassification'] = None

        # set to None if business_name (nullable) is None
        # and model_fields_set contains the field
        if self.business_name is None and "business_name" in self.model_fields_set:
            _dict['businessName'] = None

        # set to None if business_other (nullable) is None
        # and model_fields_set contains the field
        if self.business_other is None and "business_other" in self.model_fields_set:
            _dict['businessOther'] = None

        # set to None if exempt_payee_code (nullable) is None
        # and model_fields_set contains the field
        if self.exempt_payee_code is None and "exempt_payee_code" in self.model_fields_set:
            _dict['exemptPayeeCode'] = None

        # set to None if exempt_fatca_code (nullable) is None
        # and model_fields_set contains the field
        if self.exempt_fatca_code is None and "exempt_fatca_code" in self.model_fields_set:
            _dict['exemptFatcaCode'] = None

        # set to None if account_number (nullable) is None
        # and model_fields_set contains the field
        if self.account_number is None and "account_number" in self.model_fields_set:
            _dict['accountNumber'] = None

        # set to None if foreign_country_indicator (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_country_indicator is None and "foreign_country_indicator" in self.model_fields_set:
            _dict['foreignCountryIndicator'] = None

        # set to None if foreign_address (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_address is None and "foreign_address" in self.model_fields_set:
            _dict['foreignAddress'] = None

        # set to None if backup_withholding (nullable) is None
        # and model_fields_set contains the field
        if self.backup_withholding is None and "backup_withholding" in self.model_fields_set:
            _dict['backupWithholding'] = None

        # set to None if is1099able (nullable) is None
        # and model_fields_set contains the field
        if self.is1099able is None and "is1099able" in self.model_fields_set:
            _dict['is1099able'] = None

        # set to None if foreign_partner_owner_or_beneficiary (nullable) is None
        # and model_fields_set contains the field
        if self.foreign_partner_owner_or_beneficiary is None and "foreign_partner_owner_or_beneficiary" in self.model_fields_set:
            _dict['foreignPartnerOwnerOrBeneficiary'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of W8BenFormDataModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "type": obj.get("type"),
            "signedDate": obj.get("signedDate"),
            "createdAt": obj.get("createdAt"),
            "employeeFirstName": obj.get("employeeFirstName"),
            "employeeMiddleName": obj.get("employeeMiddleName"),
            "employeeLastName": obj.get("employeeLastName"),
            "employeeNameSuffix": obj.get("employeeNameSuffix"),
            "address": obj.get("address"),
            "city": obj.get("city"),
            "state": obj.get("state"),
            "zip": obj.get("zip"),
            "typeOfTin": obj.get("typeOfTin"),
            "tin": obj.get("tin"),
            "box3MaritalStatus": obj.get("box3MaritalStatus"),
            "box4LastNameDiffers": obj.get("box4LastNameDiffers"),
            "box5NumAllowances": obj.get("box5NumAllowances"),
            "otherDependents": obj.get("otherDependents"),
            "nonJobIncome": obj.get("nonJobIncome"),
            "deductions": obj.get("deductions"),
            "box6AdditionalWithheld": obj.get("box6AdditionalWithheld"),
            "box7ExemptFromWithholding": obj.get("box7ExemptFromWithholding"),
            "officeCode": obj.get("officeCode"),
            "eDeliveryConsentedAt": obj.get("eDeliveryConsentedAt"),
            "disregardedEntityChapter4FatcaStatus": obj.get("disregardedEntityChapter4FatcaStatus"),
            "name": obj.get("name"),
            "residenceAddress": obj.get("residenceAddress"),
            "residenceCity": obj.get("residenceCity"),
            "residenceState": obj.get("residenceState"),
            "residencePostalCode": obj.get("residencePostalCode"),
            "residenceCountry": obj.get("residenceCountry"),
            "mailingAddress": obj.get("mailingAddress"),
            "mailingCity": obj.get("mailingCity"),
            "mailingState": obj.get("mailingState"),
            "mailingPostalCode": obj.get("mailingPostalCode"),
            "mailingCountry": obj.get("mailingCountry"),
            "disregardedAddress": obj.get("disregardedAddress"),
            "disregardedCity": obj.get("disregardedCity"),
            "disregardedState": obj.get("disregardedState"),
            "disregardedPostalCode": obj.get("disregardedPostalCode"),
            "disregardedCountry": obj.get("disregardedCountry"),
            "foreignTin": obj.get("foreignTin"),
            "ftinNotRequired": obj.get("ftinNotRequired"),
            "referenceNumber": obj.get("referenceNumber"),
            "giin": obj.get("giin"),
            "chapter3EntityType": obj.get("chapter3EntityType"),
            "chapter4FatcaStatus": obj.get("chapter4FatcaStatus"),
            "disregardedEntity": obj.get("disregardedEntity"),
            "disregardedEntityGiin": obj.get("disregardedEntityGiin"),
            "benefitLimitation": obj.get("benefitLimitation"),
            "part4SponsoringEntity": obj.get("part4SponsoringEntity"),
            "part4SponsoringEntityGiin": obj.get("part4SponsoringEntityGiin"),
            "part7SponsoringEntity": obj.get("part7SponsoringEntity"),
            "part12IgaCountry": obj.get("part12IgaCountry"),
            "part12IgaType": obj.get("part12IgaType"),
            "part12FatcaStatusUnderIgaAnnexIi": obj.get("part12FatcaStatusUnderIgaAnnexIi"),
            "part12TrusteeName": obj.get("part12TrusteeName"),
            "part12TrusteeIsForeign": obj.get("part12TrusteeIsForeign"),
            "part12Model2IgaGiin": obj.get("part12Model2IgaGiin"),
            "box37AExchange": obj.get("box37AExchange"),
            "box37BExchange": obj.get("box37BExchange"),
            "box37BEntity": obj.get("box37BEntity"),
            "part28SponsoringEntity": obj.get("part28SponsoringEntity"),
            "part28SponsoringEntityGiin": obj.get("part28SponsoringEntityGiin"),
            "signerName": obj.get("signerName"),
            "residenceIsMailing": obj.get("residenceIsMailing"),
            "citizenshipCountry": obj.get("citizenshipCountry"),
            "makingTreatyClaim": obj.get("makingTreatyClaim"),
            "treatyCountry": obj.get("treatyCountry"),
            "treatyArticle": obj.get("treatyArticle"),
            "withholdingRate": obj.get("withholdingRate"),
            "incomeType": obj.get("incomeType"),
            "treatyReasons": obj.get("treatyReasons"),
            "certifyBox14A": obj.get("certifyBox14A"),
            "certifyBox14B": obj.get("certifyBox14B"),
            "certifyBox14C": obj.get("certifyBox14C"),
            "certifyBox17_1": obj.get("certifyBox17_1"),
            "certifyBox17_2": obj.get("certifyBox17_2"),
            "certifyBox18": obj.get("certifyBox18"),
            "certifyBox19": obj.get("certifyBox19"),
            "certifyBox21": obj.get("certifyBox21"),
            "certifyBox22": obj.get("certifyBox22"),
            "certifyBox23": obj.get("certifyBox23"),
            "certifyBox24A": obj.get("certifyBox24A"),
            "certifyBox24B": obj.get("certifyBox24B"),
            "certifyBox24C": obj.get("certifyBox24C"),
            "certifyBox24D": obj.get("certifyBox24D"),
            "certifyBox25A": obj.get("certifyBox25A"),
            "certifyBox25B": obj.get("certifyBox25B"),
            "certifyBox25C": obj.get("certifyBox25C"),
            "certifyBox26": obj.get("certifyBox26"),
            "certifyBox27": obj.get("certifyBox27"),
            "certifyBox28A": obj.get("certifyBox28A"),
            "certifyBox28B": obj.get("certifyBox28B"),
            "certifyBox29A": obj.get("certifyBox29A"),
            "certifyBox29B": obj.get("certifyBox29B"),
            "certifyBox29C": obj.get("certifyBox29C"),
            "certifyBox29D": obj.get("certifyBox29D"),
            "certifyBox29E": obj.get("certifyBox29E"),
            "certifyBox29F": obj.get("certifyBox29F"),
            "certifyBox30": obj.get("certifyBox30"),
            "certifyBox31": obj.get("certifyBox31"),
            "certifyBox32": obj.get("certifyBox32"),
            "certifyBox33": obj.get("certifyBox33"),
            "certifyBox34": obj.get("certifyBox34"),
            "certifyBox35": obj.get("certifyBox35"),
            "certifyBox36": obj.get("certifyBox36"),
            "certifyBox37A": obj.get("certifyBox37A"),
            "certifyBox37B": obj.get("certifyBox37B"),
            "certifyBox38": obj.get("certifyBox38"),
            "certifyBox39": obj.get("certifyBox39"),
            "certifyBox40A": obj.get("certifyBox40A"),
            "certifyBox40B": obj.get("certifyBox40B"),
            "certifyBox40C": obj.get("certifyBox40C"),
            "certifyBox41": obj.get("certifyBox41"),
            "certifyBox43": obj.get("certifyBox43"),
            "certifyPart29Signature": obj.get("certifyPart29Signature"),
            "part19FormationOrResolutionDate": obj.get("part19FormationOrResolutionDate"),
            "part20FilingDate": obj.get("part20FilingDate"),
            "part21DeterminationDate": obj.get("part21DeterminationDate"),
            "substantialUsOwners": [W8BenESubstantialUsOwnerDataModel.from_dict(_item) for _item in obj["substantialUsOwners"]] if obj.get("substantialUsOwners") is not None else None,
            "birthday": obj.get("birthday"),
            "foreignTinNotRequired": obj.get("foreignTinNotRequired"),
            "archived": obj.get("archived"),
            "referenceId": obj.get("referenceId"),
            "companyId": obj.get("companyId"),
            "displayName": obj.get("displayName"),
            "email": obj.get("email"),
            "signerCapacity": obj.get("signerCapacity"),
            "updatedAt": obj.get("updatedAt"),
            "ein": obj.get("ein"),
            "einType": obj.get("einType"),
            "certifyBox14": obj.get("certifyBox14"),
            "certifyBox15A": obj.get("certifyBox15A"),
            "certifyBox15B": obj.get("certifyBox15B"),
            "certifyBox15C": obj.get("certifyBox15C"),
            "certifyBox15D": obj.get("certifyBox15D"),
            "certifyBox15E": obj.get("certifyBox15E"),
            "certifyBox15F": obj.get("certifyBox15F"),
            "certifyBox15G": obj.get("certifyBox15G"),
            "certifyBox15H": obj.get("certifyBox15H"),
            "certifyBox15I": obj.get("certifyBox15I"),
            "certifyBox16A": obj.get("certifyBox16A"),
            "box16BQddCorporate": obj.get("box16BQddCorporate"),
            "box16BQddPartnership": obj.get("box16BQddPartnership"),
            "box16BQddDisregardedEntity": obj.get("box16BQddDisregardedEntity"),
            "certifyBox17A": obj.get("certifyBox17A"),
            "certifyBox17B": obj.get("certifyBox17B"),
            "certifyBox17C": obj.get("certifyBox17C"),
            "certifyBox17D": obj.get("certifyBox17D"),
            "certifyBox17E": obj.get("certifyBox17E"),
            "certifyBox18A": obj.get("certifyBox18A"),
            "certifyBox18B": obj.get("certifyBox18B"),
            "certifyBox18C": obj.get("certifyBox18C"),
            "certifyBox18D": obj.get("certifyBox18D"),
            "certifyBox18E": obj.get("certifyBox18E"),
            "certifyBox18F": obj.get("certifyBox18F"),
            "certifyBox19A": obj.get("certifyBox19A"),
            "certifyBox19B": obj.get("certifyBox19B"),
            "certifyBox19C": obj.get("certifyBox19C"),
            "certifyBox19D": obj.get("certifyBox19D"),
            "certifyBox19E": obj.get("certifyBox19E"),
            "certifyBox19F": obj.get("certifyBox19F"),
            "certifyBox20": obj.get("certifyBox20"),
            "certifyBox21A": obj.get("certifyBox21A"),
            "certifyBox21B": obj.get("certifyBox21B"),
            "certifyBox21C": obj.get("certifyBox21C"),
            "certifyBox21D": obj.get("certifyBox21D"),
            "certifyBox21E": obj.get("certifyBox21E"),
            "certifyBox21F": obj.get("certifyBox21F"),
            "box23ANameSponsoringEntity": obj.get("box23ANameSponsoringEntity"),
            "certifyBox23B": obj.get("certifyBox23B"),
            "certifyBox23C": obj.get("certifyBox23C"),
            "certifyBox25": obj.get("certifyBox25"),
            "box27ANameSponsoringEntity": obj.get("box27ANameSponsoringEntity"),
            "certifyBox27B": obj.get("certifyBox27B"),
            "certifyBox28": obj.get("certifyBox28"),
            "certifyBox29": obj.get("certifyBox29"),
            "certifyBox30A": obj.get("certifyBox30A"),
            "certifyBox30B": obj.get("certifyBox30B"),
            "certifyBox30C": obj.get("certifyBox30C"),
            "box32IgaCountry": obj.get("box32IgaCountry"),
            "box32IgaType": obj.get("box32IgaType"),
            "box32IgaTreatedAs": obj.get("box32IgaTreatedAs"),
            "box32TrusteeOrSponsor": obj.get("box32TrusteeOrSponsor"),
            "box32TrusteeIsForeign": obj.get("box32TrusteeIsForeign"),
            "certifyBox33A": obj.get("certifyBox33A"),
            "certifyBox33B": obj.get("certifyBox33B"),
            "certifyBox33C": obj.get("certifyBox33C"),
            "certifyBox33D": obj.get("certifyBox33D"),
            "certifyBox33E": obj.get("certifyBox33E"),
            "certifyBox33F": obj.get("certifyBox33F"),
            "box37ASecuritiesMarket": obj.get("box37ASecuritiesMarket"),
            "box37BNameOfEntity": obj.get("box37BNameOfEntity"),
            "box37BSecuritiesMarket": obj.get("box37BSecuritiesMarket"),
            "certifyBox40": obj.get("certifyBox40"),
            "box41SponsoringEntity": obj.get("box41SponsoringEntity"),
            "certifyBox42": obj.get("certifyBox42"),
            "box35FormedOnDate": obj.get("box35FormedOnDate"),
            "box36FiledOnDate": obj.get("box36FiledOnDate"),
            "tinMatchStatus": obj.get("tinMatchStatus"),
            "signature": obj.get("signature"),
            "businessClassification": obj.get("businessClassification"),
            "businessName": obj.get("businessName"),
            "businessOther": obj.get("businessOther"),
            "exemptPayeeCode": obj.get("exemptPayeeCode"),
            "exemptFatcaCode": obj.get("exemptFatcaCode"),
            "accountNumber": obj.get("accountNumber"),
            "foreignCountryIndicator": obj.get("foreignCountryIndicator"),
            "foreignAddress": obj.get("foreignAddress"),
            "backupWithholding": obj.get("backupWithholding"),
            "is1099able": obj.get("is1099able"),
            "foreignPartnerOwnerOrBeneficiary": obj.get("foreignPartnerOwnerOrBeneficiary")
        })
        return _obj


