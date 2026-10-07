# Bulk Certificate Generator

A REST API that generates participation certificates in bulk from a predefined certificate template. The system accepts multiple recipients in a single request, processes certificates independently, tracks generation progress, and allows completed certificates to be downloaded.

## 🚀 Features

* Bulk certificate generation
* Single predefined certificate template
* REST API built with FastAPI
* SQLite relational database
* SQLAlchemy ORM
* Pydantic request validation
* Background certificate processing
* Individual certificate status tracking
* Job-level progress tracking
* Failure isolation — one failed certificate does not stop the remaining certificates
* PDF certificate generation using ReportLab
* Certificate download API
* Automated API tests using Pytest
* Interactive Swagger API documentation

---

## 🛠️ Technology Stack

| Technology | Purpose                    |
| ---------- | -------------------------- |
| Python     | Backend programming        |
| FastAPI    | REST API framework         |
| SQLite     | Relational database        |
| SQLAlchemy | ORM/database operations    |
| Pydantic   | Request validation         |
| ReportLab  | PDF certificate generation |
| Pytest     | Automated testing          |
| HTTPX      | API testing                |
| Uvicorn    | ASGI server                |

---

## 📁 Project Structure

```text
Bulk-Certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   └── generator.py
│
├── certificates/
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

### Important files

**`main.py`**

Defines the FastAPI application and API endpoints.

**`schemas.py`**

Defines Pydantic models used for request validation and API responses.

**`models.py`**

Defines the database models for generation jobs and certificates.

**`services.py`**

Contains job creation and certificate processing logic.

**`generator.py`**

Creates certificate PDFs using ReportLab.

**`database.py`**

Configures the SQLite database and SQLAlchemy session.

**`test_api.py`**

Contains automated API and certificate-generation tests.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <your-github-repository-url>
```

Navigate into the project:

```bash
cd Bulk-Certificate-generator
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

| Method | Endpoint                         | Description                            |
| ------ | -------------------------------- | -------------------------------------- |
| GET    | `/`                              | API information                        |
| GET    | `/health`                        | Health check                           |
| POST   | `/jobs`                          | Create bulk certificate generation job |
| GET    | `/jobs/{job_id}`                 | Check job status and progress          |
| GET    | `/certificates/{certificate_id}` | Download generated certificate         |

---

# 📤 Creating a Generation Job

Send a `POST` request to:

```text
/jobs
```

Example request:

```json
{
    "event_name": "Python Workshop 2026",
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
        },
        {
            "name": "Priya",
            "email": "priya@example.com"
        }
    ]
}
```

The API creates one generation job containing all recipients.

Example response:

```json
{
    "id": 1,
    "event_name": "Python Workshop 2026",
    "event_date": "2026-10-07",
    "issuer_name": "ABC Institute",
    "status": "queued",
    "total": 3,
    "completed": 0,
    "failed": 0
}
```

The certificate generation process then runs in the background.

---

# 📊 Checking Job Progress

Send:

```text
GET /jobs/{job_id}
```

Example:

```text
GET /jobs/1
```

Example response:

```json
{
    "job_id": 1,
    "event_name": "Python Workshop 2026",
    "event_date": "2026-10-07",
    "issuer_name": "ABC Institute",
    "status": "completed",
    "total": 3,
    "completed": 3,
    "failed": 0,
    "processing": 0,
    "pending": 0,
    "progress": 100.0,
    "certificates": [
        {
            "id": 1,
            "recipient_name": "Anantha",
            "recipient_email": "anantha@example.com",
            "status": "completed",
            "file_path": "certificates/certificate_1.pdf",
            "error_message": null
        }
    ]
}
```

---

# 📥 Downloading a Certificate

After a certificate has been successfully generated, use:

```text
GET /certificates/{certificate_id}
```

Example:

```text
GET /certificates/1
```

The API returns the generated PDF file.

Certificates are stored inside:

```text
certificates/
```

---

# ❌ Failure Handling

Each recipient is processed independently.

For example, if a job contains three recipients:

```text
Recipient 1 → Success
Recipient 2 → Failure
Recipient 3 → Success
```

The result is:

```text
Total       = 3
Completed   = 2
Failed      = 1
Progress    = 100%
Status      = completed_with_errors
```

The failure of one recipient does not stop the remaining certificates from being generated.

The failed certificate stores an error message in the database.

---

# 🔄 System Architecture

```text
                 Client
                   │
                   │ POST /jobs
                   ▼
             ┌──────────────┐
             │   FastAPI    │
             └──────┬───────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Validate Request  │
          │    Pydantic       │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Create Generation │
          │       Job         │
          └─────────┬─────────┘
                    │
                    ▼
            Background Task
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       User 1    User 2    User 3
          │         │         │
          ▼         ▼         ▼
        PDF       PDF       PDF
          │         │         │
          └─────────┼─────────┘
                    ▼
              SQLite Database
                    │
                    ▼
            GET /jobs/{id}
                    │
                    ▼
          Progress + Results
                    │
                    ▼
        GET /certificates/{id}
                    │
                    ▼
             Download PDF
```

---

# 🗄️ Database Design

The application uses two primary tables.

## GenerationJob

Stores information about a bulk generation
