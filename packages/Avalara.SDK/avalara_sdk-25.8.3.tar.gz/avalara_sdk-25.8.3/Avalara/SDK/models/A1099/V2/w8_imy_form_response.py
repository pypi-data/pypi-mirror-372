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

from datetime import date
from pydantic import ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from Avalara.SDK.models.A1099.V2.entry_status_response import EntryStatusResponse
from Avalara.SDK.models.A1099.V2.w9_form_base_response import W9FormBaseResponse
from typing import Optional, Set
from typing_extensions import Self

class W8ImyFormResponse(W9FormBaseResponse):
    """
    W8ImyFormResponse
    """ # noqa: E501
    name: Optional[StrictStr] = Field(default=None, description="The name of the individual or entity associated with the form.")
    citizenship_country: Optional[StrictStr] = Field(default=None, description="The country of citizenship.", alias="citizenshipCountry")
    disregarded_entity: Optional[StrictStr] = Field(default=None, description="The name of the disregarded entity receiving the payment (if applicable).", alias="disregardedEntity")
    entity_type: Optional[StrictStr] = Field(default=None, description="The entity type.", alias="entityType")
    fatca_status: Optional[StrictStr] = Field(default=None, description="The FATCA status.", alias="fatcaStatus")
    residence_address: Optional[StrictStr] = Field(default=None, description="The residential address of the individual or entity.", alias="residenceAddress")
    residence_city: Optional[StrictStr] = Field(default=None, description="The city of residence.", alias="residenceCity")
    residence_state: Optional[StrictStr] = Field(default=None, description="The state of residence.", alias="residenceState")
    residence_zip: Optional[StrictStr] = Field(default=None, description="The ZIP code of the residence.", alias="residenceZip")
    residence_country: Optional[StrictStr] = Field(default=None, description="The country of residence.", alias="residenceCountry")
    residence_is_mailing: Optional[StrictBool] = Field(default=None, description="Indicates whether the residence address is also the mailing address.", alias="residenceIsMailing")
    mailing_address: Optional[StrictStr] = Field(default=None, description="The mailing address.", alias="mailingAddress")
    mailing_city: Optional[StrictStr] = Field(default=None, description="The city of the mailing address.", alias="mailingCity")
    mailing_state: Optional[StrictStr] = Field(default=None, description="The state of the mailing address.", alias="mailingState")
    mailing_zip: Optional[StrictStr] = Field(default=None, description="The ZIP code of the mailing address.", alias="mailingZip")
    mailing_country: Optional[StrictStr] = Field(default=None, description="The country of the mailing address.", alias="mailingCountry")
    tin_type: Optional[StrictStr] = Field(default=None, description="The type of TIN provided.", alias="tinType")
    tin: Optional[StrictStr] = Field(default=None, description="The taxpayer identification number (TIN).")
    giin: Optional[StrictStr] = Field(default=None, description="The global intermediary identification number (GIIN).")
    foreign_tin: Optional[StrictStr] = Field(default=None, description="The foreign taxpayer identification number (TIN).", alias="foreignTin")
    reference_number: Optional[StrictStr] = Field(default=None, description="A reference number for the form.", alias="referenceNumber")
    disregarded_entity_fatca_status: Optional[StrictStr] = Field(default=None, description="The FATCA status of disregarded entity or branch receiving payment.", alias="disregardedEntityFatcaStatus")
    disregarded_address: Optional[StrictStr] = Field(default=None, description="The address for disregarded entities.", alias="disregardedAddress")
    disregarded_city: Optional[StrictStr] = Field(default=None, description="The city for disregarded entities.", alias="disregardedCity")
    disregarded_state: Optional[StrictStr] = Field(default=None, description="The state for disregarded entities.", alias="disregardedState")
    disregarded_zip: Optional[StrictStr] = Field(default=None, description="The ZIP code for disregarded entities.", alias="disregardedZip")
    disregarded_country: Optional[StrictStr] = Field(default=None, description="The country for disregarded entities.", alias="disregardedCountry")
    disregarded_entity_giin: Optional[StrictStr] = Field(default=None, description="The GIIN for disregarded entities.", alias="disregardedEntityGiin")
    qualified_intermediary_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a Qualified Intermediary (QI) acting in accordance with its QI Agreement,  providing required withholding statements and documentation for relevant tax withholding purposes.", alias="qualifiedIntermediaryCertification")
    qi_primary_withholding_responsibility_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary assumes primary withholding responsibility  under chapters 3 and 4 for the specified accounts.", alias="qiPrimaryWithholdingResponsibilityCertification")
    qi_withholding_responsibility_for_ptp_sales_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary assumes primary withholding and reporting responsibility under section 1446(f)  for amounts realized from sales of interests in publicly traded partnerships.", alias="qiWithholdingResponsibilityForPtpSalesCertification")
    qi_nominee_withholding_responsibility_for_ptp_distributions_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary assumes primary withholding responsibility as a nominee  under Regulations section 1.1446-4(b)(3) for publicly traded partnership distributions.", alias="qiNomineeWithholdingResponsibilityForPtpDistributionsCertification")
    qi_securities_lender_substitute_dividend_withholding_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary is acting as a qualified securities lender and assumes primary withholding  and reporting responsibilities for U.S. source substitute dividend payments.", alias="qiSecuritiesLenderSubstituteDividendWithholdingCertification")
    qi_withholding_and1099_reporting_responsibility_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary assumes primary withholding under chapters 3 and 4, and primary Form 1099 reporting  and backup withholding responsibility for U.S. source interest and substitute interest payments.", alias="qiWithholdingAnd1099ReportingResponsibilityCertification")
    qi_form1099_or_fatca_reporting_responsibility_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary assumes Form 1099 reporting and backup withholding responsibility,  or FATCA reporting responsibility as a participating or registered deemed-compliant FFI,  for accounts held by specified U.S. persons.", alias="qiForm1099OrFatcaReportingResponsibilityCertification")
    qi_opt_out_of_form1099_reporting_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary does not assume primary Form 1099 reporting  and backup withholding responsibility for the accounts associated with this form.", alias="qiOptOutOfForm1099ReportingCertification")
    qi_withholding_rate_pool_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary meets the requirements for allocating payments  to a chapter 4 withholding rate pool of U.S. payees under Regulations section 1.6049-4(c)(4)(iii).", alias="qiWithholdingRatePoolCertification")
    qi_intermediary_or_flow_through_entity_documentation_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Intermediary has obtained or will obtain documentation confirming the status of any intermediary  or flow-through entity as a participating FFI, registered deemed-compliant FFI,  or QI for U.S. payees in a chapter 4 withholding rate pool.", alias="qiIntermediaryOrFlowThroughEntityDocumentationCertification")
    qualified_derivatives_dealer_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the Qualified Derivatives Dealer (QDD) is approved by the IRS and assumes primary withholding  and reporting responsibilities for payments related to potential section 871(m) transactions.", alias="qualifiedDerivativesDealerCertification")
    qdd_corporation: Optional[StrictBool] = Field(default=None, description="Indicates QDD classification is Corporation.", alias="qddCorporation")
    qdd_partnership: Optional[StrictBool] = Field(default=None, description="Indicates QDD classification is Partnership.", alias="qddPartnership")
    qdd_disregarded_entity: Optional[StrictBool] = Field(default=None, description="Indicates QDD classification is Disregarded Entity.", alias="qddDisregardedEntity")
    nonqualified_intermediary_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is not acting as a Qualified Intermediary  and is not acting for its own account for the accounts covered by this form.", alias="nonqualifiedIntermediaryCertification")
    nqi_withholding_statement_transmission_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the nonqualified intermediary is submitting this form to transmit withholding certificates  and/or other required documentation along with a withholding statement.", alias="nqiWithholdingStatementTransmissionCertification")
    nqi_withholding_rate_pool_compliance_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the nonqualified intermediary meets the requirements of Regulations section 1.6049-4(c)(4)(iii)  for U.S. payees included in a withholding rate pool, excluding publicly traded partnership distributions.", alias="nqiWithholdingRatePoolComplianceCertification")
    nqi_qualified_securities_lender_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the nonqualified intermediary is acting as a qualified securities lender (not as a QI)  and assumes primary withholding and reporting responsibilities for U.S. source substitute dividend payments.", alias="nqiQualifiedSecuritiesLenderCertification")
    nqi_alternative_withholding_statement_verification_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the nonqualified intermediary has verified, or will verify,  all information on alternative withholding statements for consistency with account data to determine the correct withholding rate,  as required under sections 1441 or 1471.", alias="nqiAlternativeWithholdingStatementVerificationCertification")
    territory_financial_institution_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a financial institution (other than an investment entity) that is incorporated  or organized under the laws of a possession of the United States.", alias="territoryFinancialInstitutionCertification")
    tfi_treated_as_us_person_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the territory financial institution agrees to be treated as a U.S. person  for chapters 3 and 4 purposes concerning reportable amounts and withholdable payments.", alias="tfiTreatedAsUsPersonCertification")
    tfi_withholding_statement_transmission_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the territory financial institution is transmitting withholding certificates or other required documentation  and has provided or will provide a withholding statement for reportable or withholdable payments.", alias="tfiWithholdingStatementTransmissionCertification")
    tfi_treated_as_us_person_for_ptp_sales_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the territory financial institution agrees to be treated as a U.S. person  under Regulations section 1.1446(f)-4(a)(2)(i)(B) for amounts realized from sales of publicly traded partnership interests.", alias="tfiTreatedAsUsPersonForPtpSalesCertification")
    tfi_nominee_us_person_for_ptp_distributions_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the territory financial institution agrees to be treated as a U.S. person  and as a nominee for purposes of publicly traded partnership distributions under the applicable regulations.", alias="tfiNomineeUsPersonForPtpDistributionsCertification")
    tfi_not_nominee_for_ptp_distributions_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the territory financial institution is not acting as a nominee for publicly traded partnership distributions  and is providing withholding statements for those distributions.", alias="tfiNotNomineeForPtpDistributionsCertification")
    us_branch_non_effectively_connected_income_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch is receiving reportable or withholdable payments  that are not effectively connected income, PTP distributions, or proceeds from PTP sales.", alias="usBranchNonEffectivelyConnectedIncomeCertification")
    us_branch_agreement_to_be_treated_as_us_person_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch of a foreign bank or insurance company agrees to be treated as a U.S. person  for reportable amounts or withholdable payments under the applicable regulations.", alias="usBranchAgreementToBeTreatedAsUsPersonCertification")
    us_branch_withholding_statement_and_compliance_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch is transmitting required documentation  and withholding statements for reportable or withholdable payments and is applying the appropriate FATCA regulations.", alias="usBranchWithholdingStatementAndComplianceCertification")
    us_branch_acting_as_us_person_for_ptp_sales_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch is acting as a U.S. person  for purposes of amounts realized from sales of publicly traded partnership interests under the applicable regulations.", alias="usBranchActingAsUsPersonForPtpSalesCertification")
    us_branch_nominee_for_ptp_distributions_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch is treated as a U.S. person  and as a nominee for publicly traded partnership distributions under the applicable regulations.", alias="usBranchNomineeForPtpDistributionsCertification")
    us_branch_not_nominee_for_ptp_distributions_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the U.S. branch is not acting as a nominee for publicly traded partnership distributions  and is providing the required withholding statements.", alias="usBranchNotNomineeForPtpDistributionsCertification")
    withholding_foreign_partnership_or_trust_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a withholding foreign partnership (WP) or a withholding foreign trust (WT)  that is compliant with the terms of its WP or WT agreement.", alias="withholdingForeignPartnershipOrTrustCertification")
    nonwithholding_foreign_entity_withholding_statement_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a nonwithholding foreign partnership or trust,  providing the form for non-effectively connected payments and transmitting required withholding documentation for chapters 3 and 4.", alias="nonwithholdingForeignEntityWithholdingStatementCertification")
    foreign_entity_partner_in_lower_tier_partnership_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign partnership or grantor trust acting as a partner in a lower-tier partnership  and is submitting the form for purposes of section 1446(a).", alias="foreignEntityPartnerInLowerTierPartnershipCertification")
    foreign_partnership_amount_realized_section1446_f_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign partnership receiving an amount realized  from the transfer of a partnership interest for purposes of section 1446(f).", alias="foreignPartnershipAmountRealizedSection1446FCertification")
    foreign_partnership_modified_amount_realized_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the foreign partnership is providing a withholding statement for a modified amount realized  from the transfer of a partnership interest, when applicable.", alias="foreignPartnershipModifiedAmountRealizedCertification")
    foreign_grantor_trust_amount_realized_allocation_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the foreign grantor trust is submitting the form on behalf of each grantor or owner  and providing a withholding statement to allocate the amount realized in accordance with the regulations.", alias="foreignGrantorTrustAmountRealizedAllocationCertification")
    alternative_withholding_statement_reliance_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity may rely on the information in all associated withholding certificates  under the applicable standards of knowledge in sections 1441 or 1471 when providing an alternative withholding statement.", alias="alternativeWithholdingStatementRelianceCertification")
    np_ffi_with_exempt_beneficial_owners_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the nonparticipating FFI is transmitting withholding documentation  and providing a statement allocating payment portions to exempt beneficial owners.", alias="npFfiWithExemptBeneficialOwnersCertification")
    ffi_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The name of the entity that sponsors the foreign financial institution (FFI).", alias="ffiSponsoringEntity")
    investment_entity_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is an investment entity, not a QI, WP, or WT, and has an agreement with a sponsoring entity.", alias="investmentEntityCertification")
    controlled_foreign_corporation_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a controlled foreign corporation sponsored by a U.S. financial institution, not a QI, WP, or WT,  and shares a common electronic account system for full transparency.", alias="controlledForeignCorporationCertification")
    owner_documented_ffi_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the FFI meets all requirements to qualify as an owner-documented FFI, including restrictions on activities,  ownership, and account relationships.", alias="ownerDocumentedFfiCertification")
    owner_documented_ffi_reporting_statement_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the FFI will provide a complete owner reporting statement  and required documentation for each relevant owner or debt holder.", alias="ownerDocumentedFfiReportingStatementCertification")
    owner_documented_ffi_auditor_letter_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the FFI has provided or will provide an auditor’s letter and required owner documentation,  including a reporting statement and Form W-9s, to meet owner-documented FFI requirements under the regulations.", alias="ownerDocumentedFfiAuditorLetterCertification")
    compliant_nonregistering_local_bank_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the FFI operates solely as a limited bank or credit union within its country, meets asset thresholds,  and has no foreign operations or affiliations outside its country of organization.", alias="compliantNonregisteringLocalBankCertification")
    compliant_ffi_low_value_accounts_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the FFI is not primarily engaged in investment activities, maintains only low-value accounts,  and has limited total assets within its group.", alias="compliantFfiLowValueAccountsCertification")
    sponsored_closely_held_entity_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The name of sponsoring entity for a certified deemed-compliant, closely held investment vehicle.", alias="sponsoredCloselyHeldEntitySponsoringEntity")
    sponsored_closely_held_investment_vehicle_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a sponsored investment entity with 20 or fewer individual owners,  and that all compliance obligations are fulfilled by the sponsoring entity.", alias="sponsoredCloselyHeldInvestmentVehicleCertification")
    compliant_limited_life_debt_entity_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity qualifies as a limited life debt investment entity based on its formation date, issuance terms,  and compliance with regulatory requirements.", alias="compliantLimitedLifeDebtEntityCertification")
    investment_entity_no_financial_accounts_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a financial institution solely because it is an investment entity under regulations  and the entity does not maintain financial accounts.", alias="investmentEntityNoFinancialAccountsCertification")
    restricted_distributor_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity qualifies as a restricted distributor based on its operations, customer base, regulatory compliance,  and financial and geographic limitations.", alias="restrictedDistributorCertification")
    restricted_distributor_agreement_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is, and has been, bound by distribution agreements prohibiting sales of fund interests to  specified U.S. persons and certain non-U.S. entities.", alias="restrictedDistributorAgreementCertification")
    restricted_distributor_preexisting_sales_compliance_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity complies with distribution restrictions for U.S.-linked investors  and has addressed any preexisting sales in accordance with FATCA regulations.", alias="restrictedDistributorPreexistingSalesComplianceCertification")
    foreign_central_bank_of_issue_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is treated as the beneficial owner of the payment solely  for purposes of chapter 4 under Regulations section 1.1471-6(d)(4).", alias="foreignCentralBankOfIssueCertification")
    nonreporting_iga_ffi_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity meets the requirements to be considered a nonreporting financial institution to an applicable IGA.", alias="nonreportingIgaFfiCertification")
    iga_country: Optional[StrictStr] = Field(default=None, description="The country for the applicable IGA with the United States.", alias="igaCountry")
    iga_model: Optional[StrictStr] = Field(default=None, description="The applicable IGA model.", alias="igaModel")
    iga_legal_status_treatment: Optional[StrictStr] = Field(default=None, description="Specifies how the applicable IGA is treated under the IGA provisions or Treasury regulations.", alias="igaLegalStatusTreatment")
    iga_ffi_trustee_or_sponsor: Optional[StrictStr] = Field(default=None, description="The trustee or sponsor name for the nonreporting IGA FFI.", alias="igaFfiTrusteeOrSponsor")
    iga_ffi_trustee_is_foreign: Optional[StrictBool] = Field(default=None, description="Indicates whether the trustee for the nonreporting IGA FFI is foreign.", alias="igaFfiTrusteeIsForeign")
    treaty_qualified_pension_fund_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a pension or retirement fund established in a treaty country  and is entitled to treaty benefits on U.S. source income.", alias="treatyQualifiedPensionFundCertification")
    qualified_retirement_fund_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a government-regulated retirement fund meeting specific requirements for contributions, tax exemption,  beneficiary limits, and distribution restrictions.", alias="qualifiedRetirementFundCertification")
    narrow_participation_retirement_fund_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a government-regulated retirement fund with fewer than 50 participants, limited foreign ownership,  and employer sponsorship that is not from investment entities or passive NFFEs.", alias="narrowParticipationRetirementFundCertification")
    section401_a_equivalent_pension_plan_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is formed under a pension plan meeting section 401(a) requirements, except for being U.S.-trust funded.", alias="section401AEquivalentPensionPlanCertification")
    investment_entity_for_retirement_funds_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is established solely to earn income for the benefit of qualifying retirement funds  or accounts under applicable FATCA regulations or IGAs.", alias="investmentEntityForRetirementFundsCertification")
    exempt_beneficial_owner_sponsored_retirement_fund_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is established and sponsored by a qualifying exempt beneficial owner to provide retirement, disability,  or death benefits to individuals based on services performed for the sponsor.", alias="exemptBeneficialOwnerSponsoredRetirementFundCertification")
    excepted_nonfinancial_group_entity_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a holding company, treasury center, or captive finance company operating within a nonfinancial group  and not functioning as an investment or financial institution.", alias="exceptedNonfinancialGroupEntityCertification")
    excepted_nonfinancial_start_up_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a recently formed startup NFFE investing in a non-financial business  and is not operating as or presenting itself as an investment fund.", alias="exceptedNonfinancialStartUpCertification")
    startup_formation_or_resolution_date: Optional[date] = Field(default=None, description="The date the start-up company was formed on (or, in case of new line of business, the date of board resolution approving the  new line of business).", alias="startupFormationOrResolutionDate")
    excepted_nonfinancial_entity_in_liquidation_or_bankruptcy_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is in liquidation, reorganization, or bankruptcy and intends to operate as a nonfinancial entity,  with supporting documentation available if the process exceeds three years.", alias="exceptedNonfinancialEntityInLiquidationOrBankruptcyCertification")
    nonfinancial_entity_filing_date: Optional[date] = Field(default=None, description="The filed date for a plan of reorganization, liquidation or bankruptcy.", alias="nonfinancialEntityFilingDate")
    publicly_traded_nffe_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign corporation that is not a financial institution  and whose stock is regularly traded on an established securities market.", alias="publiclyTradedNffeCertification")
    publicly_traded_nffe_securities_market: Optional[StrictStr] = Field(default=None, description="The name of the securities market where the corporation's stock is regularly traded.", alias="publiclyTradedNffeSecuritiesMarket")
    nffe_affiliate_of_publicly_traded_entity_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign corporation that is not a financial institution  and is affiliated with a publicly traded entity within the same expanded affiliated group.", alias="nffeAffiliateOfPubliclyTradedEntityCertification")
    publicly_traded_entity: Optional[StrictStr] = Field(default=None, description="The name of the affiliated entity whose stock is regularly traded on an established securities market.", alias="publiclyTradedEntity")
    nffe_affiliate_of_publicly_traded_entity_securities_market: Optional[StrictStr] = Field(default=None, description="The name of the established securities market where the affiliated entity's stock is traded.", alias="nffeAffiliateOfPubliclyTradedEntitySecuritiesMarket")
    excepted_territory_nffe_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is organized in a U.S. possession, is not engaged in financial activities,  and is entirely owned by bona fide residents of that possession.", alias="exceptedTerritoryNffeCertification")
    active_nffe_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign non-financial institution with less than 50% passive income  and less than 50% of its assets producing or held to produce passive income.", alias="activeNffeCertification")
    passive_nffe_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a foreign non-financial entity that does not qualify for any other NFFE category  and is not a financial institution.", alias="passiveNffeCertification")
    sponsored_direct_reporting_nffe_certification: Optional[StrictBool] = Field(default=None, description="Certifies that the entity is a sponsored direct reporting NFFE.", alias="sponsoredDirectReportingNffeCertification")
    direct_reporting_nffe_sponsoring_entity: Optional[StrictStr] = Field(default=None, description="The name of the entity that sponsors the direct reporting NFFE.", alias="directReportingNffeSponsoringEntity")
    signer_name: Optional[StrictStr] = Field(default=None, description="The name of the signer.", alias="signerName")
    __properties: ClassVar[List[str]] = ["id", "entryStatus", "referenceId", "companyId", "displayName", "email", "archived", "ancestorId", "signature", "signedDate", "eDeliveryConsentedAt", "createdAt", "updatedAt", "type"]

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
        """Create an instance of W8ImyFormResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of entry_status
        if self.entry_status:
            _dict['entryStatus'] = self.entry_status.to_dict()
        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if ancestor_id (nullable) is None
        # and model_fields_set contains the field
        if self.ancestor_id is None and "ancestor_id" in self.model_fields_set:
            _dict['ancestorId'] = None

        # set to None if signature (nullable) is None
        # and model_fields_set contains the field
        if self.signature is None and "signature" in self.model_fields_set:
            _dict['signature'] = None

        # set to None if signed_date (nullable) is None
        # and model_fields_set contains the field
        if self.signed_date is None and "signed_date" in self.model_fields_set:
            _dict['signedDate'] = None

        # set to None if e_delivery_consented_at (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_consented_at is None and "e_delivery_consented_at" in self.model_fields_set:
            _dict['eDeliveryConsentedAt'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of W8ImyFormResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "entryStatus": EntryStatusResponse.from_dict(obj["entryStatus"]) if obj.get("entryStatus") is not None else None,
            "referenceId": obj.get("referenceId"),
            "companyId": obj.get("companyId"),
            "displayName": obj.get("displayName"),
            "email": obj.get("email"),
            "archived": obj.get("archived"),
            "ancestorId": obj.get("ancestorId"),
            "signature": obj.get("signature"),
            "signedDate": obj.get("signedDate"),
            "eDeliveryConsentedAt": obj.get("eDeliveryConsentedAt"),
            "createdAt": obj.get("createdAt"),
            "updatedAt": obj.get("updatedAt"),
            "type": obj.get("type")
        })
        return _obj


