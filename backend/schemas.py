from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class ChurnPredictionInput(BaseModel):
    """
    Schema for a single churn prediction.
    Enforces strict typing and domain-level validation.
    """
    customer_id: Optional[str] = Field(
        None,
        max_length=128,
        description="Optional customer identifier used for the audit trail",
    )
    age: int = Field(..., ge=18, le=100, description="Customer age")
    gender: str = Field(..., pattern="^(Male|Female|Other)$", description="Customer gender")
    tenure: int = Field(..., ge=0, le=50, description="Years with the bank")
    balance: float = Field(..., ge=0.0, description="Current account balance")
    num_products: int = Field(..., ge=1, le=5, description="Number of bank products")
    has_credit_card: int = Field(..., ge=0, le=1, description="Binary credit card status")
    is_active_member: int = Field(..., ge=0, le=1, description="Binary activity status")
    estimated_salary: float = Field(..., ge=0.0, description="Annual salary")
    
    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        return v.capitalize()

class BatchPredictionInput(BaseModel):
    """Schema for processing multiple predictions at once."""
    customers: List[ChurnPredictionInput]

class PredictionResponse(BaseModel):
    """Standardized response for churn predictions."""
    customer_id: str
    churn_probability: float
    churn_prediction: int
    risk_level: str

class TrainingMetrics(BaseModel):
    """Metrics returned after a model training run."""
    accuracy: float
    roc_auc: float
    train_size: int
    test_size: int
    run_id: Optional[str]


class IntelligenceQuery(BaseModel):
    """Natural-language query for the intelligence module."""
    query: str = Field(..., min_length=1, max_length=1000, description="Free-text analysis question")
