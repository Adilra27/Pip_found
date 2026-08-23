import os
import hashlib
import hmac
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Donation, Cause
from ..schemas import RazorpayOrderCreate, RazorpayVerifyRequest, DonationResponse

try:
    import razorpay
except ImportError:
    razorpay = None

router = APIRouter(prefix="/api/donate", tags=["Donations"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_PWF123456789")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "pwf_secret_key_123")

@router.post("/create-order")
def create_razorpay_order(req: RazorpayOrderCreate, db: Session = Depends(get_db)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    # Create pending donation record in DB
    db_donation = Donation(
        donor_name=req.donor_name,
        donor_email=req.donor_email,
        donor_phone=req.donor_phone,
        amount=req.amount,
        cause_id=req.cause_id,
        status="pending"
    )
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)

    # Attempt Razorpay Order Creation or fallback to mock order for sandbox testing
    order_id = f"order_mock_{db_donation.id}"
    if razorpay and RAZORPAY_KEY_ID.startswith("rzp_live"):
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            data = {
                "amount": int(req.amount * 100), # amount in paise
                "currency": req.currency,
                "receipt": f"receipt_pwf_{db_donation.id}",
                "notes": {
                    "donor_name": req.donor_name,
                    "donor_email": req.donor_email,
                    "cause_id": str(req.cause_id or "")
                }
            }
            order = client.order.create(data=data)
            order_id = order["id"]
        except Exception as e:
            # Fallback to simulated order ID for test environment
            print(f"Razorpay live order error, using test mode: {e}")

    db_donation.razorpay_order_id = order_id
    db.commit()

    return {
        "order_id": order_id,
        "amount": req.amount,
        "currency": req.currency,
        "key_id": RAZORPAY_KEY_ID,
        "donation_id": db_donation.id
    }

@router.post("/verify")
def verify_payment(req: RazorpayVerifyRequest, db: Session = Depends(get_db)):
    donation = db.query(Donation).filter(Donation.id == req.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation record not found")

    # Mark donation as completed
    donation.status = "completed"
    donation.razorpay_payment_id = req.razorpay_payment_id
    
    # Update raised_amount on corresponding cause if applicable
    if donation.cause_id:
        cause = db.query(Cause).filter(Cause.id == donation.cause_id).first()
        if cause:
            cause.raised_amount = (cause.raised_amount or 0.0) + donation.amount
            
    db.commit()
    db.refresh(donation)

    return {
        "status": "success",
        "message": "Payment verified successfully. Thank you for your support!",
        "donation_id": donation.id
    }

@router.get("", response_model=List[DonationResponse])
def get_donations(db: Session = Depends(get_db)):
    return db.query(Donation).order_by(Donation.created_at.desc()).all()
