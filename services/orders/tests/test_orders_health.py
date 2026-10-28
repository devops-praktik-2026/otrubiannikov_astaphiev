"""Единственный тест, который проходит с самого начала.

Он нужен, чтобы на первом занятии вы увидели зелёную проверку и убедились,
что окружение собрано правильно.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from orders.db import Base
from orders.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "orders"}


def test_startup_creates_orders_table(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr("orders.main.engine", test_engine)

    with TestClient(app):
        assert inspect(test_engine).has_table("orders")

    Base.metadata.drop_all(test_engine)
