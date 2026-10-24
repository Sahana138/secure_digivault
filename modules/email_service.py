# file: modules/email_service.py


import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# EMAIL CONFIGURATION

load_dotenv()

# Sender credentials loaded from .env for security
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Gmail SMTP configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# CORE EMAIL SENDER

def send_email(receiver_email, subject, body):
    """
    Sends email using Gmail SMTP.
    """

    # Construct MIME email message
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email

    # TLS encrypted SMTP connection
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # required for secure Gmail auth
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, msg.as_string())

# OTP EMAIL

def send_otp_email(receiver_email, otp):

    subject = "Digivault OTP Verification"

    body = f"""
    <html>
    <body style="font-family: Arial; background-color: #f4f6f8; padding: 20px;">
        
        <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; text-align: center;">
            
            <h2 style="color: #2c3e50;">🔐 Digivault Security</h2>

            <p>Your One-Time Password (OTP) is:</p>

            <h1 style="color: #27ae60; letter-spacing: 5px;">
                {otp}
            </h1>

            <p style="color: #e74c3c; font-weight: bold;">
                ⏳ Expires in 1 minutes
            </p>

            <p style="font-size: 12px; color: gray;">
                Do not share this OTP with anyone.
            </p>

        </div>

    </body>
    </html>
    """

    send_email(receiver_email, subject, body)


# SECURITY ALERT EMAIL

def send_security_alert(receiver_email):

    subject = "⚠️ Digivault Security Alert"

    body = """
    <html>
    <body style="font-family: Arial; background-color: #f4f6f8; padding: 20px;">
        
        <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px;">
            
            <h2 style="color: #c0392b; text-align: center;">
                🚨 Security Alert
            </h2>

            <p>
                Your Digivault account has been <b style="color:red;">temporarily locked</b>
                due to multiple failed login attempts.
            </p>

            <p style="color: #e67e22;">
                🔒 Account will unlock automatically after <b>1 minute</b>
            </p>

            <hr>

            <p style="font-size: 14px;">
                If this was not you, someone may be trying to access your vault.
            </p>

            <p style="color: gray; font-size: 12px;">
                Digivault Security System
            </p>

        </div>

    </body>
    </html>
    """

    send_email(receiver_email, subject, body)