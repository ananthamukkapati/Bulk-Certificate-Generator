from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from .database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)

    event_name = Column(String(255), nullable=False)
    event_date = Column(String(50), nullable=False)
    issuer_name = Column(String(255), nullable=False)

    status = Column(
        String(50),
        default="queued",
        nullable=False
    )

    total = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    failed = Column(Integer, default=0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("generation_jobs.id"),
        nullable=False
    )

    recipient_name = Column(
        String(255),
        nullable=False
    )

    recipient_email = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    job = relationship(
        "GenerationJob",
        back_populates="certificates"
    )