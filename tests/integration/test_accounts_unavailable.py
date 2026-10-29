"""Интеграционная проверка недоступного сервиса клиентов."""

import os
import time

import httpx

ORDERS_URL = os.getenv("ORDERS_URL", "http://localhost:8002")


def test_orders_returns_503_when_accounts_is_unavailable() -> None:
    started_at = time.monotonic()
    response = httpx.post(
        f"{ORDERS_URL}/orders",
        json={"account_id": 1, "item": "Тестовый товар", "quantity": 1},
        timeout=4.0,
    )
    elapsed_seconds = time.monotonic() - started_at

    assert response.status_code == 503, response.text
    assert response.json()["detail"] == "Сервис клиентов не отвечает"
    assert elapsed_seconds <= 3.0
