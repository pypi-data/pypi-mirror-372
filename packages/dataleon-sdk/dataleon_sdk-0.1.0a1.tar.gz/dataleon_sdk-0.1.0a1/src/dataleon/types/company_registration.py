# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.check import Check
from .individuals.generic_document import GenericDocument

__all__ = [
    "CompanyRegistration",
    "AmlSuspicion",
    "Certificat",
    "Company",
    "CompanyContact",
    "Member",
    "Property",
    "Risk",
    "TechnicalData",
]


class AmlSuspicion(BaseModel):
    caption: Optional[str] = None
    """Human-readable description or title for the suspicious finding."""

    country: Optional[str] = None
    """Country associated with the suspicion (ISO 3166-1 alpha-2 code)."""

    gender: Optional[str] = None
    """Gender associated with the suspicion, if applicable."""

    relation: Optional[str] = None
    """
    Nature of the relationship between the entity and the suspicious activity (e.g.,
    "linked", "associated").
    """

    schema_: Optional[str] = FieldInfo(alias="schema", default=None)
    """Version of the evaluation schema or rule engine used."""

    score: Optional[float] = None
    """Risk score between 0.0 and 1 indicating the severity of the suspicion."""

    source: Optional[str] = None
    """Source system or service providing this suspicion."""

    status: Optional[Literal["true_positive", "false_positive", "pending"]] = None
    """Status of the suspicion review process.

    Possible values: "true_positive", "false_positive", "pending".
    """

    type: Optional[Literal["crime", "sanction", "pep", "adverse_news", "other"]] = None
    """Category of the suspicion.

    Possible values: "crime", "sanction", "pep", "adverse_news", "other".
    """


class Certificat(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the certificate."""

    created_at: Optional[datetime] = None
    """Timestamp when the certificate was created."""

    filename: Optional[str] = None
    """Name of the certificate file."""


class CompanyContact(BaseModel):
    department: Optional[str] = None
    """Department of the contact person."""

    email: Optional[str] = None
    """Email address of the contact person."""

    first_name: Optional[str] = None
    """First name of the contact person."""

    last_name: Optional[str] = None
    """Last name of the contact person."""

    phone_number: Optional[str] = None
    """Phone number of the contact person."""


class Company(BaseModel):
    address: Optional[str] = None
    """Full registered address of the company."""

    closure_date: Optional[date] = None
    """Closure date of the company, if applicable."""

    commercial_name: Optional[str] = None
    """Trade or commercial name of the company."""

    contact: Optional[CompanyContact] = None
    """
    Contact information for the company, including email, phone number, and address.
    """

    country: Optional[str] = None
    """Country code where the company is registered."""

    email: Optional[str] = None
    """Contact email address for the company."""

    employees: Optional[int] = None
    """Number of employees in the company."""

    employer_identification_number: Optional[str] = None
    """Employer Identification Number (EIN) or equivalent."""

    insolvency_exists: Optional[bool] = None
    """Indicates whether an insolvency procedure exists for the company."""

    insolvency_ongoing: Optional[bool] = None
    """Indicates whether an insolvency procedure is ongoing for the company."""

    legal_form: Optional[str] = None
    """Legal form or structure of the company (e.g., LLC, SARL)."""

    name: Optional[str] = None
    """Legal registered name of the company."""

    phone_number: Optional[str] = None
    """Contact phone number for the company, including country code."""

    registration_date: Optional[date] = None
    """Date when the company was officially registered."""

    registration_id: Optional[str] = None
    """Official company registration number or ID."""

    share_capital: Optional[str] = None
    """Total share capital of the company, including currency."""

    status: Optional[str] = None
    """Current status of the company (e.g., active, inactive)."""

    tax_identification_number: Optional[str] = None
    """Tax identification number for the company."""

    type: Optional[str] = None
    """Type of company within the workspace, e.g., main or affiliated."""

    website_url: Optional[str] = None
    """Official website URL of the company."""


class Member(BaseModel):
    id: Optional[str] = None

    address: Optional[str] = None
    """
    Address of the member, which may include street, city, postal code, and country.
    """

    birthday: Optional[datetime] = None
    """Birthday (available only if type = person)"""

    birthplace: Optional[str] = None
    """Birthplace (available only if type = person)"""

    country: Optional[str] = None
    """
    ISO 3166-1 alpha-2 country code of the member's address (e.g., "FR" for France).
    """

    documents: Optional[List[GenericDocument]] = None
    """
    List of documents associated with the member, including their metadata and
    processing status.
    """

    email: Optional[str] = None
    """
    Email address of the member, which may be used for communication or verification
    purposes.
    """

    first_name: Optional[str] = None
    """First name (available only if type = person)"""

    is_beneficial_owner: Optional[bool] = None
    """
    Indicates whether the member is a beneficial owner of the company, meaning they
    have significant control or ownership.
    """

    is_delegator: Optional[bool] = None
    """
    Indicates whether the member is a delegator, meaning they have authority to act
    on behalf of the company.
    """

    last_name: Optional[str] = None
    """Last name (available only if type = person)"""

    liveness_verification: Optional[bool] = None
    """
    Indicates whether liveness verification was performed for the member, typically
    in the context of identity checks.
    """

    name: Optional[str] = None
    """Company name (available only if type = company)"""

    ownership_percentage: Optional[int] = None
    """
    Percentage of ownership the member has in the company, expressed as an integer
    between 0 and 100.
    """

    phone_number: Optional[str] = None
    """Contact phone number of the member, including country code and area code."""

    postal_code: Optional[str] = None
    """Postal code of the member's address, typically a numeric or alphanumeric code."""

    registration_id: Optional[str] = None
    """
    Official registration identifier of the member, such as a national ID or company
    registration number.
    """

    relation: Optional[str] = None
    """
    Type of relationship the member has with the company, such as "shareholder",
    "director", or "beneficial_owner".
    """

    roles: Optional[str] = None
    """
    Role of the member within the company, such as "legal_representative",
    "director", or "manager".
    """

    source: Optional[Literal["gouve", "user", "company"]] = None
    """Source of the data (e.g., government, user, company)"""

    state: Optional[str] = None
    """
    Current state of the member in the workflow, such as "WAITING", "STARTED",
    "RUNNING", or "PROCESSED".
    """

    status: Optional[str] = None
    """
    Status of the member in the system, indicating whether they are approved,
    pending, or rejected. Possible values include "approved", "need_review",
    "rejected".
    """

    type: Optional[Literal["person", "company"]] = None
    """Member type (person or company)"""

    workspace_id: Optional[str] = None
    """
    Identifier of the workspace to which the member belongs, used for organizational
    purposes.
    """


class Property(BaseModel):
    name: Optional[str] = None
    """Name/key of the property."""

    type: Optional[str] = None
    """Data type of the property value."""

    value: Optional[str] = None
    """Value associated with the property name."""


class Risk(BaseModel):
    code: Optional[str] = None
    """Risk category or code identifier."""

    reason: Optional[str] = None
    """Explanation or justification for the assigned risk."""

    score: Optional[float] = None
    """Numeric risk score between 0.0 and 1.0 indicating severity or confidence."""


class TechnicalData(BaseModel):
    active_aml_suspicions: Optional[bool] = None
    """
    Flag indicating whether there are active research AML (Anti-Money Laundering)
    suspicions for the object when you apply for a new entry or get an existing one.
    """

    api_version: Optional[int] = None
    """Version number of the API used."""

    approved_at: Optional[datetime] = None
    """Timestamp when the request or process was approved."""

    callback_url: Optional[str] = None
    """URL to receive callback data from the AML system."""

    callback_url_notification: Optional[str] = None
    """URL to receive notification updates about the processing status."""

    disable_notification: Optional[bool] = None
    """Flag to indicate if notifications are disabled."""

    disable_notification_date: Optional[datetime] = None
    """Timestamp when notifications were disabled; null if never disabled."""

    export_type: Optional[str] = None
    """Export format defined by the API (e.g., "json", "xml")."""

    finished_at: Optional[datetime] = None
    """Timestamp when the process finished."""

    ip: Optional[str] = None
    """IP address of the our system handling the request."""

    language: Optional[str] = None
    """Language preference used in the client workspace (e.g., "fra")."""

    location_ip: Optional[str] = None
    """IP address of the end client (final user) captured."""

    need_review_at: Optional[datetime] = None
    """Timestamp indicating when the request or process needs review; null if none."""

    notification_confirmation: Optional[bool] = None
    """Flag indicating if notification confirmation is required or received."""

    qr_code: Optional[str] = None
    """Indicates whether QR code is enabled ("true" or "false")."""

    raw_data: Optional[bool] = None
    """Flag indicating whether to include raw data in the response."""

    rejected_at: Optional[datetime] = None
    """Timestamp when the request or process was rejected; null if not rejected."""

    session_duration: Optional[int] = None
    """Duration of the user session in seconds."""

    started_at: Optional[datetime] = None
    """Timestamp when the process started."""

    transfer_at: Optional[datetime] = None
    """Date/time of data transfer."""

    transfer_mode: Optional[str] = None
    """Mode of data transfer."""


class CompanyRegistration(BaseModel):
    aml_suspicions: Optional[List[AmlSuspicion]] = None
    """
    List of AML (Anti-Money Laundering) suspicion entries linked to the company,
    including their details.
    """

    certificat: Optional[Certificat] = None
    """
    Digital certificate associated with the company, if any, including its creation
    timestamp and filename.
    """

    checks: Optional[List[Check]] = None
    """
    List of verification or validation checks applied to the company, including
    their results and messages.
    """

    company: Optional[Company] = None
    """
    Main information about the company being registered, including legal name,
    registration ID, and address.
    """

    documents: Optional[List[GenericDocument]] = None
    """
    All documents submitted or associated with the company, including their metadata
    and processing status.
    """

    members: Optional[List[Member]] = None
    """
    List of members or actors associated with the company, including personal and
    ownership information.
    """

    portal_url: Optional[str] = None
    """
    Admin or internal portal URL for viewing the company's details, typically used
    by internal users.
    """

    properties: Optional[List[Property]] = None
    """
    Custom key-value metadata fields associated with the company, allowing for
    flexible data storage.
    """

    risk: Optional[Risk] = None
    """
    Risk assessment associated with the company, including a risk code, reason, and
    confidence score.
    """

    source_id: Optional[str] = None
    """
    Optional identifier indicating the source of the company record, useful for
    tracking or integration purposes.
    """

    technical_data: Optional[TechnicalData] = None
    """
    Technical metadata related to the request, such as IP address, QR code settings,
    and callback URLs.
    """

    webview_url: Optional[str] = None
    """
    Public-facing webview URL for the company’s identification process, allowing
    external access to the company data.
    """
