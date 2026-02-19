# Student Jobs Marketplace API

A RESTful API built with Django and Django Rest Framework to connect students with on-campus and nearby job opportunities.

## Features

- **Authentication**: Custom User model with Student, Employer, and Admin roles. JWT-based authentication.
- **Profiles**: Separate profiles for Students and Employers.
- **Job Postings**: Employers can create and manage job postings. Students can browse, search, and filter.
- **Applications**: Students can apply for jobs and track status. Employers can manage applications.
- **Search & Filter**: Filter jobs by type, location, and deadline. Search by title, description, or skills.

## Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Student-Jobs-Marketplace-API
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Start the development server**:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

- `POST /api/accounts/register/`: Register a new user.
- `POST /api/accounts/token/`: Obtain JWT tokens.
- `GET /api/jobs/listings/`: List all job postings (supports search and filtering).
- `POST /api/jobs/applications/`: Apply for a job (Students only).
- `GET /api/jobs/applications/`: View applications (Students see their own, Employers see candidates).

## Technical Stack

- **Backend**: Django, Django Rest Framework
- **Database**: SQLite (Development)
- **Auth**: SimpleJWT
- **Filtering**: django-filter
