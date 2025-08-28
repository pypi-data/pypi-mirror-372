from os import environ
from lins_log import lins_log

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

LOG_ENV = environ.get('POMPEIA_ENV', 'SANDBOX')

LOGGING = None
LOGGING_CONFIG = None

CLIENT_ID =  environ.get("PIX_CLIENT_ID")
CLIENT_SECRET =  environ.get("PIX_CLIENT_SECRET")

CERT_PATH =  environ.get("PIX_CERT_PATH")
CERT_TEXT = environ.get("PIX_CERT_TEXT")

PRIVATE_KEY_PATH =  environ.get("PIX_PRIVATE_KEY_PATH")
PRIVATE_KEY_TEXT =  environ.get("PIX_PRIVATE_KEY_TEXT")

VERIFY =  environ.get("PIX_VERIFY", True)
URL =  environ.get("PIX_URL")

CERT = (CERT_PATH, PRIVATE_KEY_PATH)
