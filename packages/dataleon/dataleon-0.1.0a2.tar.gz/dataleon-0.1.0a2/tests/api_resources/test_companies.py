# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from dataleon import Dataleon, AsyncDataleon
from tests.utils import assert_matches_type
from dataleon.types import (
    CompanyListResponse,
    CompanyRegistration,
)
from dataleon._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompanies:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Dataleon) -> None:
        company = client.companies.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Dataleon) -> None:
        company = client.companies.create(
            company={
                "name": "ACME Corp",
                "address": "123 rue Exemple, Paris",
                "commercial_name": "ACME",
                "country": "FR",
                "email": "info@acme.fr",
                "employer_identification_number": "EIN123456",
                "legal_form": "SARL",
                "phone_number": "+33 1 23 45 67 89",
                "registration_date": "2010-05-15",
                "registration_id": "RCS123456",
                "share_capital": "100000",
                "status": "active",
                "tax_identification_number": "FR123456789",
                "type": "main",
                "website_url": "https://acme.fr",
            },
            workspace_id="wk_123",
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Dataleon) -> None:
        response = client.companies.with_raw_response.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Dataleon) -> None:
        with client.companies.with_streaming_response.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Dataleon) -> None:
        company = client.companies.retrieve(
            company_id="company_id",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Dataleon) -> None:
        company = client.companies.retrieve(
            company_id="company_id",
            document=True,
            scope="scope",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Dataleon) -> None:
        response = client.companies.with_raw_response.retrieve(
            company_id="company_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Dataleon) -> None:
        with client.companies.with_streaming_response.retrieve(
            company_id="company_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            client.companies.with_raw_response.retrieve(
                company_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Dataleon) -> None:
        company = client.companies.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Dataleon) -> None:
        company = client.companies.update(
            company_id="company_id",
            company={
                "name": "ACME Corp",
                "address": "123 rue Exemple, Paris",
                "commercial_name": "ACME",
                "country": "FR",
                "email": "info@acme.fr",
                "employer_identification_number": "EIN123456",
                "legal_form": "SARL",
                "phone_number": "+33 1 23 45 67 89",
                "registration_date": "2010-05-15",
                "registration_id": "RCS123456",
                "share_capital": "100000",
                "status": "active",
                "tax_identification_number": "FR123456789",
                "type": "main",
                "website_url": "https://acme.fr",
            },
            workspace_id="wk_123",
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Dataleon) -> None:
        response = client.companies.with_raw_response.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Dataleon) -> None:
        with client.companies.with_streaming_response.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            client.companies.with_raw_response.update(
                company_id="",
                company={"name": "ACME Corp"},
                workspace_id="wk_123",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Dataleon) -> None:
        company = client.companies.list()
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Dataleon) -> None:
        company = client.companies.list(
            end_date=parse_date("2019-12-27"),
            limit=1,
            offset=0,
            source_id="source_id",
            start_date=parse_date("2019-12-27"),
            state="VOID",
            status="rejected",
            workspace_id="workspace_id",
        )
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Dataleon) -> None:
        response = client.companies.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = response.parse()
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Dataleon) -> None:
        with client.companies.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = response.parse()
            assert_matches_type(CompanyListResponse, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Dataleon) -> None:
        company = client.companies.delete(
            "company_id",
        )
        assert company is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Dataleon) -> None:
        response = client.companies.with_raw_response.delete(
            "company_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = response.parse()
        assert company is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Dataleon) -> None:
        with client.companies.with_streaming_response.delete(
            "company_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = response.parse()
            assert company is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            client.companies.with_raw_response.delete(
                "",
            )


class TestAsyncCompanies:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.create(
            company={
                "name": "ACME Corp",
                "address": "123 rue Exemple, Paris",
                "commercial_name": "ACME",
                "country": "FR",
                "email": "info@acme.fr",
                "employer_identification_number": "EIN123456",
                "legal_form": "SARL",
                "phone_number": "+33 1 23 45 67 89",
                "registration_date": "2010-05-15",
                "registration_id": "RCS123456",
                "share_capital": "100000",
                "status": "active",
                "tax_identification_number": "FR123456789",
                "type": "main",
                "website_url": "https://acme.fr",
            },
            workspace_id="wk_123",
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDataleon) -> None:
        response = await async_client.companies.with_raw_response.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = await response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDataleon) -> None:
        async with async_client.companies.with_streaming_response.create(
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = await response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.retrieve(
            company_id="company_id",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.retrieve(
            company_id="company_id",
            document=True,
            scope="scope",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncDataleon) -> None:
        response = await async_client.companies.with_raw_response.retrieve(
            company_id="company_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = await response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncDataleon) -> None:
        async with async_client.companies.with_streaming_response.retrieve(
            company_id="company_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = await response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            await async_client.companies.with_raw_response.retrieve(
                company_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.update(
            company_id="company_id",
            company={
                "name": "ACME Corp",
                "address": "123 rue Exemple, Paris",
                "commercial_name": "ACME",
                "country": "FR",
                "email": "info@acme.fr",
                "employer_identification_number": "EIN123456",
                "legal_form": "SARL",
                "phone_number": "+33 1 23 45 67 89",
                "registration_date": "2010-05-15",
                "registration_id": "RCS123456",
                "share_capital": "100000",
                "status": "active",
                "tax_identification_number": "FR123456789",
                "type": "main",
                "website_url": "https://acme.fr",
            },
            workspace_id="wk_123",
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDataleon) -> None:
        response = await async_client.companies.with_raw_response.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = await response.parse()
        assert_matches_type(CompanyRegistration, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDataleon) -> None:
        async with async_client.companies.with_streaming_response.update(
            company_id="company_id",
            company={"name": "ACME Corp"},
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = await response.parse()
            assert_matches_type(CompanyRegistration, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            await async_client.companies.with_raw_response.update(
                company_id="",
                company={"name": "ACME Corp"},
                workspace_id="wk_123",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.list()
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.list(
            end_date=parse_date("2019-12-27"),
            limit=1,
            offset=0,
            source_id="source_id",
            start_date=parse_date("2019-12-27"),
            state="VOID",
            status="rejected",
            workspace_id="workspace_id",
        )
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDataleon) -> None:
        response = await async_client.companies.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = await response.parse()
        assert_matches_type(CompanyListResponse, company, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDataleon) -> None:
        async with async_client.companies.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = await response.parse()
            assert_matches_type(CompanyListResponse, company, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncDataleon) -> None:
        company = await async_client.companies.delete(
            "company_id",
        )
        assert company is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDataleon) -> None:
        response = await async_client.companies.with_raw_response.delete(
            "company_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        company = await response.parse()
        assert company is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDataleon) -> None:
        async with async_client.companies.with_streaming_response.delete(
            "company_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            company = await response.parse()
            assert company is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `company_id` but received ''"):
            await async_client.companies.with_raw_response.delete(
                "",
            )
