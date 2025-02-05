from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, DateTime, Numeric
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False)  # Generated UUID
    name = Column(String(255))  # Business name
    created_at = Column(DateTime, default=datetime.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    price = Column(Numeric(10,2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)

# Orders Table (For Each Order)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    status = Column(String(50), default="Pending")  # Pending, Confirmed, Shipped, Cancelled
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User")

# Order Items Table (Multiple Products Per Order)
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Numeric(10,2), nullable=False)

    order = relationship("Order")
    product = relationship("Product")

# Database Connection
DATABASE_URL = "postgresql://admin:guest@localhost:5432/greenlife"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)  # Creates tables if they don't exist

if __name__ == '__main__':
    init_db()