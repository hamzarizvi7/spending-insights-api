import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spending Insights API")


@app.post("/transactions", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(
    payload: schemas.TransactionCreate, db: Session = Depends(get_db)
):
    txn = models.Transaction(**payload.model_dump())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@app.get("/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(
    category: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    db: Session = Depends(get_db),
):
    query = select(models.Transaction)
    if category:
        query = query.where(models.Transaction.category == category)
    if start_date:
        query = query.where(models.Transaction.date >= start_date)
    if end_date:
        query = query.where(models.Transaction.date <= end_date)
    return db.scalars(query.order_by(models.Transaction.date.desc())).all()