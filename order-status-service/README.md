# Order Status Microservice - FastAPI (PostgreSQL)

## Description
This microservice manages the full lifecycle of orders by tracking multiple status flags such as `requested`, `accepted`, `completed`, `paid`, and `alert`. It enforces strict business rules on state transitions and role-based permissions to ensure order integrity and correctness. Designed with maintainability and clarity in mind, it follows **SOLID** principles and uses a clean 3-layer architecture (presentation, domain, data access).

## Features
- Order creation with unique order IDs
- Retrieval of current order status and metadata
- Controlled state updates with validation of allowed transitions:
  - Cannot accept before requested
  - Cannot complete before accepted
  - Cannot pay before completed
  - No backward state changes once a later state is true
- Role-based permissions on state updates (e.g., only requester can update `requested` and `paid`, only creator can update `accepted` and `completed`)
- SQLAlchemy ORM for PostgreSQL integration
- Dependency injection for DB session and business logic
- Designed for clear separation of concerns to ease testing and future extension

## Endpoints

| Endpoint                 | Method | Description                                  |
|--------------------------|--------|----------------------------------------------|
| `/orders/`               | POST   | Create a new order                           |
| `/orders/{order_id}/status` | GET    | Retrieve current status and details of an order |
| `/orders/{order_id}/update` | PUT    | Update a specific status field of an order (with validation and permissions) |

## Architecture: SOLID + N-Layer

- **Presentation Layer**: FastAPI routes handle HTTP requests/responses and validation.
- **Domain Layer**: Business logic enforces state transition rules and permission checks.
- **Data Access Layer**: SQLAlchemy models and session management abstract database interaction.
- Dependency Injection pattern enables clean, testable components and decouples database from business logic.

## External Connections Diagram

```
                  ┌──────────────┐
                  │  Frontend /  │
                  │   Client     │
                  └──────┬───────┘
                         │ REST JSON
                         ▼
                  ┌──────────────┐
                  │   FastAPI    │
                  │   (API)      │
                  └──────┬───────┘
                         │ DB session
                         ▼
                  ┌──────────────┐
                  │ SQLAlchemy   │
                  │ (PostgreSQL) │
                  └──────────────┘
```
## Environment Variables / Config

- `DB_URL`: PostgreSQL connection string (e.g. `postgresql://user:pass@host:port/dbname`)
- `SECRET_KEY`: Used for security or JWT (if extended)
- `PORT`: Service port (default 5017)

## Running the Service

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 5017 --reload
```

## Recommendations
- Run behind a production-grade ASGI server (e.g. Gunicorn + Uvicorn workers) in production
- Secure environment variables using a secrets manager
- Add logging and monitoring for operational visibility
- Extend with event-driven messaging if asynchronous workflows are needed
- Write unit and integration tests for business rules and API endpoints

---