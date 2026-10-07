import os

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# =========================================================
# Test 1: Root Endpoint
# =========================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"

test_root()
# =========================================================
# Test 2: Create Generation Job
# =========================================================

def test_create_generation_job():

    payload = {
        "event_name": "Python Bootcamp",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Anantha",
                "email": "anantha@example.com"
            },
            {
                "name": "Rahul",
                "email": "rahul@example.com"
            }
        ]
    }

    response = client.post(
        "/jobs",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_name"] == "Python Bootcamp"
    assert data["total"] == 2
    assert data["completed"] == 0
    assert data["failed"] == 0

    assert "id" in data

test_create_generation_job()
# =========================================================
# Test 3: Invalid Email Validation
# =========================================================

def test_invalid_email():

    payload = {
        "event_name": "Python Bootcamp",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Anantha",
                "email": "invalid-email"
            }
        ]
    }

    response = client.post(
        "/jobs",
        json=payload
    )

    assert response.status_code == 422

test_invalid_email()
# =========================================================
# Test 4: Empty Recipients Validation
# =========================================================

def test_empty_recipients():

    payload = {
        "event_name": "Python Bootcamp",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": []
    }

    response = client.post(
        "/jobs",
        json=payload
    )

    assert response.status_code == 422

test_empty_recipients()

# =========================================================
# Test 5: Job Status
# =========================================================

def test_job_status():

    payload = {
        "event_name": "Data Science Workshop",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Test User",
                "email": "test@example.com"
            }
        ]
    }

    create_response = client.post(
        "/jobs",
        json=payload
    )

    assert create_response.status_code == 200

    job_id = create_response.json()["id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1

    assert "progress" in data
    assert "certificates" in data
test_job_status()

# =========================================================
# Test 6: Non-existent Job
# =========================================================

def test_nonexistent_job():

    response = client.get(
        "/jobs/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Generation job not found"
test_nonexistent_job()

# =========================================================
# Test 7: Certificate Generation
# =========================================================

def test_certificate_generation():

    payload = {
        "event_name": "Certificate Test",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Certificate User",
                "email": "certificate@example.com"
            }
        ]
    }

    response = client.post(
        "/jobs",
        json=payload
    )

    assert response.status_code == 200

    job_id = response.json()["id"]

    # BackgroundTasks run when TestClient processes the request,
    # so the job should normally be completed here.

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["total"] == 1

    certificate = data["certificates"][0]

    assert certificate["status"] == "completed"

    assert certificate["file_path"] is not None

    assert os.path.exists(
        certificate["file_path"]
    )
test_certificate_generation()

# =========================================================
# Test 8: Retrieve Certificate
# =========================================================

def test_retrieve_certificate():

    payload = {
        "event_name": "Download Test",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Download User",
                "email": "download@example.com"
            }
        ]
    }

    response = client.post(
        "/jobs",
        json=payload
    )

    assert response.status_code == 200

    job_id = response.json()["id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    data = status_response.json()

    certificate_id = data["certificates"][0]["id"]

    download_response = client.get(
        f"/certificates/{certificate_id}"
    )

    assert download_response.status_code == 200

    assert (
        download_response.headers["content-type"]
        == "application/pdf"
    )

test_retrieve_certificate()
# =========================================================
# Test 9: Non-existent Certificate
# =========================================================

def test_nonexistent_certificate():

    response = client.get(
        "/certificates/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Certificate not found"
    test_nonexistent_certificate()

# =========================================================
# Test 10: Individual Certificate Failure
# =========================================================

def test_individual_certificate_failure():

    payload = {
        "event_name": "Failure Test",
        "event_date": "2026-10-07",
        "issuer_name": "ABC Institute",

        "recipients": [
            {
                "name": "Successful User One",
                "email": "success1@example.com"
            },
            {
                "name": "Failed User",
                "email": "failure@example.com"
            },
            {
                "name": "Successful User Two",
                "email": "success2@example.com"
            }
        ]
    }

    # Make certificate generation fail only for
    # the second certificate.
    original_generate = __import__(
        "app.services",
        fromlist=["generate_certificate"]
    ).generate_certificate

    call_count = 0

    def generate_with_one_failure(*args, **kwargs):

        nonlocal call_count

        call_count += 1

        if call_count == 2:
            raise Exception(
                "Simulated certificate generation failure"
            )

        return original_generate(
            *args,
            **kwargs
        )

    with patch(
        "app.services.generate_certificate",
        side_effect=generate_with_one_failure
    ):

        response = client.post(
            "/jobs",
            json=payload
        )

    assert response.status_code == 200

    job_id = response.json()["id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    # Three certificates requested
    assert data["total"] == 3

    # Two successfully generated
    assert data["completed"] == 2

    # One failed
    assert data["failed"] == 1

    # All three were processed
    assert data["progress"] == 100.0

    # Job has partial failures
    assert data["status"] == "completed_with_errors"

    certificates = data["certificates"]

    statuses = [
        certificate["status"]
        for certificate in certificates
    ]

    assert statuses.count("completed") == 2
    assert statuses.count("failed") == 1

    failed_certificate = next(
        certificate
        for certificate in certificates
        if certificate["status"] == "failed"
    )

    assert failed_certificate["error_message"] is not None