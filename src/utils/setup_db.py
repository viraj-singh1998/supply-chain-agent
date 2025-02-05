import db_schema
import seed_products

def setup():
    db_schema.init_db()
    seed_products.seed_products()

if __name__ == "__main__":
    setup()