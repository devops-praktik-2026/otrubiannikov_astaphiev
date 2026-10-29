"""Тесты запросов к сервису заказов."""

from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from orders.db import Base, get_session
from orders.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_get_session() -> Iterator[Session]:
    with TestSession() as session:
        yield session


@pytest.fixture()
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def order_payload() -> dict:
    return {"account_id": 1, "item": "Кофемолка", "quantity": 2}


@pytest.fixture(autouse=True)
def account_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    def successful_response(url: str, timeout: float) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(status_code=200, request=request)

    monkeypatch.setattr("orders.accounts_client.httpx.get", successful_response)


def test_read_created_order_returns_200_and_card(client: TestClient, order_payload: dict):
    created_response = client.request(method="POST", url="/orders", json=order_payload)
    assert created_response.status_code == 201
    created_order = created_response.json()

    response = client.request(method="GET", url=f"/orders/{created_order['id']}")

    assert response.status_code == 200
    assert response.json() == created_order


def test_read_nonexistent_order_returns_404(client: TestClient):
    response = client.request(method="GET", url="/orders/999999")

    assert response.status_code == 404
    assert str(999999) in response.json()["detail"]


def test_create_order_for_nonexistent_account_returns_404(
    client: TestClient,
    order_payload: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    def not_found_response(url: str, timeout: float) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(status_code=404, request=request)

    monkeypatch.setattr("orders.accounts_client.httpx.get", not_found_response)

    response = client.post("/orders", json=order_payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "account 1 not found"
