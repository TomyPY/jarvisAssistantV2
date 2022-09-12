from dotenv import load_dotenv
import os
load_dotenv()

TELEGRAM_TOKEN=os.environ.get("API_KEY")
SENDER_EMAIL="updates@streamstop.co"
PASSWORD=os.environ.get("PASSWORD")