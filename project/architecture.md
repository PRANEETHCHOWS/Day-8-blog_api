# Blog REST API Architecture

## 1) Overview

This project is a production-ready Blog REST API built with:

- FastAPI (HTTP API framework)
- SQLAlchemy ORM (data access layer)
- PostgreSQL (primary production database)
- Pydantic (request/response validation)
- JWT (stateless authentication)
- Pytest (automated tests)

The service exposes authenticated CRUD operations for blog posts and a public health endpoint.

---

## 2) High-Level Architecture

```text
Client (Web/Mobile/Postman/Swagger)
        |
        v
FastAPI App (main.py)
  - Routing
  - Dependency injection
  - OpenAPI/Swagger
        |
        +--> Auth layer (auth/auth.py + dependencies.py)
        |      - JWT issue
        |      - JWT verify
        |
        +--> Post router (routers/post.py)
               - Input validation via schemas
               - Business logic + DB actions
                      |
                      v
              SQLAlchemy Session (database.py)
                      |
                      v
                PostgreSQL (prod)
                SQLite (local/test fallback)
```

---

## 3) Project Structure and Responsibilities

- `main.py`
  - Creates FastAPI application
  - Registers lifespan startup hook
  - Auto-creates tables at startup
  - Mounts routers
  - Exposes `/health` and `/auth/token`
  - Configures Swagger JWT security scheme

- `database.py`
  - Reads `DATABASE_URL` from environment
  - Configures SQLAlchemy engine/session (`SessionLocal`)
  - Defines declarative `Base`

- `dependencies.py`
  - Provides DB session dependency (`get_db`)
  - Provides JWT auth dependency (`get_current_user`)

- `models/post.py`
  - SQLAlchemy `Post` table definition
  - Includes typed columns and timestamps

- `schemas/post.py`
  - Pydantic models:
    - `PostCreate`
    - `PostUpdate`
    - `PostResponse`
  - Validation constraints for title/content/tags

- `routers/post.py`
  - Post CRUD endpoints:
    - `POST /posts`
    - `GET /posts`
    - `GET /posts/{post_id}`
    - `PUT /posts/{post_id}`
    - `DELETE /posts/{post_id}`
  - Pagination and tag filtering

- `auth/auth.py`
  - JWT creation and verification logic
  - Security constants:
    - `SECRET_KEY`
    - `ALGORITHM`

- `tests/test_api.py`
  - End-to-end API tests with in-memory DB
  - Validates health, auth, CRUD, and auth guardrails

- `Procfile`
  - Runtime command for Railway/Procfile-compatible platforms

---

## 4) Data Model

## Post

- `id`: integer primary key
- `title`: string (3-200 chars, required)
- `content`: string (max 10000 chars, required)
- `tags`: list of strings (max 5 tags)
- `author_id`: integer (required)
- `created_at`: server-generated timestamp
- `updated_at`: server-generated timestamp (auto-updated)

Notes:
- Production target is PostgreSQL.
- SQLite compatibility is kept for local/testing convenience.

---

## 5) Authentication & Authorization Flow

## Token Issuance

1. Client calls `POST /auth/token?username=<value>`.
2. API creates JWT payload with:
   - `sub` = username
   - `exp` = expiry time
3. API returns:
   - `access_token`
   - `token_type = bearer`

## Protected Endpoint Access

1. Client sends `Authorization: Bearer <token>`.
2. `get_current_user` dependency validates token signature and expiry.
3. If valid, request continues.
4. If invalid/missing, API returns `401`.

---

## 6) Request Lifecycle

1. Request enters FastAPI route.
2. FastAPI runs dependencies:
   - DB session creation
   - Auth validation (if protected endpoint)
3. Pydantic validates input schema.
4. Router executes business logic and ORM operations.
5. SQLAlchemy commits/queries via session.
6. Pydantic serializes response.
7. DB session closes automatically in dependency cleanup.

---

## 7) API Design Notes

- RESTful resource design around `/posts`.
- Public endpoint:
  - `GET /health`
- Auth endpoint:
  - `POST /auth/token`
- API docs:
  - `GET /docs` (Swagger)
  - Bearer auth supported in UI.

---

## 8) Deployment Architecture (Railway)

## Runtime

- Single FastAPI service (Uvicorn process)
- Procfile command:
  - `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`

## Required Environment Variables

- `DATABASE_URL`
- `SECRET_KEY`

Recommended:
- Railway PostgreSQL plugin/service
- App variable mapping:
  - `DATABASE_URL=${{Postgres.DATABASE_URL}}`

---

## 9) Testing Strategy

- Framework: `pytest`
- Test type: API integration-style using `TestClient`
- Focus areas:
  - Health endpoint availability
  - JWT-based protection
  - Post create/read/update/delete flow
  - Unauthorized access rejection

---

## 10) Scalability and Production Considerations

- Move secrets from code to environment immediately (`SECRET_KEY`).
- Add Alembic migrations for schema evolution.
- Add structured logging and request IDs.
- Add rate limiting for auth endpoints.
- Add ownership checks (author-level authorization) for update/delete.
- Add CI pipeline for tests + linting + security checks.
- Add observability (metrics, traces, error monitoring).

---

## 11) Future Extension Points

- User model and registration/login with password hashing.
- Refresh tokens and token revocation strategy.
- Tag indexing and advanced post search.
- Soft deletes and audit history.
- Role-based access control (RBAC).

