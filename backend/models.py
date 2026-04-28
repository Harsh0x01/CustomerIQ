from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    tenure = Column(Integer)
    balance = Column(Float)
    num_products = Column(Integer)
    has_credit_card = Column(Integer)
    is_active_member = Column(Integer)
    estimated_salary = Column(Float)
    exited = Column(Integer)   # 0 = stayed, 1 = churned
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "age": self.age,
            "gender": self.gender,
            "tenure": self.tenure,
            "balance": self.balance,
            "num_products": self.num_products,
            "has_credit_card": self.has_credit_card,
            "is_active_member": self.is_active_member,
            "estimated_salary": self.estimated_salary,
            "exited": self.exited,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PredictionHistory(Base):
    """Immutable log of all model inferences for auditing and drift analysis."""
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    model_version = Column(String, index=True)
    inputs = Column(JSON)      # Store the feature vector used
    probability = Column(Float)
    prediction = Column(Integer)
    risk_level = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """System-wide record of high-impact events (Data Uploads, Model Training, Config Changes)."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    action = Column(String, index=True)  # e.g., "TRAIN_MODEL", "UPLOAD_CSV", "DELETE_ALL"
    target = Column(String)             # e.g., "churn_v1.0", "q4_data.csv"
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CustomerTimeline(Base):
    """Time-series snapshots of customer attributes to track behavioral shifts."""
    __tablename__ = "customer_timeline"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    balance = Column(Float)
    is_active_member = Column(Integer)
    num_products = Column(Integer)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now())