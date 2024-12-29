from sqlalchemy.orm import Session
from app.models import Order, Portfolio, Transaction, Asset, User
from app.services.MarketDataService import MarketDataService
from fastapi import HTTPException
from datetime import datetime

class OrderService:
    @staticmethod
    def create_order(
        user_id: int, symbol: str, quantity: float, order_type: str, action: str, 
        db: Session, price: float = None, take_profit: float = None, stop_loss: float = None
    ):
        # Fetch user and portfolio as before
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if order_type == "market":
            current_price = MarketDataService.get_market_data(symbol)
            price = current_price
        elif order_type == "limit" and price is None:
            raise HTTPException(status_code=400, detail="Limit orders require a price")

        # Create the new order
        new_order = Order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=order_type,
            action=action,
            status="executed" if order_type == "market" else "pending",
            executed_at=datetime.utcnow() if order_type == "market" else None,
            user_id=user_id,
            take_profit=take_profit,
            stop_loss=stop_loss
        )
        db.add(new_order)

        if new_order.status == "executed":
            total_amount = price * quantity
            if action == "buy":
                if portfolio.balance < total_amount:
                    raise HTTPException(status_code=400, detail="Insufficient balance")
                portfolio.balance -= total_amount
                update_asset(symbol, quantity, price, "long", portfolio.id, db)
            elif action == "sell":
                asset = db.query(Asset).filter(
                    Asset.symbol == symbol, Asset.portfolio_id == portfolio.id
                ).first()
                if not asset or asset.quantity < quantity:
                    raise HTTPException(status_code=400, detail="Insufficient quantity to sell")
                portfolio.balance += total_amount
                update_asset(symbol, -quantity, price, "short", portfolio.id, db)

        db.commit()
        db.refresh(new_order)
        return new_order

    @staticmethod
    def process_limit_orders(db: Session):
        """Check and execute pending limit orders or trigger stop-loss/take-profit."""
        pending_orders = db.query(Order).filter(Order.status == "pending").all()

        for order in pending_orders:
            market_price = MarketDataService.get_market_data(order.symbol)

            # Execute Limit Orders
            if order.order_type == "limit" and (
                (order.action == "buy" and market_price <= order.price) or
                (order.action == "sell" and market_price >= order.price)
            ):
                OrderService.execute_order(order, market_price, db)

            # Trigger Stop Loss
            elif order.stop_loss is not None and (
                (order.action == "buy" and market_price <= order.stop_loss) or
                (order.action == "sell" and market_price >= order.stop_loss)
            ):
                OrderService.execute_order(order, market_price, db)

            # Trigger Take Profit
            elif order.take_profit is not None and (
                (order.action == "buy" and market_price >= order.take_profit) or
                (order.action == "sell" and market_price <= order.take_profit)
            ):
                OrderService.execute_order(order, market_price, db)

    @staticmethod
    def execute_order(order: Order, market_price: float, db: Session):
        """Execute a pending limit order and update the portfolio and transaction."""
        user = db.query(User).filter(User.id == order.user_id).first()
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == order.user_id).first()

        total_amount = market_price * order.quantity

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

        db.commit()
        db.refresh(order)


def update_asset(symbol: str, quantity: float, price: float, position_type: str, portfolio_id: int, db: Session):
    asset = db.query(Asset).filter(
        Asset.symbol == symbol, Asset.portfolio_id == portfolio_id
    ).first()

    if quantity > 0:
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
    else:
        if asset:
            asset.quantity += quantity
            if asset.quantity == 0:
                db.delete(asset)

    db.commit()
