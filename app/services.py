from sqlalchemy.orm import Session

from .models import GenerationJob, Certificate
from .schemas import GenerationJobCreate
from .generator import generate_certificate


def create_generation_job(
    db: Session,
    request: GenerationJobCreate
):
    job = GenerationJob(
        event_name=request.event_name,
        event_date=request.event_date,
        issuer_name=request.issuer_name,
        status="queued",
        total=len(request.recipients),
        completed=0,
        failed=0
    )

    db.add(job)
    db.flush()

    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="pending"
        )

        db.add(certificate)

    db.commit()
    db.refresh(job)

    return job


def process_generation_job(
    job_id: int
):
    """
    Process all certificates belonging to a job.

    Each certificate is processed independently so
    one failure does not stop the remaining certificates.
    """

    from .database import SessionLocal

    db: Session = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if not job:
            return

        job.status = "processing"
        db.commit()

        certificates = db.query(Certificate).filter(
            Certificate.job_id == job_id
        ).all()

        for certificate in certificates:

            try:
                certificate.status = "processing"
                db.commit()

                file_path = generate_certificate(
                    certificate_id=certificate.id,
                    recipient_name=certificate.recipient_name,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    issuer_name=job.issuer_name
                )

                certificate.status = "completed"
                certificate.file_path = file_path
                certificate.error_message = None

                job.completed += 1

                db.commit()

            except Exception as error:

                certificate.status = "failed"
                certificate.error_message = str(error)

                job.failed += 1

                db.commit()

        if job.failed == 0:
            job.status = "completed"
        elif job.completed == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"

        db.commit()

    finally:
        db.close()