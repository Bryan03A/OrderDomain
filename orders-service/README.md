 # Order Service - Go (Gin + PostgreSQL)
 
 ## Description
 This microservice retrieves user orders from a PostgreSQL database and enriches each order with detailed model information obtained from an external catalog service via REST. 
 It is designed with the **KISS (Keep It Simple, Stupid)** principle, emphasizing straightforward and maintainable code by separating concerns clearly: database access, external API communication, and HTTP request handling.
 The service exposes a single REST endpoint to fetch all “required” orders for a user, including detailed metadata about each model ordered.
 
 ## Features
 - Retrieves orders filtered by user ID and status ("required") from PostgreSQL
 - For each order, fetches model details (name, description, price, etc.) from an external catalog service via HTTP GET
 - Uses Gin framework for HTTP routing and middleware (logging, recovery)
 - Clear separation between data retrieval and enrichment logic
 - Graceful error handling: logs warnings if model details are missing but does not fail the entire request
 - Minimal dependencies for simplicity and performance
 
 ## Endpoints
 
 | Endpoint             | Method | Description                                                    |
 |----------------------|--------|----------------------------------------------------------------|
 | /orders/user/:user_id | GET    | Returns all “required” orders for a user, enriched with model details |
 
 ## Architecture: KISS + RESTful
 
 - **Gin**: Lightweight HTTP web framework for Go, used for routing and middleware
 - **database/sql**: Standard Go SQL package to query PostgreSQL directly
 - **External API Calls**: Model data fetched synchronously using net/http
 - **Logging**: Standard log package for error and warning output
 
 ## Database
 - Relational database PostgreSQL stores order records in a `customs` table
 - Orders are filtered by `user_id` and `state = 'required'` in queries
 - Database connection uses a static connection string (recommend using environment variables in production)
 
 ## Security
 - No authentication or authorization implemented; the endpoint is publicly accessible
 - Database credentials are hardcoded (should be replaced with environment variables for security)
 
 ## Dependencies
 - Gin web framework
 - lib/pq PostgreSQL driver
 
 ## External Connections Diagram
 
 ``` 
                ┌─────────────┐      HTTP GET      ┌────────────────┐
                │  Client /   │◄──────────────────►│  Order Service │
                │  Frontend   │                    └──────┬─────────┘
                └─────────────┘                           │
                                                Queries orders by user_id
                                                          │
                                                  ┌───────▼────────┐
                                                  │ PostgreSQL DB  │
                                                  └───────┬────────┘
                                                          │
                                                Gets model details by model_id
                                                          │
                                                   ┌──────▼──────────┐
                                                   │ Catalog Service │
                                                   └─────────────────┘
 ```

 ## Running the Service
 ```bash
 go mod tidy
 go run main.go
 ```

 ## Recommendations
 - Use environment variables for sensitive configuration (DB URI, catalog URL)
 - Add authentication and authorization to secure endpoints
 - Consider caching model details to reduce external API calls and improve performance
 - Implement connection pooling and better error handling for production readiness
 - Add CORS middleware if the API is accessed from browsers