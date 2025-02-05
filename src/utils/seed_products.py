from sqlalchemy.orm import Session
from db_schema import Product, SessionLocal

# Sample product data
PRODUCTS = [
    {"name": "Organic Almonds", "description": "Raw organic almonds", "price": 12.99, "stock_quantity": 100},
    {"name": "Whole Wheat Pasta", "description": "100% whole wheat pasta", "price": 4.99, "stock_quantity": 200},
    {"name": "Organic Green Tea", "description": "Loose leaf organic green tea", "price": 6.99, "stock_quantity": 150},
    {"name": "Natural Peanut Butter", "description": "No sugar, no additives", "price": 8.49, "stock_quantity": 180},
    {"name": "Quinoa", "description": "Gluten-free, organic quinoa", "price": 7.99, "stock_quantity": 250},
    {"name": "Chia Seeds", "description": "Rich in omega-3 and fiber", "price": 5.99, "stock_quantity": 300},
    {"name": "Organic Honey", "description": "Raw unfiltered honey", "price": 10.99, "stock_quantity": 120},
    {"name": "Brown Rice", "description": "Whole grain brown rice", "price": 3.99, "stock_quantity": 400},
    {"name": "Coconut Oil", "description": "Cold-pressed virgin coconut oil", "price": 9.99, "stock_quantity": 130},
    {"name": "Oats", "description": "Gluten-free organic oats", "price": 4.49, "stock_quantity": 220},
    {"name": "Flax Seeds", "description": "High in fiber and omega-3", "price": 5.49, "stock_quantity": 260},
    {"name": "Dried Cranberries", "description": "Sweet and tangy dried cranberries", "price": 6.49, "stock_quantity": 140},
    {"name": "Organic Black Beans", "description": "Non-GMO black beans", "price": 2.99, "stock_quantity": 350},
    {"name": "Cashew Butter", "description": "Creamy and nutritious", "price": 11.99, "stock_quantity": 100},
    {"name": "Organic Turmeric Powder", "description": "Pure turmeric spice", "price": 4.99, "stock_quantity": 170},
    {"name": "Coconut Flour", "description": "Gluten-free baking alternative", "price": 6.99, "stock_quantity": 200},
    {"name": "Raw Walnuts", "description": "Fresh and crunchy", "price": 13.99, "stock_quantity": 90},
    {"name": "Organic Apple Cider Vinegar", "description": "With the mother", "price": 7.49, "stock_quantity": 110},
    {"name": "Himalayan Pink Salt", "description": "Mineral-rich salt", "price": 3.99, "stock_quantity": 300},
    {"name": "Cacao Nibs", "description": "Raw unsweetened cacao", "price": 9.49, "stock_quantity": 80},
]

# Function to populate the database
def seed_products():
    db: Session = SessionLocal()
    try:
        # Insert all products
        for product in PRODUCTS:
            db.add(Product(**product))
        db.commit()
        print("Successfully added 20 products to the database.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting products: {e}")
    finally:
        db.close()

# Run the script
if __name__ == "__main__":
    seed_products()