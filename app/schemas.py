from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List


# ==========================================
# 1. Recipient Schema
# ==========================================

class RecipientCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    email: EmailStr


# ==========================================
# 2. Generation Job Create Schema
# ==========================================

class GenerationJobCreate(BaseModel):

    event_name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    event_date: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    issuer_name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    recipients: List[RecipientCreate] = Field(
        ...,
        min_length=1
    )


# ==========================================
# 3. Basic Job Response
# ==========================================

class JobResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    event_name: str
    event_date: str
    issuer_name: str

    status: str

    total: int
    completed: int
    failed: int


# ==========================================
# 4. Certificate Status Response
# ==========================================

class CertificateStatusResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    recipient_name: str
    recipient_email: str

    status: str

    file_path: str | None = None
    error_message: str | None = None


# ==========================================
# 5. Job Status / Progress Response
# ==========================================

class JobStatusResponse(BaseModel):

    job_id: int

    event_name: str
    event_date: str
    issuer_name: str

    status: str

    total: int
    completed: int
    failed: int
    processing: int
    pending: int

    progress: float

    certificates: List[CertificateStatusResponse]