from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str  # "customer", "retailer", "wholesaler"
    is_verified: bool = Field(default=False, sa_column_kwargs={"server_default": "0"})
