# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClearinghouseCheckClaimStatusParams"]


class ClearinghouseCheckClaimStatusParams(TypedDict, total=False):
    provider_npi: Required[Annotated[str, PropertyInfo(alias="providerNpi")]]
    """The provider's NPI number"""

    subscriber_date_of_birth: Required[Annotated[str, PropertyInfo(alias="subscriberDateOfBirth")]]
    """The subscriber's date of birth (YYYY-MM-DD format)"""

    subscriber_first_name: Required[Annotated[str, PropertyInfo(alias="subscriberFirstName")]]
    """The subscriber's first name"""

    subscriber_last_name: Required[Annotated[str, PropertyInfo(alias="subscriberLastName")]]
    """The subscriber's last name"""

    subscriber_member_id: Required[Annotated[str, PropertyInfo(alias="subscriberMemberId")]]
    """The subscriber's member ID"""

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]
    """The Payer ID in our clearinghouse"""

    payer_claim_number: Annotated[str, PropertyInfo(alias="payerClaimNumber")]
    """The payer claim number (ICN) to check status for"""

    provider_name: Annotated[str, PropertyInfo(alias="providerName")]
    """The provider's organization name"""

    service_from_date: Annotated[str, PropertyInfo(alias="serviceFromDate")]
    """The beginning date of service (YYYY-MM-DD format)"""

    service_to_date: Annotated[str, PropertyInfo(alias="serviceToDate")]
    """The ending date of service (YYYY-MM-DD format)"""
