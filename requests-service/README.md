# Order Microservice - Go (Gin + PostgreSQL + External HTTP)

 ## Description
 This microservice provides order retrieval functionality, filtered by the creator's identifier. It connects to a PostgreSQL database to fetch order records, then enriches each order with detailed model information by querying an external catalog HTTP service. The service is designed with simplicity and maintainability in mind, following the **KISS (Keep It Simple, Stupid)** principle.
 
 ## Features
 - Fetches orders filtered by the `created_by` field from a PostgreSQL table named `customs`.
 - For each order, fetches detailed model information from an external REST catalog service.
 - Gracefully handles partial failures when model details cannot be retrieved, logging warnings without breaking the entire response.
 - Database connection logic encapsulated in a helper function for reuse and clearer error handling.
 - Lightweight HTTP REST API built with the Gin framework, optimized for fast responses and low resource use.
 - No explicit authentication or CORS middleware enabled, assuming this service is deployed in a trusted network or behind a gateway.
 
 ## Endpoints
 | Endpoint                  | Method | Description                                                     |
 |---------------------------|--------|-----------------------------------------------------------------|
 | /orders/created_by/:created_by | GET    | Returns all orders created by a specific user, enriched with model details fetched from an external service. |
 
 ## Architecture: KISS + DRY
 - **Go + Gin**: Minimalist, fast web framework for REST API.
 - **PostgreSQL**: Relational DB for persistent order data.
 - **External Catalog Service**: Provides model metadata used to enrich orders.
 - **Database Connection Helper**: Simplifies and centralizes DB connection setup and error handling.
 - **Simple Logging**: Logs errors and warnings clearly, aiding debugging without halting the service.
 
 ## Dependencies
 - github.com/gin-gonic/gin
 - github.com/lib/pq (PostgreSQL driver)
 - Go standard library (net/http, database/sql, encoding/json, log)
 
 ## External Connections Diagram
 
 ```text
    ┌───────────────┐                     ┌─────────────┐
    │   Client /    │    HTTP GET         │  Order      │
    │ Frontend App  │────────────────────►│ Microservice│
    └───────────────┘                     └──────┬──────┘
                                                 │
                       ┌─────────────────────────┴──────────────────────┐
                       │                                                │
               ┌───────▼─────────┐                           ┌───────────▼───────────┐
               │  PostgreSQL DB  │                           │ External Catalog HTTP │
               │ (Orders stored) │                           │ Service (Model Data)  │
               └─────────────────┘                           └───────────────────────┘
 ```
 ## Environment Variables
 - `POSTGRES_URI`: PostgreSQL connection string (e.g. `postgresql://user:pass@host:port/dbname?sslmode=disable`)
 - `CATALOG_URL`: Base URL for external model catalog API (e.g. `http://catalog-service/models/id/`)

 ## Running the Service
 ```bash
 go run main.go
 ```

 ## Recommendations
 - Add authentication and authorization to protect endpoints if exposing publicly.
 - Implement CORS if accessed directly by browser clients.
 - Consider caching model details for improved performance and reduced external calls.
 - Add metrics and tracing for observability in production.
 - Use connection pooling and graceful shutdown for robustness.

 ---