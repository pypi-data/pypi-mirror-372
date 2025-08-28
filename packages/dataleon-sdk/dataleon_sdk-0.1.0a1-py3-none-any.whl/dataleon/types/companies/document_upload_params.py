# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from ..._types import FileTypes

__all__ = ["DocumentUploadParams"]


class DocumentUploadParams(TypedDict, total=False):
    document_type: Required[
        Literal[
            "liasse_fiscale",
            "amortised_loan_schedule",
            "invoice",
            "receipt",
            "company_statuts",
            "registration_company_certificate",
            "kbis",
            "rib",
            "livret_famille",
            "birth_certificate",
            "payslip",
            "social_security_card",
            "vehicle_registration_certificate",
            "carte_grise",
            "criminal_record_extract",
            "proof_of_address",
            "identity_card_front",
            "identity_card_back",
            "driver_license_front",
            "driver_license_back",
            "identity_document",
            "driver_license",
            "passport",
            "tax",
            "certificate_of_incorporation",
            "certificate_of_good_standing",
            "lcb_ft_lab_aml_policies",
            "niu_entreprise",
            "financial_statements",
            "rccm",
            "proof_of_source_funds",
            "organizational_chart",
            "risk_policies",
        ]
    ]
    """Filter by document type for upload (must be one of the allowed values)"""

    file: FileTypes
    """File to upload (required)"""

    url: str
    """URL of the file to upload (either `file` or `url` is required)"""
