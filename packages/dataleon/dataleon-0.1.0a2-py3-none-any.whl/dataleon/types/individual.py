# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.check import Check
from .individuals.generic_document import GenericDocument

__all__ = [
    "Individual",
    "AmlSuspicion",
    "Certificat",
    "IdentityCard",
    "Person",
    "Property",
    "Risk",
    "Tag",
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


class IdentityCard(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the document."""

    back_document_signed_url: Optional[str] = None
    """Signed URL linking to the back image of the document."""

    birth_place: Optional[str] = None
    """Place of birth as indicated on the document."""

    birthday: Optional[str] = None
    """Date of birth in DD/MM/YYYY format as shown on the document."""

    country: Optional[str] = None
    """Country code issuing the document (ISO 3166-1 alpha-2)."""

    expiration_date: Optional[str] = None
    """Expiration date of the document, in YYYY-MM-DD format."""

    first_name: Optional[str] = None
    """First name as shown on the document."""

    front_document_signed_url: Optional[str] = None
    """Signed URL linking to the front image of the document."""

    gender: Optional[str] = None
    """Gender indicated on the document (e.g., "M" or "F")."""

    issue_date: Optional[str] = None
    """Date when the document was issued, in YYYY-MM-DD format."""

    last_name: Optional[str] = None
    """Last name as shown on the document."""

    mrz_line_1: Optional[str] = None
    """First line of the Machine Readable Zone (MRZ) on the document."""

    mrz_line_2: Optional[str] = None
    """Second line of the MRZ on the document."""

    mrz_line_3: Optional[str] = None
    """Third line of the MRZ if applicable; otherwise null."""

    type: Optional[str] = None
    """Type of document (e.g., passport, identity card)."""


class Person(BaseModel):
    birthday: Optional[str] = None
    """Date of birth, formatted as DD/MM/YYYY."""

    email: Optional[str] = None
    """Email address of the individual."""

    face_image_signed_url: Optional[str] = None
    """Signed URL linking to the person’s face image."""

    first_name: Optional[str] = None
    """First (given) name of the person."""

    full_name: Optional[str] = None
    """Full name of the person, typically concatenation of first and last names."""

    gender: Optional[str] = None
    """Gender of the individual (e.g., "M" for male, "F" for female)."""

    last_name: Optional[str] = None
    """Last (family) name of the person."""

    maiden_name: Optional[str] = None
    """Maiden name of the person, if applicable."""

    phone_number: Optional[str] = None
    """Contact phone number including country code."""


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


class Tag(BaseModel):
    key: Optional[str] = None
    """Name of the tag used to identify the metadata field."""

    private: Optional[bool] = None
    """Indicates whether the tag is private (not visible to external users)."""

    type: Optional[str] = None
    """Data type of the tag value (e.g., "string", "number", "boolean")."""

    value: Optional[str] = None
    """Value assigned to the tag."""


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


class Individual(BaseModel):
    id: Optional[str] = None
    """Unique identifier of the individual."""

    aml_suspicions: Optional[List[AmlSuspicion]] = None
    """List of AML (Anti-Money Laundering) suspicion entries linked to the individual."""

    auth_url: Optional[str] = None
    """URL to authenticate the individual, usually for document signing or onboarding."""

    certificat: Optional[Certificat] = None
    """Digital certificate associated with the individual, if any."""

    checks: Optional[List[Check]] = None
    """List of verification or validation checks applied to the individual."""

    created_at: Optional[datetime] = None
    """Timestamp of the individual's creation in ISO 8601 format."""

    documents: Optional[List[GenericDocument]] = None
    """All documents submitted or associated with the individual."""

    identity_card: Optional[IdentityCard] = None
    """Reference to the individual's identity document."""

    number: Optional[int] = None
    """Internal sequential number or reference for the individual."""

    person: Optional[Person] = None
    """
    Personal details of the individual, such as name, date of birth, and contact
    info.
    """

    portal_url: Optional[str] = None
    """Admin or internal portal URL for viewing the individual's details."""

    properties: Optional[List[Property]] = None
    """Custom key-value metadata fields associated with the individual."""

    risk: Optional[Risk] = None
    """Risk assessment associated with the individual."""

    source_id: Optional[str] = None
    """Optional identifier indicating the source of the individual record."""

    state: Optional[str] = None
    """
    Current operational state in the workflow (e.g., WAITING, IN_PROGRESS,
    COMPLETED).
    """

    status: Optional[str] = None
    """
    Overall processing status of the individual (e.g., rejected, need_review,
    approved).
    """

    tags: Optional[List[Tag]] = None
    """
    List of tags assigned to the individual for categorization or metadata purposes.
    """

    technical_data: Optional[TechnicalData] = None
    """Technical metadata related to the request (e.g., QR code settings, language)."""

    webview_url: Optional[str] = None
    """Public-facing webview URL for the individual’s identification process."""

    workspace_id: Optional[str] = None
    """Identifier of the workspace to which the individual belongs."""
