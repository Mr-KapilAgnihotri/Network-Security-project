from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 1. Load variables from the .env file
load_dotenv()

USERNAME = os.getenv("MONGO_DB_USERNAME")
PASSWORD = os.getenv("MONGO_DB_PASSWORD")
CLUSTER_URL = os.getenv("MONGO_DB_CLUSTER_URL")
APP_NAME = os.getenv("MONGO_DB_APP_NAME")

quoted_username = quote_plus(USERNAME)
quoted_password = quote_plus(PASSWORD)
uri = (
    f"mongodb+srv://{quoted_username}:{quoted_password}@{CLUSTER_URL}/"
    f"?appName={APP_NAME}"
)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)