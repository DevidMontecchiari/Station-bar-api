"""Read this third: business decisions still belong to the application."""
from fastapi import HTTPException
from sqlmodel import Session, select
from models import BarOrder, MenuItem, OrderInput, OrderLine, OrderOutput


def read_order(session: Session, order_id: int) -> OrderOutput:
    order = session.get(BarOrder, order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    lines = session.exec(select(OrderLine).where(OrderLine.order_id == order_id).order_by(OrderLine.id)).all()
    # Reconstruct nested JSON from related rows; table names do not define the API.
    return OrderOutput(id=order.id, table=order.table_number, status=order.status,
                       items=[{"menu_item_id": line.menu_item_id, "quantity": line.quantity} for line in lines])


def create_order(session: Session, payload: OrderInput) -> OrderOutput:
    # Validate the whole order before storing any part of it.
    for line in payload.items:
        item = session.get(MenuItem, line.menu_item_id)
        if item is None:
            raise HTTPException(404, "Menu item not found")
        if not item.available:
            raise HTTPException(409, "Menu item is unavailable")
    try:
        order = BarOrder(table_number=payload.table)
        session.add(order)
        session.flush()  # INSERT now to obtain the generated ID; not a commit.
        for line in payload.items:
            session.add(OrderLine(order_id=order.id, **line.model_dump()))
        session.flush()
        result = read_order(session, order.id)
        session.commit()  # Order and ALL lines become durable together.
        return result
    except Exception:
        session.rollback()  # Never leave a partially written order.
        raise


def delete_order(session: Session, order_id: int):
    order = session.get(BarOrder, order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    try:
        for line in session.exec(select(OrderLine).where(OrderLine.order_id == order_id)).all():
            session.delete(line)
        session.flush()  # Remove child rows before their referenced parent.
        session.delete(order)
        session.commit()
    except Exception:
        session.rollback()
        raise
