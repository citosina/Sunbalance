# 🌞 SunBalance

SunBalance is a “sun & vitamin D co-pilot” for families. It combines a modular Django backend with a Vue 3 single-page app to surface conservative, friendly recommendations about when to go outside and for how long.

> **Safety reminder:** SunBalance only provides general, conservative guidance. It is not medical advice. Always follow the instructions of your healthcare professionals, especially for children or if you have skin or health conditions.

## Features

- **Onboarding wizard** – Capture home location, skin type, preferred time windows, and family members in a few guided steps.
- **Profile management** – Update the household defaults and tweak profiles for kids or dependents.
- **Today’s plan** – One-tap status card showing current UV, recommended exposure range, trend for the next hours, and safety callouts.
- **Recommendation engine** – Pure Python heuristics that err on the side of caution by factoring skin type, age group, altitude, sunscreen, and clothing coverage.
- **UV service wrapper** – Cached, fault-tolerant integration with external UV APIs. If the provider fails, SunBalance returns a conservative fallback and flags data quality.
- **Modern frontend** – Vue 3 (Composition API) + Pinia + Vite with responsive styling and a reusable component library.
- **Automated tests** – Django unit tests for critical logic plus Vitest coverage for the Sun card UI component.

## Project structure

```text
Sunbalance/
├── accounts/              # Registration + JWT helpers
├── profiles/              # Household preferences and per-person profiles
├── sun_engine/            # Recommendation heuristics + API endpoint
├── uv_api/                # External UV service wrapper with caching
├── api/                   # Aggregated API routing
├── frontend/              # Vite + Vue 3 SPA (mobile-first)
├── sunbalance/            # Django project settings and URLs
├── manage.py
└── requirements.txt
```

## Backend setup (Django + DRF)

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the provided example and adjust values for your environment:

```bash
cp .env.example .env
```

`.env` values that matter:

- `SECRET_KEY` – Django secret key
- `DEBUG` – `True` for local development only
- `ALLOWED_HOSTS` – Comma-separated list of hosts
- `UV_API_KEY` – API key for OpenUV (or another compatible provider)
- `UV_API_BASE_URL` – Endpoint template (defaults to OpenUV’s UV endpoint)
- `ACCESS_TOKEN_MINUTES` / `REFRESH_TOKEN_DAYS` – SimpleJWT lifetimes

### 3. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

The backend exposes JSON endpoints under `http://localhost:8000/api/`.

### 4. Available endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new account |
| `/api/auth/token/` | POST | Obtain JWT access & refresh tokens |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/profiles/user/` | GET/PATCH | Household defaults |
| `/api/profiles/items/` | CRUD | Manage personal profiles |
| `/api/recommendation/today/?profile_id=…` | GET | Current-day sun plan for the selected profile |

Responses include a `disclaimer` field reiterating that the output is not medical advice.

## Frontend setup (Vue 3 + Vite)

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Environment variables

Create `frontend/.env` based on `frontend/.env.example` and point `VITE_API_BASE_URL` to your backend:

```bash
cp frontend/.env.example frontend/.env
```

### 3. Run locally

```bash
npm run dev
```

The SPA is served at `http://localhost:5173`. It expects the Django API at `http://localhost:8000/api` by default.

### 4. Tests

- Backend: `python manage.py test`
- Frontend: `cd frontend && npm run test -- --run`

## Recommendation heuristics (quick overview)

The core logic lives in `sun_engine/recommendations.py` and follows these principles:

1. Estimate time to minimal erythema dose (MED) per skin type and current UV index.
2. Apply multipliers for age group (children and toddlers get smaller windows) and altitude.
3. Adjust effective UV for clothing coverage, hats, sunscreen, and cloud cover.
4. Apply a safety factor so the recommended window remains below the theoretical MED.
5. Clamp results to conservative limits (e.g., maximum 45 minutes for moderate UV, max 10 minutes for extreme UV).
6. Return structured statuses (`good_now`, `caution_now`, `avoid_now`, `low_uv`) plus warnings and suggested time windows.

The heuristics are intentionally simple and well-documented so they can be refined with domain expert input later.

## Tooling & DX

- **Formatting** – Use Black + isort for Python (`pip install black isort`) and leverage Prettier/ESLint if you extend the frontend tooling.
- **Caching** – UV responses are cached for 10 minutes via Django’s local memory cache to avoid hammering external APIs.
- **Signals** – New users automatically get a default `UserProfile` and `SunProfile` so onboarding can just update values.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Ensure backend and frontend tests pass.
4. Submit a pull request with context on the change.

## License

This project is released under the [MIT License](LICENSE).
