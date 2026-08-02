from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.auth import get_current_user
import pandas as pd
import io

router = APIRouter()

@router.post("/")
@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    
    # Check if uploaded file is actually a CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Read the file content into pandas
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))

    # Check required columns exist
    required_columns = [
        "customer_id", "age", "gender", "tenure", "balance",
        "num_products", "has_credit_card", "is_active_member",
        "estimated_salary", "exited"
    ]
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing column: {col}"
            )

    # Save each row to the database
    saved = 0
    skipped = 0
    seen_ids = set()
    for _, row in df.iterrows():
        customer_id = str(row["customer_id"])
        # Skip if customer already exists or is a duplicate within this file
        if customer_id in seen_ids:
            skipped += 1
            continue
        existing = db.query(models.Customer).filter(
            models.Customer.customer_id == customer_id
        ).first()
        
        if existing:
            skipped += 1
            continue

        customer = models.Customer(
            customer_id=customer_id,
            age=int(row["age"]),
            gender=str(row["gender"]),
            tenure=int(row["tenure"]),
            balance=float(row["balance"]),
            num_products=int(row["num_products"]),
            has_credit_card=int(row["has_credit_card"]),
            is_active_member=int(row["is_active_member"]),
            estimated_salary=float(row["estimated_salary"]),
            exited=int(row["exited"])
        )
        db.add(customer)
        seen_ids.add(customer_id)
        saved += 1

    db.commit()

    return {
        "message": "Upload complete",
        "saved": saved,
        "skipped": skipped,
        "total_rows": len(df)
    }