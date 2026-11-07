## Testing email sending functionality using Gmail SMTP server
import os
import smtplib
import ssl
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables explicitly
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

username = os.getenv("Email")
password = os.getenv("Password")

if not username or not password:
    raise ValueError("SMTP credentials are missing")

# Remove spaces sometimes displayed in Google App Passwords
password = password.replace(" ", "")

try:
    print("Connecting to Gmail SMTP...")

    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=20
    ) as server:

        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()

        print("TLS connection established.")

        server.login(username, password)

        print("Gmail SMTP authentication successful!")

except smtplib.SMTPAuthenticationError as e:
    print("Authentication failed:", e.smtp_code, e.smtp_error)

except smtplib.SMTPException as e:
    print("SMTP error:", type(e).__name__, str(e))

except Exception as e:
    print("Unexpected error:", type(e).__name__, str(e))
