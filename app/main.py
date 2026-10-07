from fastapi import (
    FastAPI,
    Depends,
    BackgroundTasks,
    HTTPException
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models

from .schemas import (
    GenerationJobCreate,
    JobResponse,
    JobStatusResponse
)

from .services import (
    create_generation_job,
    process_generation_job
)

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/jobs", response_model=JobResponse)
def create_job(
    request: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job = create_generation_job(
        db=db,
        request=request
    )

    background_tasks.add_task(
        process_generation_job,
        job.id
    )

    return job

@app.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse
)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(models.GenerationJob).filter(
        models.GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found"
        )

    certificates = db.query(
        models.Certificate
    ).filter(
        models.Certificate.job_id == job_id
    ).all()

    processing = sum(
        1 for certificate in certificates
        if certificate.status == "processing"
    )

    pending = sum(
        1 for certificate in certificates
        if certificate.status == "pending"
    )

    if job.total > 0:
        progress = (
            (job.completed + job.failed)
            / job.total
        ) * 100
    else:
        progress = 0

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "event_date": job.event_date,
        "issuer_name": job.issuer_name,

        "status": job.status,

        "total": job.total,
        "completed": job.completed,
        "failed": job.failed,

        "processing": processing,
        "pending": pending,

        "progress": round(progress, 2),

        "certificates": certificates
    }

@app.get("/certificates/{certificate_id}")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.query(
        models.Certificate
    ).filter(
        models.Certificate.id == certificate_id
    ).first()

    # Certificate does not exist
    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    # Certificate generation failed
    if certificate.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Certificate is not available yet"
        )

    # File path is missing
    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    # Return PDF file
    return FileResponse(
        path=certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )