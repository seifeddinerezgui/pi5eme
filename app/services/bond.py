from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models
from app.models import Bond
from app.models.portfolio import Portfolio
from app.schemas.bond import BondCreate

import yfinance as yf
import numpy as np



#cv
def add_bond(db: Session, bond_data: BondCreate):
    new_bond = Bond(
        face_value=bond_data.face_value,
        coupon_rate=bond_data.coupon_rate,
        market_rate=bond_data.market_rate,
        maturity=bond_data.maturity,
        payment_frequency=bond_data.payment_frequency,
    )
    db.add(new_bond)
    db.commit()
    db.refresh(new_bond)  
    return new_bond

#cv
def calculate_bond_price(db: Session,id :int):
  
    bond = db.query(Bond).filter(Bond.bond_id ==id).first()
    periods = bond.maturity * bond.payment_frequency
    coupon = bond.face_value * bond.coupon_rate / bond.payment_frequency
    discount_rate = bond.market_rate / bond.payment_frequency
    
    # Prix de l'obligation
    price = sum(coupon / (1 + discount_rate) ** t for t in range(1, periods + 1))
    price += bond.face_value / (1 + discount_rate) ** periods

    # Calcul de la durée de Macaulay
    macaulay_duration = sum(t * coupon / (1 + discount_rate) ** t for t in range(1, periods + 1))
    macaulay_duration += periods * (bond.face_value / (1 + discount_rate) ** periods)
    macaulay_duration /= price

    # Durée modifiée
    modified_duration = macaulay_duration / (1 + discount_rate)
    
    return {"price": price, "modified_duration": modified_duration, "coupon":coupon, "periode":periods}

#cv
def simulate_portfolio_with_bond(db: Session, user_id: int, bond_id: int):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()
    bond = db.query(models.Bond).filter(models.Bond.bond_id == bond_id).first()
    if portfolio is None or bond is None:
        raise HTTPException(status_code=404, detail="Portfolio or Bond not found")
    
    bond_price_value=bond_price1(bond)
    portfolio.balance -= bond_price_value  # Deduct the bond price from portfolio balance
    bond.user_id=user_id
    db.commit()
    return {"portfolio_balance": portfolio.balance, "bond_price": bond_price_value}

#cv
def bond_price1(bond: Bond):
    coupon_payment = bond.face_value * bond.coupon_rate / bond.payment_frequency
    price = 0
    for t in range(1, bond.maturity * bond.payment_frequency + 1):
        price += coupon_payment / (1 + bond.market_rate / bond.payment_frequency) ** t
    price += bond.face_value / (1 + bond.market_rate / bond.payment_frequency) ** (bond.maturity * bond.payment_frequency)
    return price

#cv
def bond_price(face_value: float, coupon_rate: float, market_rate: float, maturity: int, payment_frequency: int):
    coupon_payment = face_value * coupon_rate / payment_frequency
    price = 0
    for t in range(1, maturity * payment_frequency + 1):
        price += coupon_payment / (1 + market_rate / payment_frequency) ** t
    price += face_value / (1 + market_rate / payment_frequency) ** (maturity * payment_frequency)
    return price

#Nrmln labes
def portfolio_risk_analysis(db: Session, user_id: int):
    # Récupérer le portefeuille de l'utilisateur
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Récupérer tous les actifs liés à ce portefeuille
    assets = db.query(models.Asset).filter(models.Asset.portfolio_id == portfolio.id).all()
    market_rate_change = get_market_rate_change("^GSPC", "2024-11-01", "2024-11-23")

    # Calculer le risque lié aux actions détenues dans le portefeuille
    total_risk = 0
    for asset in assets:
        # Récupérer le bêta pour l'action
        beta = calculate_beta(asset.symbol, "^GSPC", "2024-01-01", "2024-11-23")  # Exemple avec S&P 500

        # Calculer le risque pour cette action
        asset_risk = beta * market_rate_change * asset.quantity

        # Ajouter le risque pour cet actif au total
        total_risk += asset_risk

    return {"total_risk": total_risk}

#cv
def get_market_rate_change(market_index, start_date, end_date):
    market_data = yf.download(market_index, start=start_date, end=end_date) 
    market_returns = market_data['Adj Close'].pct_change().dropna()
    return market_returns.iloc[-1]  # Dernier rendement calculé

#cv
def calculate_beta(stock_ticker: str, market_ticker: str, start_date: str, end_date: str) -> float:
    # Télécharger les données historiques des prix
    stock_data = yf.download(stock_ticker, start=start_date, end=end_date)
    market_data = yf.download(market_ticker, start=start_date, end=end_date)

    # Vérifier si les données ont bien été récupérées
    if stock_data.empty or market_data.empty:
        raise ValueError(f"Data not available for {stock_ticker} or {market_ticker}.")

    # Calcul des rendements quotidiens
    stock_returns = stock_data['Adj Close'].pct_change().dropna()
    market_returns = market_data['Adj Close'].pct_change().dropna()

    # Synchroniser les index pour s'assurer qu'ils correspondent
    common_index = stock_returns.index.intersection(market_returns.index)
    stock_returns = stock_returns.loc[common_index]
    market_returns = market_returns.loc[common_index]

    # Calcul de la covariance et de la variance
    covariance_matrix = np.cov(stock_returns, market_returns)
    covariance = covariance_matrix[0, 1]  # Covariance entre l'action et le marché
    market_variance = covariance_matrix[1, 1]  # Variance du marché

    # Calcul du bêta
    beta = covariance / market_variance
    return beta


# aamla ro7ha cv 
def calculate_zero_coupon_bonds_for_coverage(db: Session, user_id: int):
    # Calculate the portfolio risk
    risk = portfolio_risk_analysis(db, user_id)
    
    # Extract the total risk value from the returned dictionary
    total_risk = risk['total_risk']

    # Retrieve all bonds with user_id == NULL (no user assigned to the bond)
    bonds = db.query(models.Bond).filter(models.Bond.user_id == None).all()

    # Check if any bonds are found
    if not bonds:
        raise HTTPException(status_code=404, detail="No bonds found with user_id == NULL")

    required_bonds_list = []

    # Calculate the number of bonds required to cover the risk
    for bond in bonds:
        # Calculate bond price using your existing bond_price1 function
        bond_price = bond_price1(bond)

        # Check if the bond price is valid
        if bond_price <= 0:
            continue
        
        # Calculate the required number of bonds
        required_bonds = total_risk / bond_price
        required_bonds_list.append({
            'bond_id': bond.bond_id,
           # 'required_bonds': required_bonds,
            'bond_price': bond_price
        })

    return {"required_bonds": required_bonds_list}


#a voir
def suggested_bonds_for_coverage(db: Session, user_id: int):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    risk = portfolio_risk_analysis(db, user_id)  # Assumer un changement de taux de 0 pour obtenir le risque
    required_bonds = calculate_zero_coupon_bonds_for_coverage(db, user_id)
    return {"suggested_bonds": required_bonds["required_bonds"]}
