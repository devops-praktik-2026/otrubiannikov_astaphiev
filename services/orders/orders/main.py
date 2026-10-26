"""Точка входа сервиса заказов."""

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Mapped, Session, mapped_column

from orders.config import settings
from orders.db import Base, get_session

app = FastAPI(
    title="Сервис заказов",
    description="Заготовка.",
    version="0.1.0",
)


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int]
    item: Mapped[str]
    quantity: Mapped[int]


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    account_id: int = Field(gt=0)
    item: str = Field(min_length=1)
    quantity: int = Field(ge=1)


@app.get("/health", tags=["Служебное"], summary="Жив ли сервис")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(payload: Order, session: Session = Depends(get_session)) -> OrderModel:
    order = OrderModel(**payload.model_dump())
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, session: Session = Depends(get_session)) -> OrderModel:
    order = session.get(OrderModel, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ {order_id} не найден",
        )
    return order
