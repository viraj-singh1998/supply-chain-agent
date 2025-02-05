from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from .db_schema import User, Product, Order, OrderItem, SessionLocal
from .config import *
from datetime import datetime, timedelta

def create_user(user_id: str, user_name: str) -> str:
    """
    Creates a new user with the given user ID. Calling format: create_user: {"user_id": <user_id>, "user_name": <user_name>}
    Args:
        user_id (str): The unique identifier for the user.
        user_name (str): The user's name
    Returns:
        str: Confirmation message on successful user creation or an error message.
    """
    user_id = user_id.strip('\n').strip()
    user_name = user_name.strip('\n').strip()

    db: Session = SessionLocal()
    try:
        # Check if the user with the given user_id already exists
        existing_user = db.query(User).filter(User.user_id == user_id).first()
        if existing_user:
            return f"Error: User with ID {user_id} already exists."

        # Create a new user if no existing user is found
        user = User(user_id=user_id, name=user_name, created_at=datetime.now())
        db.add(user)
        db.commit()
        return f"User {user_name} with ID: {user_id} successfully created."
    
    except SQLAlchemyError as e:
        db.rollback()
        return f"Error creating user: {e}"
    
    finally:
        db.close()


def list_all_products() -> list:
    """
    Lists all unique products along with their corresponding IDs, names and stock quantities. Calling format: list_all_products: {}
    Returns:
        list: A list of dictionaries with product details (id, name, stock_quantity).
    """
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        return [{"id": p.id, "name": p.name, "stock_quantity": p.stock_quantity} for p in products]
    finally:
        db.close()


def place_order(user_id: str, products: dict) -> dict:
    """
    Places a new order for the user, checking stock availability for all requested products.
    Updates the stock quantity after placing the order.
    """
    user_id = user_id.strip('\n').strip()

    db: Session = SessionLocal()
    try:
        out_of_stock_items = []
        total_price = 0
        order_items = []

        for product_id, quantity in products.items():
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product or product.stock_quantity < quantity:
                out_of_stock_items.append({"product_id": product_id, "available_stock": product.stock_quantity if product else 0})
            else:
                total_price += product.price * quantity
                order_items.append({"product_id": product_id, "quantity": quantity, "price_per_unit": product.price})

        if out_of_stock_items:
            return {"error": "Some items are out of stock", "out_of_stock": out_of_stock_items}

        # Create the order
        order = Order(user_id=user_id, total_amount=total_price, status="Confirmed", created_at=datetime.now())
        db.add(order)
        db.commit()

        # Create order items and update stock quantities
        for item in order_items:
            product = db.query(Product).filter(Product.id == item["product_id"]).first()
            product.stock_quantity -= item["quantity"]  # Update stock quantity
            db.add(OrderItem(order_id=order.id, **item))

        db.commit()
        return {"order_id": order.id, "total_amount": total_price, "status": "Pending"}
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"error": str(e)}
    
    finally:
        db.close()


def get_past_orders(user_id: str) -> list:
    """
    Retrieves all past orders of a user along with their items (each item's id, name, status, and bill amount).
    Calling format: get_past_orders: {"user_id": <user_id>}
    Args:
        user_id (str): The unique identifier of the user.
    
    Returns:
        list: A list of dictionaries containing order details (order_id, total_amount, status, items).
    """
    user_id = user_id.strip('\n').strip()
    print(f'user ID: <{user_id}>')
    db: Session = SessionLocal()
    try:
        # Perform the join between Order, OrderItem, and Product based on product_id and order_id
        orders = db.query(Order, OrderItem, Product).join(OrderItem, Order.id == OrderItem.order_id) \
                                                     .join(Product, OrderItem.product_id == Product.id) \
                                                     .filter(Order.user_id == user_id).all()

        # Construct the response by iterating over the orders and order items
        order_details = []
        for order, item, product in orders:
            order_data = next((o for o in order_details if o['order_id'] == order.id), None)
            if not order_data:
                order_data = {
                    "order_id": order.id,
                    "total_amount": order.total_amount,
                    "status": order.status,
                    "items": [],
                }
                order_details.append(order_data)

            # Add the item details including the product name to the appropriate order
            order_data["items"].append({
                "product_id": item.product_id,
                "product_name": product.name,  # Added product name
                "quantity": item.quantity,
                "price_per_unit": item.price_per_unit,
            })
        print(order_details)
        return order_details
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"error": str(e)}
    
    finally:
        db.close()


def modify_order(order_id: int, new_products: dict) -> str:
    """
    Modifies an existing order if it is still pending. Updates stock quantities for the modified items.
    """
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.status.in_(['Pending', 'Confirmed'])).first()
        if not order:
            return "Order cannot be modified, it is either not found or already processed."

        # Cancel old order items and update stock quantities back
        old_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in old_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            product.stock_quantity += item.quantity  # Revert stock quantity
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

        total_price = 0
        for product_id, quantity in new_products.items():
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product or product.stock_quantity < quantity:
                return f"Product {product_id} is out of stock."

            total_price += product.price * quantity
            db.add(OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, price_per_unit=product.price))

            product.stock_quantity -= quantity  # Update stock quantity

        order.total_amount = total_price
        db.commit()
        return f"Order {order_id} successfully modified."
    
    except SQLAlchemyError as e:
        db.rollback()
        return f"Error modifying order: {e}"
    
    finally:
        db.close()


def cancel_order(order_id: int) -> str:
    """
    Cancels an order if it is still pending. Updates stock quantities for the canceled items.
    """
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.status.in_(['Pending', 'Confirmed'])).first()
        if not order:
            return "Order cannot be canceled. It is either not found or already processed."

        # Update stock quantities for canceled items
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            product.stock_quantity += item.quantity  # Revert stock quantity

        order.status = "Canceled"
        db.commit()
        return f"Order {order_id} successfully canceled."
    
    finally:
        db.close()


def refresh_order_status():
    """
    Refreshes the order status for all orders that are 5 minutes or older and have a status of "Confirmed".
    Updates their status to "Shipped".
    
    Calling format: refresh_order_status: {}
    
    Returns:
        dict: A message indicating how many orders were updated.
    """
    db: Session = SessionLocal()
    try:
        # Get the timestamp 5 minutes ago
        time_threshold = datetime.now() - timedelta(minutes=config.SHIPPING_TURNAROUND_MINS)

        # Update all orders with status 'Confirmed' that are 5 minutes or older
        updated_orders = db.query(Order).filter(Order.status == "Confirmed", Order.created_at <= time_threshold).all()

        if updated_orders:
            # Update the status to 'Shipped'
            for order in updated_orders:
                order.status = "Shipped"
            
            db.commit()
            return {"message": f"{len(updated_orders)} order(s) successfully updated to 'Shipped'."}
        else:
            return {"message": "No orders to update."}
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"error": str(e)}
    
    finally:
        db.close()


def get_order_status(order_id: int) -> str:
    """
    Checks the current status of an order. Calling format: get_order_status: {"order_id": <order_id>}
    Args:
        order_id (int): The order ID to check the status of.
    
    Returns:
        str: The current status of the order.
    """
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        return order.status if order else "Order not found."
    finally:
        db.close()


def reorder_previous_order(order_id: int) -> dict:
    """
    Places a reorder for a previously completed order. Updates stock quantities for reordered items.
    """
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"error": "Order not found."}

        previous_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        product_quantities = {item.product_id: item.quantity for item in previous_items}

        # Place the new order and update stock quantities
        return place_order(order.user_id, product_quantities)
    
    finally:
        db.close()