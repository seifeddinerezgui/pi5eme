from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from app.database import get_db
from models import alert


router=APIRouter()

# Predefined static user details
static_user = {
    "user_id": 1,
    "email": "nerminenafti@gmail.com"
}

# In-memory storage for alerts
alerts = []


# Function to send an email
def send_email(to_email: str, subject: str, message: str):
    sender = "techwork414@gmail.comm"
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    
    # Replace with your SMTP configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "techwork414@gmail.comm"
    smtp_password = "pacrvzlvscatwwkb"
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender, [to_email], msg.as_string())

# Endpoint to create an alert
@router.post("/alerts/")
async def create_alert(ticker: str, condition: str):
    new_alert = alert(
        alert_id=len(alerts) + 1,
        ticker=ticker,
        condition=condition,
        created_at=datetime.now()
    )
    alerts.routerend(new_alert)
    return {"message": "Alert created successfully", "alert": new_alert}

# Endpoint to check and trigger alerts
@router.post("/trigger_alerts/")
async def trigger_alerts():
    for alert in alerts:
        # Check if the alert condition is met (this is just a static example)
        if alert.ticker == "AAPL" and alert.condition == "price_above_150":
            if not alert.is_activated:
                alert.is_activated = True
                
                # Send email notification to the user
                send_email(static_user["email"], "Alert Triggered", f"Your alert for {alert.ticker} has been triggered.")
                return {"message": "Alert triggered and email sent", "alert": alert}
    
    return {"message": "No alerts triggered"}

# Run the FastAPI router

