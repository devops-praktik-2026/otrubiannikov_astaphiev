"""Заведомо падающий тест

СЕЙЧАС ОН ПРОПУСКАЕТСЯ. Снимите строку со skip ниже, запустите проверки
и убедитесь, что тест падает. Это нормальное и правильное состояние:
сначала появляется тест, который описывает нужное поведение, и только
потом — код, который заставляет его пройти.

"""

import pytest
from fastapi.testclient import TestClient

from orders.main import app

client = TestClient(app)


def test_read_created_order_returns_200_and_card(client: TestClient, order_payload: dict):
    created_response = client.request(method = "POST", url="/orders", json=order_payload)
    assert created_response.status_code == 201
    created_order = created_response.json()

    response = client.request(method = "GET", url=f"/orders/{created_order['id']}")

    assert response.status_code == 200
    assert response.json() == created_order

def test_read_nonexistent_order_returns_404(client: TestClient):
    response = client.request(method = "GET", url="/orders/999999")

    assert response.status_code == 404
    assert str(999999) in response.json()["detail"]