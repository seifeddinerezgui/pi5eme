# app/services/portfolio_management.py

from sqlalchemy.orm import Session
from app.models import Portfolio, Asset, Transaction


def get_portfolio(db: Session, user_id: int):
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

def update_balance(db: Session, user_id: int, amount: float):
    portfolio = get_portfolio(db, user_id)
    portfolio.balance += amount
    db.commit()
    db.refresh(portfolio)
    return portfolio


def update_portfolio(transaction: Transaction, db: Session):
    # Find the buyer's portfolio
    buyer_portfolio = db.query(Portfolio).filter(Portfolio.user_id == transaction.user_id).first()

    # Update asset quantity in buyer's portfolio
    asset = db.query(Asset).filter(
        Asset.portfolio_id == buyer_portfolio.id,
        Asset.symbol == transaction.symbol
    ).first()

    if transaction.transaction_type == "buy":
        if asset:
            asset.quantity += transaction.quantity
        else:
            new_asset = Asset(
                symbol=transaction.symbol,
                quantity=transaction.quantity,
                price_bought=transaction.price,
                portfolio_id=buyer_portfolio.id
            )
            db.add(new_asset)
        buyer_portfolio.balance -= transaction.total

    elif transaction.transaction_type == "sell":
        if asset and asset.quantity >= transaction.quantity:
            asset.quantity -= transaction.quantity
            if asset.quantity == 0:
                db.delete(asset)
            buyer_portfolio.balance += transaction.total

    db.commit()
