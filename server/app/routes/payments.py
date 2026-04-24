 # /payments endpoints
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.payment import Payment, PaymentProvider, PaymentStatus
from ..models.enrollment import Enrollment
from ..models.course import Course
from ..models.lesson import Lesson
from ..models.progress import Progress
from ..models.user import User
from ..schemas.payment import PaymentInitiate, PaymentResponse, PaymentStatusResponse
from ..services.payment_service import (
    initiate_chapa_payment, verify_chapa_payment, initiate_stripe_payment
)
from ..utils.dependencies import get_current_user
from ..config import settings
import stripe

router = APIRouter(prefix="/payments", tags=["Payments"])

def create_enrollment_with_progress(db: Session, user_id: int, course_id: int):
    """
    Helper function: Creates enrollment and progress records after payment.
    Called by both Chapa and Stripe webhooks.
    """
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first()

    if existing:
        # Update payment status if enrollment exists
        existing.payment_completed = True
        db.commit()
        return existing

    # Create new enrollment
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        payment_completed=True
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    # Create progress records for all lessons
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
    for lesson in lessons:
        progress = Progress(
            enrollment_id=enrollment.id,
            lesson_id=lesson.id,
            completed=False
        )
        db.add(progress)
    db.commit()
    return enrollment

@router.post("/initiate", response_model=PaymentResponse)
def initiate_payment(
    data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start payment process for a course.
    Automatically detects user's country and routes to:
    - Chapa if country is Ethiopia
    - Stripe for all other countries
    Returns a checkout_url for the frontend to redirect the user.
    """
    # Get course
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already enrolled and paid
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == data.course_id,
        Enrollment.payment_completed == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

    # Determine payment provider based on country
    is_ethiopian = current_user.country and current_user.country.lower() in ["ethiopia", "et"]
    provider = PaymentProvider.CHAPA if is_ethiopian else PaymentProvider.STRIPE

    # Create payment record
    tx_ref = f"tx-{current_user.id}-{course.id}-{uuid.uuid4().hex[:8]}"
    payment = Payment(
        user_id=current_user.id,
        course_id=data.course_id,
        amount=course.price,
        provider=provider,
        status=PaymentStatus.PENDING,
        transaction_id=tx_ref
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Route to correct payment provider
    if provider == PaymentProvider.CHAPA:
        result = initiate_chapa_payment(
            amount=course.price,
            email=current_user.email,
            first_name=current_user.full_name,
            tx_ref=tx_ref,
            course_title=course.title,
            callback_url=f"{settings.FRONTEND_URL}/payment/chapa/callback"
        )
        print(f"Chapa response: {result}")  # Debug
        if result.get("status") != "success":
            raise HTTPException(status_code=400, detail=f"Chapa error: {result.get('message', result)}")
        checkout_url = result["data"]["checkout_url"]
    else:
        result = initiate_stripe_payment(
            amount=course.price,
            course_title=course.title,
            course_id=course.id,
            user_id=current_user.id
        )
        checkout_url = result["checkout_url"]
        # Update transaction_id with Stripe session ID
        payment.transaction_id = result["session_id"]
        db.commit()

    return PaymentResponse(
        payment_id=payment.id,
        course_id=course.id,
        amount=course.price,
        provider=provider.value,
        status=payment.status.value,
        checkout_url=checkout_url,
        transaction_id=payment.transaction_id,
        created_at=payment.created_at
    )

@router.get("/chapa/verify/{tx_ref}")
def verify_chapa(
    tx_ref: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify Chapa payment after user returns from payment page.
    Frontend calls this after user completes payment on Chapa.
    """
    payment = db.query(Payment).filter(
        Payment.transaction_id == tx_ref
    ).first()

    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    if payment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to verify this payment")

    result = verify_chapa_payment(tx_ref)

    if result.get("status") == "success" and result["data"]["status"] == "success":
        payment.status = PaymentStatus.COMPLETED
        db.commit()
        # Create enrollment
        create_enrollment_with_progress(db, payment.user_id, payment.course_id)
        return {"status": "success", "message": "Payment verified and enrollment created"}

    return {"status": "failed", "message": "Payment verification failed"}

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe webhook endpoint.
    Stripe calls this automatically when payment is completed.
    Verifies the webhook signature for security.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Handle successful payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        course_id = int(session["metadata"]["course_id"])
        user_id = int(session["metadata"]["user_id"])

        # Update payment status
        payment = db.query(Payment).filter(
            Payment.transaction_id == session["id"]
        ).first()
        if payment:
            payment.status = PaymentStatus.COMPLETED
            db.commit()

        # Create enrollment
        create_enrollment_with_progress(db, user_id, course_id)

    return {"status": "ok"}

@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a payment.
    Frontend uses this to show payment confirmation or failure message.
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status.value,
        provider=payment.provider.value,
        amount=payment.amount,
        transaction_id=payment.transaction_id
    )

@router.get("/history")
def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's payment history.
    Frontend uses this for the Subscription/Billing page.
    Shows all past payments with date, amount, provider, status.
    """
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "course_id": p.course_id,
            "amount": p.amount,
            "provider": p.provider.value,
            "status": p.status.value,
            "transaction_id": p.transaction_id,
            "created_at": p.created_at
        }
        for p in payments
    ]
