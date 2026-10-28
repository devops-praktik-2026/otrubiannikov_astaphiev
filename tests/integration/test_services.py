"""Интеграционная проверка взаимодействия сервисов."""

import os
import time
from uuid import uuid4

import httpx

ACCOUNTS_URL = os.getenv("ACCOUNTS_URL", "http://localhost:8001")
ORDERS_URL = os.getenv("ORDERS_URL", "http://localhost:8002")


def wait_for_service(url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            response = httpx.get(f"{url}/health", timeout=1.0)
            if response.status_code == 200:
                return
        except httpx.RequestError:
            pass
        time.sleep(0.5)
    raise AssertionError(f"Сервис {url} не запустился за {timeout_seconds} секунд")


def test_create_order_for_created_account() -> None:
    wait_for_service(ACCOUNTS_URL)
    wait_for_service(ORDERS_URL)

    email = f"integration-{uuid4()}@example.com"
    account_response = httpx.post(
        f"{ACCOUNTS_URL}/accounts",
        json={"name": "Интеграционный тест", "email": email},
        timeout=5.0,
    )

    assert account_response.status_code == 201, account_response.text
    account_id = account_response.json()["id"]

    order_response = httpx.post(
        f"{ORDERS_URL}/orders",
        json={"account_id": account_id, "item": "Тестовый товар", "quantity": 1},
        timeout=5.0,
    )

    assert order_response.status_code == 201, order_response.text
    assert order_response.json()["account_id"] == account_id
