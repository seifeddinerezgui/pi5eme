import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import HistoricalScenario, HistoricalTrade, HistoricalData, ExpertTrade

def populate_database():
    db: Session = SessionLocal()

    # Clear the database tables
    db.query(HistoricalTrade).delete()
    db.query(HistoricalData).delete()
    db.query(ExpertTrade).delete()
    db.query(HistoricalScenario).delete()
    db.commit()

    # Create 3 scenarios
    scenarios = [
        HistoricalScenario(
            name="2008 Financial Crisis",
            symbol="AAPL",
            start_date=datetime(2008, 9, 15),
            end_date=datetime(2009, 3, 15),
            additional_info={"description": "Lehman Brothers collapse and aftermath."}
        ),
        HistoricalScenario(
            name="COVID-19 Market Crash",
            symbol="TSLA",
            start_date=datetime(2020, 2, 20),
            end_date=datetime(2020, 6, 20),
            additional_info={"description": "Market crash due to COVID-19 pandemic."}
        ),
        HistoricalScenario(
            name="Dot-com Bubble Burst",
            symbol="AMZN",
            start_date=datetime(2000, 3, 10),
            end_date=datetime(2002, 10, 10),
            additional_info={"description": "Dot-com bubble burst and market effects."}
        )
    ]
    db.add_all(scenarios)
    db.commit()

    # Create 50 expert trades for each scenario
    for scenario in scenarios:
        for _ in range(50):
            trade_date = scenario.start_date + timedelta(days=random.randint(0, (scenario.end_date - scenario.start_date).days))
            trade = ExpertTrade(
                symbol=scenario.symbol,
                action=random.choice(["buy", "sell"]),
                price=round(random.uniform(50, 300), 2),
                timestamp=trade_date,
                scenario_id=scenario.id
            )
            db.add(trade)
    db.commit()

    # Create 10 user trades for each scenario
    for scenario in scenarios:
        for _ in range(10):
            trade_date = scenario.start_date + timedelta(days=random.randint(0, (scenario.end_date - scenario.start_date).days))
            trade = HistoricalTrade(
                symbol=scenario.symbol,
                action=random.choice(["buy", "sell"]),
                price=round(random.uniform(50, 300), 2),
                quantity=random.randint(1, 10),
                timestamp=trade_date,
                scenario_id=scenario.id,
                user_id=1  # Assuming a single test user with ID 1
            )
            db.add(trade)
    db.commit()

    # Generate historical data for each scenario
    for scenario in scenarios:
        current_date = scenario.start_date
        while current_date <= scenario.end_date:
            data = HistoricalData(
                scenario_id=scenario.id,
                timestamp=current_date,
                open=round(random.uniform(50, 300), 2),
                close=round(random.uniform(50, 300), 2),
                high=round(random.uniform(50, 300), 2),
                low=round(random.uniform(50, 300), 2),
                volume=random.randint(1000, 1000000)
            )
            db.add(data)
            current_date += timedelta(days=1)
    db.commit()

    db.close()
    print("Database populated successfully!")

if __name__ == "__main__":
    populate_database()
