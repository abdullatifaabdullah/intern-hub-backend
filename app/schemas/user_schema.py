from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int


