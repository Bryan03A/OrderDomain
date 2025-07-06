package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

const (
	POSTGRES_URI = "postgresql://admin:admin123@23.23.135.253:5432/mydb?sslmode=disable"
	CATALOG_URL  = "http://3.224.44.87/catalog/models/id/"
)

type Order struct {
	ID           int     `json:"id"`
	ModelID      string  `json:"model_id"`
	CustomParams string  `json:"custom_params"`
	UserID       string  `json:"user_id"`
	CreatedAt    string  `json:"created_at"`
	CostInitial  float64 `json:"cost_initial"`
	CostFinal    float64 `json:"cost_final"`
	ModelDetails Model   `json:"model_details,omitempty"`
}

type Model struct {
	ModelID     string `json:"model_id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Format      string `json:"format"`
	Price       string `json:"price"`
	CreatedBy   string `json:"created_by"`
}

// openDB opens the database connection and handles common errors
func openDB() (*sql.DB, error) {
	db, err := sql.Open("postgres", POSTGRES_URI)
	if err != nil {
		return nil, fmt.Errorf("failed to open DB: %w", err)
	}
	return db, nil
}

// fetchModelDetails retrieves the model details by ID from the external service
func fetchModelDetails(modelID string) (Model, error) {
	var response struct {
		Model Model `json:"model"`
	}

	resp, err := http.Get(CATALOG_URL + modelID)
	if err != nil {
		return Model{}, fmt.Errorf("request error: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return Model{}, fmt.Errorf("model not found")
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return Model{}, fmt.Errorf("decode error: %w", err)
	}

	return response.Model, nil
}

// GetOrdersByCreatedBy handles the GET request to fetch orders filtered by created_by
func GetOrdersByCreatedBy(c *gin.Context) {
	createdBy := c.Param("created_by")

	db, err := openDB()
	if err != nil {
		log.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database connection failed"})
		return
	}
	defer db.Close()

	rows, err := db.Query(`
		SELECT id, model_id, custom_params, user_id, created_at, cost_initial, cost_final
		FROM customs
		WHERE created_by = $1
	`, createdBy)
	if err != nil {
		log.Println("DB query error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Query failed"})
		return
	}
	defer rows.Close()

	var orders []Order
	for rows.Next() {
		var order Order
		if err := rows.Scan(&order.ID, &order.ModelID, &order.CustomParams, &order.UserID, &order.CreatedAt, &order.CostInitial, &order.CostFinal); err != nil {
			log.Println("Row scan error:", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading orders"})
			return
		}

		modelDetails, err := fetchModelDetails(order.ModelID)
		if err != nil {
			log.Printf("Warning: Model details not found for model_id %s: %v\n", order.ModelID, err)
		} else {
			order.ModelDetails = modelDetails
		}

		orders = append(orders, order)
	}

	c.JSON(http.StatusOK, gin.H{"orders": orders})
}

func main() {
	gin.SetMode(gin.ReleaseMode)

	router := gin.New()
	router.Use(gin.Logger(), gin.Recovery())

	router.SetTrustedProxies(nil)
	router.GET("/orders/created_by/:created_by", GetOrdersByCreatedBy)

	log.Println("Server running on port 5018...")
	router.Run("0.0.0.0:5018")
}
