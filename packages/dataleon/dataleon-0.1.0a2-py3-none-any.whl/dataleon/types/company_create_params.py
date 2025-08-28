# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CompanyCreateParams", "Company", "TechnicalData"]


class CompanyCreateParams(TypedDict, total=False):
    company: Required[Company]
    """Main information about the company being registered."""

    workspace_id: Required[str]
    """Unique identifier of the workspace in which the company is being created."""

    source_id: str
    """
    Optional identifier to track the origin of the request or integration from your
    system.
    """

    technical_data: TechnicalData
    """Technical metadata and callback configuration."""


class Company(TypedDict, total=False):
    name: Required[str]
    """Legal name of the company."""

    address: str
    """Registered address of the company."""

    commercial_name: str
    """Commercial or trade name of the company, if different from the legal name."""

    country: str
    """
    ISO 3166-1 alpha-2 country code of company registration (e.g., "FR" for France).
    """

    email: str
    """Contact email address for the company."""

    employer_identification_number: str
    """Employer Identification Number (EIN) or equivalent."""

    legal_form: str
    """Legal structure of the company (e.g., SARL, SAS)."""

    phone_number: str
    """Contact phone number for the company."""

    registration_date: str
    """Date of official company registration in YYYY-MM-DD format."""

    registration_id: str
    """Official company registration identifier."""

    share_capital: str
    """Declared share capital of the company, usually in euros."""

    status: str
    """Current status of the company (e.g., active, inactive)."""

    tax_identification_number: str
    """National tax identifier (e.g., VAT or TIN)."""

    type: str
    """Type of company, such as "main" or "affiliated"."""

    website_url: str
    """Company’s official website URL."""


class TechnicalData(TypedDict, total=False):
    active_aml_suspicions: bool
    """
    Flag indicating whether there are active research AML (Anti-Money Laundering)
    suspicions for the company when you apply for a new entry or get an existing
    one.
    """

    callback_url: str
    """URL to receive a callback once the company is processed."""

    callback_url_notification: str
    """URL to receive notifications about the processing state and status."""

    language: str
    """Preferred language for responses or notifications (e.g., "eng", "fra")."""

    raw_data: bool
    """Flag indicating whether to include raw data in the response."""
