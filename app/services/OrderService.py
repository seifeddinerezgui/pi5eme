from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Portfolio, Asset, Transaction, User
from app.models.order import Order
from app.services.MarketDataService import MarketDataService

class OrderService:

    @staticmethod
    def create_buy_order(user_id: int, symbol: str, quantity: float, order_position_type: str, db: Session):
        # Step 1: Fetch user and portfolio
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Step 2: Fetch the current market price of the asset
        current_price = MarketDataService.get_market_data(symbol)

        # Step 3: Calculate total cost of the order
        total_cost = current_price * quantity

        # Step 4: Check if the user has enough balance
        if portfolio.balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Step 5: Deduct balance from portfolio
        portfolio.balance -= total_cost

        # Step 6: Create a new order
        db_order = Order(
            symbol=symbol,
            quantity=quantity,
            price=current_price,
            order_type="buy",  # Fixed as 'buy' since this is a buy order
            order_position_type=order_position_type,
            executed_at=datetime.utcnow(),
            user_id=user_id
        )

        # Step 7: Record the transaction
        transaction = Transaction(
            symbol=symbol,
            quantity=quantity,
            price=current_price,
            total=total_cost,
            transaction_type="buy",
            position_type=order_position_type,
            user_id=user_id
        )

        # Step 8: Update asset in the portfolio
        asset = db.query(Asset).filter(Asset.portfolio_id == portfolio.id, Asset.symbol == symbol,
                                       Asset.position_type == order_position_type).first()

        if asset:
            # Update asset's quantity and average price
            total_quantity = asset.quantity + quantity
            asset.price_bought = ((asset.price_bought * asset.quantity) + (current_price * quantity)) / total_quantity
            asset.quantity = total_quantity
        else:
            # Add a new asset if not found in the portfolio
            new_asset = Asset(
                symbol=symbol,
                quantity=quantity,
                price_bought=current_price,
                position_type=order_position_type,
                portfolio_id=portfolio.id
            )
            db.add(new_asset)

        # Step 9: Commit changes to the database
        db.add(db_order)
        db.add(transaction)
        db.commit()
        db.refresh(db_order)
        db.refresh(portfolio)

        return db_order





##############################################################################################



    @staticmethod
    def create_sell_order(user_id: int, symbol: str, quantity: float, db: Session):
        # Step 1: Fetch user and portfolio
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Step 2: Fetch the current market price of the asset
        current_price = MarketDataService.get_market_data(symbol)

        # Step 3: Fetch the asset from the portfolio
        asset = db.query(Asset).filter(Asset.portfolio_id == portfolio.id, Asset.symbol == symbol).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found in portfolio")

        # Step 4: Check if the quantity to sell is valid
        if quantity > asset.quantity:
            raise HTTPException(status_code=400, detail="Insufficient quantity to sell")

        # Step 5: Calculate total revenue from the sale
        total_revenue = current_price * quantity

        # Step 6: Calculate profit/loss based on the position type
        if asset.position_type == "long":
            # For long positions, profit/loss is calculated against the average price bought
            profit_loss = (current_price - asset.price_bought) * quantity
        elif asset.position_type == "short":
            # For short positions, profit/loss is calculated in reverse
            profit_loss = (asset.price_bought - current_price) * quantity
        else:
            raise HTTPException(status_code=400, detail="Invalid order position type")

        # Step 7: Update portfolio balance
        portfolio.balance += total_revenue + profit_loss

        # Step 8: Update the asset quantity
        asset.quantity -= quantity
        if asset.quantity == 0:
            db.delete(asset)  # Remove asset if quantity is zero

        # Step 9: Create a new order
        db_order = Order(
            symbol=symbol,
            quantity=quantity,
            price=current_price,
            order_type="sell",  # Fixed as 'sell' since this is a sell order
            order_position_type=asset.position_type,  # Use the existing position type
            executed_at=datetime.utcnow(),
            user_id=user_id
        )

        # Step 10: Record the transaction
        transaction = Transaction(
            symbol=symbol,
            quantity=quantity,
            price=current_price,
            total=total_revenue,
            transaction_type="sell",
            position_type=asset.position_type, # Use the existing position type
            user_id=user_id
        )

        # Step 11: Commit changes to the database
        db.add(db_order)
        db.add(transaction)
        db.commit()
        db.refresh(db_order)
        db.refresh(portfolio)

        return db_order
