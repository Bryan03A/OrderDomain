 # Orders Microservice - Go (Gin + PostgreSQL + External Catalog API)

 ## Description
 This microservice is responsible for retrieving paid custom orders associated with a user. 
 For each order, it enriches the data by fetching model details from an external catalog API.
 It follows the **KISS (Keep It Simple, Stupid)** design principle for modularity, clarity, and maintainability.

 ## Features
 - RESTful endpoint to retrieve all paid orders for a user
 - Integrates with a PostgreSQL database using Go's standard `database/sql` package
 - Fetches external model metadata from an external Catalog API via HTTP
 - Structured logging for operational visibility
 - Stateless design for easy containerization and scaling
 - Error handling and graceful fallbacks if model data is unavailable

 ## Endpoints

 | Endpoint               | Method | Description                                                         |
 |------------------------|--------|---------------------------------------------------------------------|
 | /orders/user/:user_id  | GET    | Returns a list of paid orders for the given user enriched with model data |

 ## Architecture: KISS + REST Integration

 - **Gin**: Lightweight and fast HTTP router and middleware framework for Go
 - **PostgreSQL**: Used as the primary data store for custom orders
 - **External API Integration**: Calls catalog microservice (`/catalog/models/id/:model_id`) to enrich data
 - **Modular Functions**: Separate functions for DB connection, data fetching, and external requests
 - **Stateless**: No session or local state is stored across requests
 - **Environment Variables**: Configuration is static in code (to be externalized for production)
 
 This service is designed for fast reads, minimal dependencies, and clean orchestration with other components.

 ## Dependencies
 - Go (1.20+)
 - Gin (`github.com/gin-gonic/gin`)
 - lib/pq (`github.com/lib/pq`) – PostgreSQL driver
 - Standard libraries: `net/http`, `database/sql`, `encoding/json`, `log`

 ## External Connections Diagram

 ```
                      ┌──────────────┐                 ┌──────────────┐
                      │   Frontend   │◄───────────────►│ Orders API   │
                      │ / Gateway    │                 └──────┬───────┘
                      └──────────────┘                        │
                                                              │ PostgreSQL
                                                        ┌─────▼──────┐
                                                        │  Orders DB │
                                                        └─────┬──────┘
                                                              │
                                                              │ Enriches each order with
                                                       ┌──────▼────────┐
                                                       │ External API  │
                                                       │ Catalog Svc   │
                                                       └───────────────┘
 ```

 ## Environment Variables (suggested)
 - `POSTGRES_URI`: PostgreSQL connection URI (currently hardcoded)
 - `CATALOG_URL`: Base URL for external catalog service (currently hardcoded)
 - `PORT`: Listening port (default `5019`)

 ## Running the Service
 ```bash
 go run main.go
 ```

 ## Recommendations
 - Move hardcoded config values (PostgreSQL URI, Catalog URL) to environment variables
 - Add request-level logging and tracing for observability
 - Integrate retries or circuit breakers for external API calls
 - Use connection pooling for database efficiency
 - Add unit tests and integration tests to validate external dependencies
 - Consider using a service mesh or API Gateway to secure and monitor traffic