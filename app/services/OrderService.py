from sqlalchemy.orm import Session
from app.models import Order, Portfolio, Transaction, Asset, User
from app.services.MarketDataService import MarketDataService
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime


class OrderService:
    @staticmethod
    def create_order(
        user_id: int, symbol: str, quantity: float,
        order_type: str, action: str, db: Session, price: float = None
    ):
        # Step 1: Fetch user and portfolio
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Step 2: Fetch market price if it's a market order
        if order_type == "market":
            current_price = MarketDataService.get_market_data(symbol)
            price = current_price  # Use the current price for market orders
        elif order_type == "limit" and price is None:
            raise HTTPException(status_code=400, detail="Limit orders require a price")

        # Step 3: Set the position type based on the action
        position_type = "long" if action == "buy" else "short"

        # Step 4: Create the order object
        new_order = Order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=order_type,
            action=action,
            status="executed" if order_type == "market" else "pending",
            executed_at=datetime.utcnow() if order_type == "market" else None,
            user_id=user_id,
        )
        db.add(new_order)

        # Step 5: If the order is executed, update portfolio and assets
        if new_order.status == "executed":
            total_amount = price * quantity

            if action == "buy":
                if portfolio.balance < total_amount:
                    raise HTTPException(status_code=400, detail="Insufficient balance")
                portfolio.balance -= total_amount
                update_asset(symbol, quantity, price, position_type, portfolio.id, db)
            elif action == "sell":
                asset = db.query(Asset).filter(
                    Asset.symbol == symbol, Asset.portfolio_id == portfolio.id
                ).first()
                if not asset or asset.quantity < quantity:
                    raise HTTPException(status_code=400, detail="Insufficient quantity to sell")
                portfolio.balance += total_amount
                update_asset(symbol, -quantity, price, position_type, portfolio.id, db)

            # Record the transaction
            transaction = Transaction(
                symbol=symbol,
                quantity=quantity,
                price=price,
                total=total_amount,
                transaction_type=action,
                position_type=position_type,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            db.add(transaction)

        # Commit changes to the database
        db.commit()
        db.refresh(new_order)
        return new_order

    @staticmethod
    def process_limit_orders(db: Session):
        """Check and execute pending limit orders if the market price matches."""
        # Fetch all pending limit orders
        pending_orders = db.query(Order).filter(
            Order.status == "pending", Order.order_type == "limit"
        ).all()

        for order in pending_orders:
            # Get the latest market price
            market_price = MarketDataService.get_market_data(order.symbol)

            # Check if the limit price matches the market price
            if (order.action == "buy" and market_price <= order.price) or \
               (order.action == "sell" and market_price >= order.price):
                # Execute the order
                OrderService.execute_order(order, market_price, db)

    @staticmethod
    def execute_order(order: Order, market_price: float, db: Session):
        """Execute a pending limit order and update the portfolio and transaction."""
        user = db.query(User).filter(User.id == order.user_id).first()
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == order.user_id).first()

        # Calculate total amount (quantity * market price)
        total_amount = market_price * order.quantity

        # Handle balance updates based on buy/sell action
        if order.action == "buy":
            if portfolio.balance < total_amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            portfolio.balance -= total_amount
            update_asset(order.symbol, order.quantity, market_price, "long", portfolio.id, db)
        elif order.action == "sell":
            asset = db.query(Asset).filter(
                Asset.symbol == order.symbol, Asset.portfolio_id == portfolio.id
            ).first()
            if not asset or asset.quantity < order.quantity:
                raise HTTPException(status_code=400, detail="Insufficient quantity to sell")
            portfolio.balance += total_amount
            update_asset(order.symbol, -order.quantity, market_price, "short", portfolio.id, db)

        # Update order status and record the transaction
        order.status = "executed"
        order.executed_at = datetime.utcnow()

        transaction = Transaction(
            symbol=order.symbol,
            quantity=order.quantity,
            price=market_price,
            total=total_amount,
            transaction_type=order.action,
            position_type="long" if order.action == "buy" else "short",
            user_id=order.user_id,
            created_at=datetime.utcnow()
        )
        db.add(transaction)

        # Commit changes
        db.commit()
        db.refresh(order)

def update_asset(symbol: str, quantity: float, price: float, position_type: str, portfolio_id: int, db: Session):
    """Update or create asset in the portfolio based on the executed order."""
    asset = db.query(Asset).filter(
        Asset.symbol == symbol, Asset.portfolio_id == portfolio_id
    ).first()

    if quantity > 0:  # Buy action
        if asset:
            total_quantity = asset.quantity + quantity
            asset.price_bought = ((asset.price_bought * asset.quantity) + (price * quantity)) / total_quantity
            asset.quantity = total_quantity
        else:
            new_asset = Asset(
                symbol=symbol,
                quantity=quantity,
                price_bought=price,
                position_type=position_type,
                portfolio_id=portfolio_id
            )
            db.add(new_asset)
    else:  # Sell action
        if asset:
            asset.quantity += quantity  # Subtract sold quantity (quantity is negative)
            if asset.quantity == 0:
                db.delete(asset)

    db.commit()
