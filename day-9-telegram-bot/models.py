from pydantic import BaseModel
from datetime import date


class ExpenseBase(BaseModel):
    description: str
    amount: float
    category: str
    date: date


class Expense(ExpenseBase):
    id: int