from fastapi import FastAPI, status
from httpx import AsyncClient

from app.core.config import Settings
from app.core.errors import AppError


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


async def test_openapi_docs_are_served(client: AsyncClient) -> None:
    docs = await client.get("/docs")
    schema = await client.get("/openapi.json")

    assert docs.status_code == status.HTTP_200_OK
    assert "/api/v1/health" in schema.json()["paths"]


async def test_unknown_route_uses_common_error_format(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    error = response.json()["error"]
    assert error["code"] == "HTTP_404"
    assert error["request_id"] == response.headers["X-Request-ID"]


async def test_app_error_is_converted(app: FastAPI, client: AsyncClient) -> None:
    async def fail() -> None:
        raise AppError("EVENT_NOT_OPEN", "Inscriptions fermées.", status.HTTP_409_CONFLICT)

    app.add_api_route("/boom", fail)

    response = await client.get("/boom")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error"]["code"] == "EVENT_NOT_OPEN"


async def test_unexpected_error_hides_details(app: FastAPI, client: AsyncClient) -> None:
    async def crash() -> None:
        raise RuntimeError("secret interne")

    app.add_api_route("/crash", crash)

    response = await client.get("/crash")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert response.json()["error"]["request_id"]
    assert "secret interne" not in response.text


async def test_validation_error_does_not_echo_input(app: FastAPI, client: AsyncClient) -> None:
    async def typed(value: int) -> int:
        return value

    app.add_api_route("/typed", typed)

    response = await client.get("/typed", params={"value": "valeur-sensible"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "valeur-sensible" not in response.text


def test_cors_origins_are_parsed_from_comma_separated_value() -> None:
    settings = Settings(_env_file=None, cors_origins="http://a.test, http://b.test")  # type: ignore[call-arg]

    assert settings.cors_origins == ["http://a.test", "http://b.test"]
