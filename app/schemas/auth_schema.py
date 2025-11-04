from pydantic import BaseModel, field_validator
from email_validator import validate_email, EmailNotValidError


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


