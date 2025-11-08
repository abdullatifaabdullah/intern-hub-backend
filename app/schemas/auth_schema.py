from pydantic import BaseModel, field_validator
from email_validator import validate_email, EmailNotValidError
from app.models.user import UserRole


class SignInRequest(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email_allow_local(cls, v: str) -> str:
        """Validate email, allowing local/test domains like .local"""
        try:
            # Try standard validation first
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError:
            # If standard validation fails, allow local/test domains
            # Basic format check: something@something
            if '@' in v and len(v.split('@')) == 2:
                local, domain = v.split('@')
                if local and domain:
                    return v
            raise ValueError("Invalid email format")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class SignOutRequest(BaseModel):
    refresh_token: str | None = None


class SignUpRequest(BaseModel):
    email: str
    password: str
    role: str = UserRole.STUDENT  # Default to student

    @field_validator('email')
    @classmethod
    def validate_email_allow_local(cls, v: str) -> str:
        """Validate email, allowing local/test domains like .local"""
        try:
            # Try standard validation first
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError:
            # If standard validation fails, allow local/test domains
            # Basic format check: something@something
            if '@' in v and len(v.split('@')) == 2:
                local, domain = v.split('@')
                if local and domain:
                    return v
            raise ValueError("Invalid email format")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is either admin or student"""
        if v not in [UserRole.ADMIN, UserRole.STUDENT]:
            raise ValueError("Role must be either 'admin' or 'student'")
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets minimum requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


