from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    AUTH0_ALGORITHMS = ["RS256"]
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
    AUTH0_IDENTIFIER = os.getenv("AUTH0_IDENTIFIER")