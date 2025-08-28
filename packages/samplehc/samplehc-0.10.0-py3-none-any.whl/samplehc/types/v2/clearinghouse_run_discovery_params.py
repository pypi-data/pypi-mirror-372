# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClearinghouseRunDiscoveryParams", "Person"]


class ClearinghouseRunDiscoveryParams(TypedDict, total=False):
    person: Required[Person]

    account_number: Annotated[str, PropertyInfo(alias="accountNumber")]
    """Account number"""

    check_credit: Annotated[bool, PropertyInfo(alias="checkCredit")]
    """Whether to check credit"""

    check_demographics: Annotated[bool, PropertyInfo(alias="checkDemographics")]
    """Whether to check demographics"""

    date_of_service: Annotated[str, PropertyInfo(alias="dateOfService")]
    """Date of service (YYYY-MM-DD)"""

    run_business_rules: Annotated[bool, PropertyInfo(alias="runBusinessRules")]
    """Whether to run business rules"""

    service_code: Annotated[str, PropertyInfo(alias="serviceCode")]
    """Service code"""

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]


class Person(TypedDict, total=False):
    address_line1: Annotated[str, PropertyInfo(alias="addressLine1")]
    """Patient's address line 1"""

    address_line2: Annotated[str, PropertyInfo(alias="addressLine2")]
    """Patient's address line 2"""

    city: str
    """Patient's city"""

    date_of_birth: Annotated[str, PropertyInfo(alias="dateOfBirth")]
    """Patient's date of birth (YYYY-MM-DD)"""

    first_name: Annotated[str, PropertyInfo(alias="firstName")]
    """Patient's first name"""

    last_name: Annotated[str, PropertyInfo(alias="lastName")]
    """Patient's last name"""

    state: str
    """Patient's state"""

    zip: str
    """Patient's ZIP code"""
