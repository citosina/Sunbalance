# 🌞 SunBalance

[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.x-FF1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

SunBalance is a Django REST API that helps people manage healthy sun exposure. The service
combines location awareness, real-time UV index lookups (via the OpenUV platform), and simple
analytics so that users can make informed decisions about spending time outdoors while tracking
their vitamin D production.

> **Why SunBalance?** Excessive sun exposure is risky, yet sunlight is the primary natural source of
> vitamin D. SunBalance gives users a data-driven, privacy-conscious way to balance those
> considerations.

---

## Table of Contents

1. [Key Features](#key-features)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Environment Configuration](#environment-configuration)
   - [Database Migrations](#database-migrations)
   - [Run the API](#run-the-api)
5. [API Overview](#api-overview)
   - [Authentication](#authentication)
   - [Sun Exposure Endpoints](#sun-exposure-endpoints)
   - [UV Index Endpoints](#uv-index-endpoints)
6. [Data Model](#data-model)
7. [Testing](#testing)
8. [Development Tips](#development-tips)
9. [Contributing](#contributing)
10. [License](#license)

---

## Key Features

- **JWT-secured REST API** – JSON Web Tokens provided by SimpleJWT secure every request after login.
- **Sun exposure tracking** – Persist daily exposure logs, including UV index and estimated vitamin D.
- **Smart UV lookups** – Fetch UV data for explicit GPS coordinates or fall back to coarse IP-based
  geolocation using `geocoder` and the OpenUV API.
- **Future-ready frontend** – Designed to back both web and native clients via clean, documented
  endpoints.
- **CORS enabled** – Ready to be consumed by JavaScript single-page applications out of the box.

## System Architecture

```text
┌────────────┐      ┌────────────────┐      ┌─────────────┐
│  Frontend  │ ---> │  SunBalance    │ ---> │  OpenUV API │
│ (React,    │ REST │  Django + DRF  │ HTTP │  (external) │
│  React Nat.)│     │  JWT security  │      │             │
└────────────┘      └────────────────┘      └─────────────┘
```

- **Django 4.2** powers the core application, including authentication and ORM.
- **Django REST Framework** exposes the JSON API.
- **SimpleJWT** issues access and refresh tokens with configurable lifetimes.
- **SQLite** is the default development database (swap to PostgreSQL or another RDBMS for production).

## Project Structure

```text
Sunbalance/
├── api/                 # Django app that exposes REST endpoints
│   ├── models.py        # Sun exposure domain models
│   ├── serializers.py   # API serializers for DRF
│   ├── urls.py          # Endpoint routing
│   └── views.py         # Business logic + integrations
├── sunbalance/          # Project configuration (settings, URLs, WSGI/ASGI)
├── manage.py            # Django utility entry point
├── requirements.txt     # (Create this from your virtualenv if missing)
└── README.md
```

> **Note:** The repository currently ships with a local SQLite database (`db.sqlite3`) for convenience.
> Remove it before committing to production environments.

## Getting Started

### Prerequisites

- Python **3.10+**
- pip and `virtualenv`
- An [OpenUV API key](https://www.openuv.io/)

### Installation

```bash
# Clone the repository
git clone https://github.com/citosina/SunBalance.git
cd SunBalance

# (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# .\venv\Scripts\activate     # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

If `requirements.txt` is not yet generated, create one from the active environment with
`pip freeze > requirements.txt` once dependencies are installed.

### Environment Configuration

Create a `.env` file (or define environment variables) with the following settings:

```dotenv
DJANGO_SECRET_KEY=your-django-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
OPENUV_API_KEY=your-openuv-token
```

Update `sunbalance/settings.py` to consume these variables, or export them before running the
server. Never check real secrets into version control.

### Database Migrations

```bash
python manage.py migrate
```

You can create an administrative superuser if you plan to use the Django admin:

```bash
python manage.py createsuperuser
```

### Run the API

```bash
python manage.py runserver
```

The development server starts at <http://127.0.0.1:8000/>. API endpoints live under
`http://127.0.0.1:8000/api/`.

## API Overview

All endpoints return JSON. Unless noted otherwise, they require a valid JWT access token in the
`Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint        | Description                 |
|--------|-----------------|-----------------------------|
| POST   | `/api/register/` | Create a new user account.  |
| POST   | `/api/login/`    | Obtain JWT access & refresh tokens. |

**Example login request**

```http
POST /api/login/
Content-Type: application/json

{
  "username": "demo",
  "password": "correct-horse-battery-staple"
}
```

**Successful response**

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### Sun Exposure Endpoints

| Method | Endpoint              | Description                                         |
|--------|----------------------|-----------------------------------------------------|
| GET    | `/api/sun_exposure/` | List the authenticated user's sun exposure entries. |
| POST   | `/api/sun_exposure/` | Create a new exposure entry (auto-attached to user). |

**POST payload**

```json
{
  "duration_minutes": 35,
  "uv_index": 5.2,
  "vitamin_d_produced": 800
}
```

### UV Index Endpoints

| Method | Endpoint                                   | Description |
|--------|--------------------------------------------|-------------|
| GET    | `/api/uv_index/<lat>/<lon>/`               | Fetch UV data for explicit coordinates. |
| GET    | `/api/smart_location_uv_index/?lat=&lon=`  | Use provided GPS coords or fall back to IP geolocation. |

> The smart endpoint defaults to IP-based lookup (via `geocoder.ip("me")`) if latitude and longitude
> are omitted. Make sure outbound HTTP requests are permitted in your environment.

## Data Model

`SunExposure` records are associated with Django `User` accounts.

| Field              | Type        | Notes                               |
|--------------------|-------------|-------------------------------------|
| `user`             | FK → User   | Automatically set to the requester. |
| `date`             | Date        | Defaults to creation date.          |
| `duration_minutes` | Integer     | Sun exposure duration.              |
| `uv_index`         | Float       | UV index recorded for the session.  |
| `vitamin_d_produced` | Float     | Estimated vitamin D production (IU).|

## Testing

Run the Django test suite:

```bash
python manage.py test
```

Add unit tests under `api/tests.py` to cover endpoints, authentication, and integrations.

## Development Tips

- Enable logging for external API calls when debugging OpenUV responses.
- Replace the placeholder OpenUV token in `api/views.py` with the `OPENUV_API_KEY` environment
  variable before deploying.
- Configure [Django CORS Headers](https://pypi.org/project/django-cors-headers/) with explicit
  origins in production environments instead of `CORS_ALLOW_ALL_ORIGINS = True`.
- Switch `DEBUG` to `False`, define `ALLOWED_HOSTS`, and move secrets to a secure store before
  shipping to production.

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Add or update tests when applicable.
4. Submit a pull request describing your changes.

## License

This project is licensed under the [MIT License](LICENSE).
