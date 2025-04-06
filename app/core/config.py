import os

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret
from databases import DatabaseURL

API_V1_STR = "/api"

ALEX_URL = "https://localhost:5001"
# ALEX_URL = "https://demo002.alexrental.app"


ECOUPON_FILE_PATH = "assets/images/user/"

class SMS_API:
    SMS_URL =  "https://portal-otp.smsmkt.com/api/send-message" 
    API_KEY="781b3afd78120ac6bd6d06b96259d8e6"
    SECRET_KEY="pS9eEK0QHCTFYgZi"
    SENDER = "WTG-Demo"
    COUPON_URL = "https://wtg.promo/c/"
   

class AlexEmail:
    MAIL_USERNAME="v.blue.front1@gmail.com"
    MAIL_PASSWORD="Lll3ell-1234%"
    MAIL_FROM="v.blue.front1@gmail.com"
    MAIL_PORT=587
    MAIL_SERVER="smtp.gmail.com"
    MAIL_FROM_NAME="Alex support"


JWT_TOKEN_PREFIX = "Token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

ACCESS_TOKEN_EXPIRE_HOURS = 12 

MAX_FILE_SIZE = 1024

load_dotenv(".env")

MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "secret key for project"))

PROJECT_NAME = os.getenv("PROJECT_NAME", "FastAPI example application")
ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))

MONGODB_URL = os.getenv("MONGODB_URL", "")  # deploying without docker-compose
if not MONGODB_URL:
    MONGO_HOST = os.getenv("MONGO_HOST", "165.22.98.55")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER", "ecoupon_admin")
    MONGO_PASS = os.getenv("MONGO_PASSWORD", "eCoupon#Passw0rd#987=")
    MONGO_DB = os.getenv("MONGO_DB", "ecouponv1")

    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    )
else:
    MONGODB_URL = DatabaseURL(MONGODB_URL)

database_name = MONGO_DB
article_collection_name = "articles"
favorites_collection_name = "favorites"
tags_collection_name = "tags"
users_collection_name = "users"
comments_collection_name = "commentaries"
followers_collection_name = "followers"
