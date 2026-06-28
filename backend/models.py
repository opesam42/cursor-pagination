from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime



class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    amount: float
    merchant: str
    status: str
    created_at: datetime = Field(index=True)
