from datetime import datetime, timedelta
from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
import secrets

class OTP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    otp: str
    expires_at: datetime = Field(
        sa_column=Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=15))
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_used: bool = False

    @classmethod
    def generate_otp(cls, length: int = 6) -> str:
        """Generate a random numeric OTP of given length"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    def is_expired(self) -> bool:
        """Check if the OTP has expired"""
        return datetime.utcnow() > self.expires_at
