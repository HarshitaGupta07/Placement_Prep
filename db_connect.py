import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

# Initialize variables
client = None
db = None
users_collection = None
sessions_collection = None

# If URI exists, try to connect
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        
        # Database Name (Exact match from your screenshot)
        db = client['AI_Interviewer_DB'] 
        
        # User Data Collection
        users_collection = db['users'] 
        
        # Interview & Test History Collection (Capital 'S' fixed)
        sessions_collection = db['Sessions'] 
        
        print("MongoDB Connected Successfully!")
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
else:
    print("Warning: MONGO_URI not found in .env file.")