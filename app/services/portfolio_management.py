# app/services/portfolio_management.py
from sqlalchemy.orm import Session

  # Assurez-vous que getData est correctement importée
from datetime import datetime
from app.services.MarketDataService import MarketDataService
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import Portfolio, Asset, Transaction,Order,User
from collections import defaultdict



def get_portfolio(db: Session, user_id: 1):
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



def update_portfolio_balance(db: Session, user_id: int):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        print(f"No portfolio found for user {user_id}")
        return

    total_balance_update = 0

    
    assets = db.query(Asset).filter(Asset.portfolio_id == portfolio.id).all()

    for asset in assets:
        
        stock_info = MarketDataService.get_market_data(asset.symbol)
        
       
        if isinstance(stock_info, float):
            current_price = stock_info
        elif isinstance(stock_info, dict) and 'price' in stock_info:
            current_price = float(stock_info['price'].replace(',', ''))
        else:
            print(f"Erreur : données de prix non disponibles pour {asset.symbol}")
            continue

       
        if asset.position_type == "long":
            profit_loss = (current_price - asset.price_bought) * asset.quantity
        elif asset.position_type == "short":
            profit_loss = (asset.price_bought - current_price) * asset.quantity
        else:
            continue  
        total_balance_update += profit_loss

   
    portfolio.balance += total_balance_update
    db.commit()
    print(f"Balance updated for user {user_id} at {datetime.utcnow()}")



def start_balance_update_scheduler(user_id: int):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: run_balance_update(user_id), 'interval', minutes=8)  # Exécuter toutes les minutes
    scheduler.start()

def run_balance_update(user_id: int):
    db = SessionLocal()
    try:
        update_portfolio_balance(db, user_id)
    finally:
        db.close()

def calculate_asset_percentages(portfolio_id: int, db: Session):
    # Récupérer le portefeuille avec ses actifs
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    
    if not portfolio:
        raise ValueError("Portfolio not found")
    
    total_balance = portfolio.balance
    if total_balance <= 0:
        raise ValueError("Portfolio balance must be greater than zero")
    
    # Regrouper les actifs par symbole
    symbol_totals = defaultdict(float)  # Dictionnaire pour stocker la valeur totale de chaque symbole
    for asset in portfolio.assets:
        asset_value = asset.quantity * asset.price_bought
        symbol_totals[asset.symbol] += asset_value
    
    # Calculer les pourcentages
    asset_percentages = []
    for symbol, total_value in symbol_totals.items():
        percentage = (total_value / total_balance) * 100
        asset_percentages.append({
            "symbol": symbol,
            "percentage": percentage
        })
    
    return asset_percentages
def get_all_user_ranks_by_balance(db: Session):
    # Récupérer les utilisateurs et les soldes de leurs portefeuilles
    users_with_balances = (
        db.query(User.id, User.username, Portfolio.balance)
        .join(Portfolio, User.id == Portfolio.user_id)
        .order_by(Portfolio.balance.desc())  # Trier par balance décroissante
        .all()
    )

    # Générer une liste avec les rangs
    user_ranks = []
    for rank, user in enumerate(users_with_balances, start=1):
        user_ranks.append({
            "rank": rank,
            "username": user.username,
            "balance": user.balance
        })

    return user_ranks