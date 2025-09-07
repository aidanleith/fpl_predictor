import os
from dotenv import load_dotenv

load_dotenv()

class dbConnect:

    def __init__(self):
        # Try Railway variables first, fall back to local .env variables
        self.host = os.getenv('MYSQLHOST') or os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306))
        self.database = os.getenv('MYSQL_DATABASE') or os.getenv('DB_DATABASE')
        self.username = os.getenv('MYSQLUSER') or os.getenv('DB_USERNAME')
        self.password = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD')
        
        # Debug logging - remove this after fixing
        print(f"DB Config - Host: {self.host}, Port: {self.port}, DB: {self.database}")
        print(f"MYSQLHOST env var: {os.getenv('MYSQLHOST')}")
        print(f"DB_HOST env var: {os.getenv('DB_HOST')}")