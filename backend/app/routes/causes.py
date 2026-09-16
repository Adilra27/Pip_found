from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Cause
from ..schemas import CauseResponse

router = APIRouter(prefix="/api/causes", tags=["Causes"])

@router.get("", response_model=List[CauseResponse])
def get_all_causes(db: Session = Depends(get_db)):
    return db.query(Cause).all()

@router.get("/{cause_id}", response_model=CauseResponse)
def get_cause_by_id(cause_id: int, db: Session = Depends(get_db)):
    cause = db.query(Cause).filter(Cause.id == cause_id).first()
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    return cause
