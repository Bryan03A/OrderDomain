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

// Order represents a custom order
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

// Model represents a model in the catalog
type Model struct {
	ModelID     string `json:"model_id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Format      string `json:"format"`
	Price       string `json:"price"`
	CreatedBy   string `json:"created_by"`
}

// fetchModelDetails queries the catalog and returns the details of a model
func fetchModelDetails(modelID string) (Model, error) {
	url := CATALOG_URL + modelID
	resp, err := http.Get(url)
	if err != nil {
		return Model{}, fmt.Errorf("request error: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return Model{}, fmt.Errorf("model not found")
	}

	var result struct {
		Model Model `json:"model"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return Model{}, fmt.Errorf("decode error: %v", err)
	}

	return result.Model, nil
}

// openDB creates a database connection
func openDB() (*sql.DB, error) {
	return sql.Open("postgres", POSTGRES_URI)
}

// getOrdersByUserID retrieves orders from the database for a given user_id
func getOrdersByUserID(db *sql.DB, userID string) ([]Order, error) {
	query := `SELECT id, model_id, custom_params, user_id, created_at, cost_initial, cost_final 
			  FROM customs WHERE user_id = $1 AND state = 'paid'`

	rows, err := db.Query(query, userID)
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

		if model, err := fetchModelDetails(o.ModelID); err == nil {
			o.ModelDetails = model
		}
		orders = append(orders, o)
	}
	return orders, nil
}

// handleGetOrders handles the HTTP request to get orders by user_id
func handleGetOrders(c *gin.Context) {
	userID := c.Param("user_id")

	db, err := openDB()
	if err != nil {
		log.Println("DB connection error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "DB connection failed"})
		return
	}
	defer db.Close()

	orders, err := getOrdersByUserID(db, userID)
	if err != nil {
		log.Println("Query error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Query failed"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"orders": orders})
}

func main() {
	router := gin.Default()
	router.SetTrustedProxies(nil)
	router.GET("/orders/user/:user_id", handleGetOrders)

	log.Println("Server running on port 5019...")
	router.Run(":5019")
}
