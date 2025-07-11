# 🧭 Microservices Architecture Overview

This document provides a high-level overview of each microservice in the system.

## 📌 Includes:
- 🎯 Purpose
- 💻 Language & Framework
- 🔌 Communication Style
- 🛢️ Database/Storage
- 🔐 Security Notes
- 🎨 Design Pattern
- 🔍 Endpoints
- ⚙️ Configuration Details

---

## 7️⃣ **Order Status Service** (Python / FastAPI)
- **🧠 Purpose**: Manages orders and their lifecycle statuses (requested, accepted, completed, paid, alert) with strict state transition rules and role-based permissions.
- **🧪 Port**: `5017`
- **🧰 Tech Stack**:
- &nbsp; - Language: Python
- &nbsp; - Framework: FastAPI
- &nbsp; - DB: PostgreSQL
- **🛢️ Database**:
- &nbsp; - Type: Relational
- &nbsp; - Engine: PostgreSQL
- &nbsp; - Hosted on a remote server (configurable via environment variables)
- **🔐 Security**:
- &nbsp; - Role-based state update restrictions (requester vs creator)
- &nbsp; - Validation of allowed state transitions to avoid invalid order lifecycle changes
- **📡 Communication**: REST (JSON)
- &nbsp; - Endpoints for creating orders, querying status, and updating order states
- **🌍 Endpoints**:
- &nbsp; - `POST /orders/` — Create a new order
- &nbsp; - `GET /orders/{order_id}/status` — Retrieve current status of an order
- &nbsp; - `PUT /orders/{order_id}/update` — Update the status of an order with permission and transition checks
- **🎨 Design Pattern**: `SOLID` principles applied, especially Single Responsibility and Dependency Inversion
- **🏗️ Architecture**: 3-layer (N-layer) architecture
- &nbsp; - Presentation Layer (API routes)
- &nbsp; - Domain Layer (business logic and validation in services)
- &nbsp; - Data Access Layer (repository pattern for database operations)
- **🛠️ Notes**:
- &nbsp; - Uses SQLAlchemy ORM for DB interactions
- &nbsp; - Dependency injection for DB session and service instances
- &nbsp; - Designed for maintainability, testability, and clear separation of concerns

---

## 8️⃣ **Orders Service** (Go / Gin)
- **🧠 Purpose**: Retrieves custom orders for a specific user and fetches associated model details from an external catalog service.
- **🧪 Port**: `5019`
- **🧰 Tech Stack**:
  - Language: Go
  - Framework: Gin
  - DB: PostgreSQL (external instance)
  - HTTP Client for catalog model lookup
- **🛢️ Database**:
  - Type: Relational
  - Engine: PostgreSQL
  - Hosted externally (IP: `23.23.135.253`)
- **🔐 Security**:
  - No authentication applied at the service level
  - Assumes upstream API Gateway or service mesh handles authentication
- **📡 Communication**: REST (JSON)
  - Consumes: `GET /orders/user/:user_id`
  - Calls external API: `GET http://50.19.4.172/catalog/models/id/:model_id`
- **🌍 Endpoints**:
  - `GET /orders/user/:user_id`: Returns a list of paid custom orders and enriches each with model metadata
- **📬 External Dependencies**:
  - Catalog Service at `50.19.4.172`
  - PostgreSQL database for retrieving orders
- **🎨 Design Pattern**: `KISS` (Keep It Simple)
- **🛠️ Notes**:
  - Stateless design
  - CORS is assumed to be handled by NGINX or upstream proxy
  - Logs key operations and errors

---

## 9️⃣  **Order Service** (Go / Gin)
- **🧠 Purpose**: Manages user orders retrieval from a PostgreSQL database and enriches orders with model details fetched from an external catalog service.
- **🧪 Port**: `5008`
- **🧰 Tech Stack**:
- &nbsp; - Language: Go
- &nbsp; - Framework: Gin (HTTP web framework)
- &nbsp; - DB: PostgreSQL (self-hosted)
- &nbsp; - External Service: REST API for model details
- **🛢️ Database**:
- &nbsp; - Type: Relational
- &nbsp; - Engine: PostgreSQL
- &nbsp; - Holds order records in the `customs` table
- **🔐 Security**:
- &nbsp; - No authentication implemented (public endpoint)
- &nbsp; - Runs with minimal privileges; database credentials stored in code (consider env vars for prod)
- **📡 Communication**: REST (JSON)
- &nbsp; - Fetches model data via HTTP GET from external catalog service
- **🌍 Endpoints**:
- &nbsp; - `GET /orders/user/:user_id` — Retrieves all "required" orders for the given user, including enriched model details
- **🎨 Design Pattern**: `KISS` (Keep It Simple)
- **🛠️ Notes**:
- &nbsp; - Separate functions for DB querying and external API calls for clarity and simplicity  
- &nbsp; - No CORS middleware (commented out)
- &nbsp; - Logs warnings on missing model details without failing entire request
- &nbsp; - Uses `database/sql` with Postgres driver and `gin` for HTTP server

---

## 🔟  **Order Service** (Go / Gin)
- **🧠 Purpose**: Retrieves user orders filtered by creator, enriches orders with model details fetched from an external catalog service.
- **🧪 Port**: `5018`
- **🧰 Tech Stack**:
- &nbsp; - Language: Go
- &nbsp; - Framework: Gin (HTTP web framework)
- &nbsp; - DB: PostgreSQL (Remote instance)
- &nbsp; - External HTTP service for model details enrichment
- **🛢️ Database**:
- &nbsp; - Type: Relational
- &nbsp; - Engine: PostgreSQL
- &nbsp; - Hosted remotely (IP: 23.23.135.253)
- **🔐 Security**:
- &nbsp; - No explicit authentication or authorization in this microservice (could be added)
- **📡 Communication**: REST (JSON)
- &nbsp; - Fetches order data from PostgreSQL
- &nbsp; - Fetches model details via HTTP GET to external catalog service
- **🌍 Endpoints**:
- &nbsp; - `GET /orders/created_by/:created_by` - Returns all orders created by a specific user, including enriched model details.
- **🎨 Design Pattern**: `KISS` (Keep It Simple)
- **🛠️ Notes**:
- &nbsp; - Connection pooling and error handling implemented simply
- &nbsp; - No middleware for CORS or authentication
- &nbsp; - Uses a helper function to keep DB connection logic DRY
- &nbsp; - Logs errors but continues processing to provide partial responses if some model details fail

---
