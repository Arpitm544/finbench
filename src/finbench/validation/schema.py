from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    PAYMENT = "PAYMENT"
    TRANSFER = "TRANSFER"
    CASH_OUT = "CASH_OUT"
    CASH_IN = "CASH_IN"
    DEBIT = "DEBIT"


class TransactionSchema(BaseModel):
    step: int = Field(..., ge=1, le=744, description="Simulation step 1 to 744 (hours)")
    type: TransactionType
    amount: float = Field(..., ge=0.0, description="Transaction amount")
    nameOrig: str = Field(..., min_length=3, max_length=64)
    oldbalanceOrg: float = Field(..., ge=0.0)
    newbalanceOrig: float = Field(..., ge=0.0)
    nameDest: str = Field(..., min_length=3, max_length=64)
    oldbalanceDest: float = Field(..., ge=0.0)
    newbalanceDest: float = Field(..., ge=0.0)
    isFraud: int = Field(..., ge=0, le=1)
    isFlaggedFraud: Optional[int] = Field(0, ge=0, le=1)

    @field_validator("type", mode="before")
    def validate_type(cls, v):
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper in TransactionType.__members__:
                return TransactionType(v_upper)
        raise ValueError(f"Invalid transaction type: {v}")
