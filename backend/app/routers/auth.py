from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_session
from app.models.user import User
from app.models.otp import OTP
from app.schemas.user import UserCreate, UserRead
from app.schemas.otp import OTPRequest, OTPVerify, LoginWithOTP
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.email import send_otp_email
from app.config import settings

router = APIRouter(tags=["Authentication"])

# 🧩 Helper function to create and send OTP
async def create_and_send_otp(email: str, session: Session, username: str = None, is_registration: bool = False):
    # Invalidate any existing OTPs for this email
    session.exec(
        OTP.__table__.delete()
        .where(OTP.email == email)
    )
    
    # Generate new OTP
    otp = OTP.generate_otp()
    
    # Save OTP to database
    otp_record = OTP(
        email=email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    )
    session.add(otp_record)
    session.commit()
    
    # Send OTP via email
    await send_otp_email(email, otp, username)
    
    return {"message": "OTP sent successfully"}

# 🧩 Register a new user
@router.post("/register/request-otp", status_code=status.HTTP_200_OK)
async def request_registration_otp(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    # Create and send OTP
    await create_and_send_otp(user_data.email, session, user_data.name, is_registration=True)
    
    return {"message": "OTP sent to your email. Please verify to complete registration."}

class RegisterWithOTP(OTPVerify):
    name: str
    email: str
    password: str
    role: str

@router.post("/register/verify-otp", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def verify_and_register(
    data: RegisterWithOTP,
    session: Session = Depends(get_session)
):
    # Verify OTP
    otp_record = session.exec(
        select(OTP)
        .where(OTP.email == data.email)
        .where(OTP.otp == data.otp)
        .where(OTP.is_used == False)
        .where(OTP.expires_at > datetime.utcnow())
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_record.is_used = True
    session.add(otp_record)
    
    # Create new user
    hashed_pw = hash_password(data.password)
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_pw,
        role=data.role,
        is_verified=True
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@router.post("/register", response_model=UserRead, deprecated=True)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    # Hash the password
    hashed_pw = hash_password(user.password)

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

# 🧩 Login to get JWT token
@router.post("/login/request-otp", status_code=status.HTTP_200_OK)
async def request_login_otp(
    otp_request: OTPRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Check if user exists
    user = session.exec(select(User).where(User.email == otp_request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create and send OTP
    await create_and_send_otp(otp_request.email, session, user.name)
    
    return {"message": "OTP sent to your email. Please verify to login."}

@router.post("/login/verify-otp")
async def verify_otp_and_login(
    login_data: LoginWithOTP,
    session: Session = Depends(get_session)
):
    # Verify user credentials
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify OTP
    otp_record = session.exec(
        select(OTP)
        .where(OTP.email == login_data.email)
        .where(OTP.otp == login_data.otp)
        .where(OTP.is_used == False)
        .where(OTP.expires_at > datetime.utcnow())
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_record.is_used = True
    session.add(otp_record)
    session.commit()
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }

@router.post("/login", deprecated=True)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    # This is the old login endpoint kept for backward compatibility
    # It will be removed in future versions
    return await verify_otp_and_login(
        LoginWithOTP(
            email=form_data.username,
            password=form_data.password,
            otp=""  # Empty OTP for backward compatibility
        ),
        session
    )
