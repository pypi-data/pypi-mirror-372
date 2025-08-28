# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .company_registration import CompanyRegistration

__all__ = ["CompanyListResponse"]

CompanyListResponse: TypeAlias = List[CompanyRegistration]
