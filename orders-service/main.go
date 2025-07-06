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

// fetchModelDetails fetches model details from an external service.
func fetchModelDetails(modelID string) (Model, error) {
	resp, err := http.Get(CATALOG_URL + modelID)
	if err != nil {
		return Model{}, fmt.Errorf("error requesting model: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return Model{}, fmt.Errorf("model not found (status %d)", resp.StatusCode)
	}

	var result struct {
		Model Model `json:"model"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return Model{}, fmt.Errorf("error decoding JSON: %w", err)
	}

	return result.Model, nil
}

// getOrdersByUserID retrieves orders from the database for a specific user.
func getOrdersByUserID(db *sql.DB, userID string) ([]Order, error) {
	rows, err := db.Query(`SELECT id, model_id, custom_params, user_id, created_at, cost_initial, cost_final 
		FROM customs WHERE user_id = $1 AND state = 'required'`, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var orders []Order
	for rows.Next() {
		var o Order
		if err := rows.Scan(&o.ID, &o.ModelID, &o.CustomParams, &o.UserID, &o.CreatedAt, &o.CostInitial, &o.CostFinal); err != nil {
			return nil, err
		}

		model, err := fetchModelDetails(o.ModelID)
		if err == nil {
			o.ModelDetails = model
		} else {
			log.Printf("Warning: no model details for model_id %s: %v", o.ModelID, err)
		}

		orders = append(orders, o)
	}

	return orders, nil
}

// HTTP handler for the /orders/user/:user_id route
func GetOrdersByUserIDHandler(c *gin.Context) {
	userID := c.Param("user_id")

	db, err := sql.Open("postgres", POSTGRES_URI)
	if err != nil {
		log.Println("DB connection error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database connection failed"})
		return
	}
	defer db.Close()

	orders, err := getOrdersByUserID(db, userID)
	if err != nil {
		log.Println("Error fetching orders:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch orders"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"orders": orders})
}

func main() {
	gin.SetMode(gin.ReleaseMode)

	router := gin.New()
	router.Use(gin.Logger(), gin.Recovery())
	router.SetTrustedProxies(nil)

	router.GET("/orders/user/:user_id", GetOrdersByUserIDHandler)

	log.Println("Server running on port 5008...")
	if err := router.Run("0.0.0.0:5008"); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
