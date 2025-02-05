# Supply Chain Agent

## Overview
This repository contains an AI-powered conversational agent designed to streamline the **order capture process** for distributors and retailers of GreenLife Foods. The agent enables users to **inquire about past orders, place new orders, check product availability, modify/cancel orders, and reorder past purchases** through a conversational interface.<br>
The agent is able to **course-correct** by means of feedback loops in the conversation, and without explicit logic routing of any kind. For example, if a user mistakenly places an order for a product that does not exist in the inventory, the agent will be corrected at *place_order()*, after which it is likely to implicitly call *list_all_products()* to disambiguate the user's query.

## Prompt
- The system prompt can be found in src/utils/config.py
- ReAct methodology implemented from scratch.
- Success/Error response fed back into ReAct loop to self-correct.
- Examples given at src/exemplars.txt
---


## Features
- **Conversational AI** using OpenAI GPT-4 mini
- **Order management system** (create, modify, cancel, reorder)
- **Product inquiry system**
- **User conversation history retrieval** for contextual continuity
- **PostgreSQL database** for persistence
- **FastAPI-based backend** for CRUD operations
- **Streamlit frontend** for user interaction

---

## Setup Instructions

### **1. Clone the Repository**
```sh
 git clone https://github.com/viraj-singh1998/supply-chain-agent.git
 cd supply-chain-agent
```

### **2. Set Up PostgreSQL with Docker**
Ensure Docker is installed and running. Then, start a PostgreSQL container:
```sh
docker run --name supply-chain-db -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=guest -e POSTGRES_DB=supply_chain -p 5432:5432 -d postgres
```

To verify the container is running:
```sh
docker ps
```

### **3. Install Dependencies**
Ensure Python (>=3.9) and `pip` are installed, then run:
```sh
pip install -r requirements.txt
```

### **4. Set Up the Database**
Run database migrations to create the required tables:
```sh
python src/utils/setup_db.py
```

### **5. Start the Backend API (FastAPI)**
```sh
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```
The API will be accessible at: [http://localhost:8080/docs](http://localhost:8080/docs)

### **6. Start the Frontend (Streamlit)**
```sh
streamlit run frontend.py
```
This will launch the chatbot interface in your browser.

---

## Environment Variables
Create a `.env` file in the root directory with the following:
```ini
DB_URL=postgresql://admin:admin@localhost/supply_chain
OPENAI_API_KEY=your-openai-api-key
LLAMA_API_KEY=your-llama-api-key
```

---

## Assumptions & Limitations
- Users must be identified by a unique user ID.
- The database must be manually seeded with products.
- The order status assumes 4 exhaustive states: **Pending, Confirmed, Shipped, Cancelled**
- Authentication has not been implemented yet in any measure except by not providing the user a tool to query the User table. Therefore, a user can only access user/order information about themselves.
- Only one tool call possible at a time.
- **[EXPERIMENTAL OBSERVATION]** Long running conversations tend to act as pseudo-exemplars to the model and encourage it to break format, causing unchecked generation till an error is thrown. Handling conversation history/memory to be implemented in a better way.

---

## Order Status Descriptions

- **Pending**: This status is applied to orders momentarily before the process completes successfully. If the order placement process fails, the order stays in the "Pending" state until further action is taken.
- **Confirmed**: Once the order placement process goes through smoothly, the order status changes to "Confirmed."
- **Shipped**: Orders that are "Confirmed" change to "Shipped" after a configurable parameter in the config: `SHIPPING_TURNAROUND_MINS` (currently set to 5 minutes).
- **Cancelled**: This status applies if the user opts to cancel an existing order, and the cancellation is processed quickly.

---

## Running PostgreSQL Interactive Shell
To interact with the database directly, start a PostgreSQL interactive session inside the running container:
```sh
docker exec -it supply-chain-db psql -U admin -d supply_chain
```

### **Example Queries**

#### **Check available tables**
```sql
\dt
```

#### **View all users**
```sql
SELECT * FROM users;
```

#### **View all orders placed by a specific user**
```sql
SELECT o.id, o.total_amount, o.status, o.created_at
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.user_id = 'specific-user-id';
```

#### **View all products in an order**
```sql
SELECT oi.order_id, p.name, oi.quantity, oi.price_per_unit
FROM order_items oi
JOIN products p ON oi.product_id = p.id
WHERE oi.order_id = 1;
```

#### **Count total orders per user**
```sql
SELECT u.user_id, COUNT(o.id) AS total_orders
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id;
```

#### **Delete a specific order**
```sql
DELETE FROM orders WHERE id = 2;
```