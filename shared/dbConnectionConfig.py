import os
from dotenv import load_dotenv

load_dotenv()

class dbConnect:

    def __init__(self):
        # Try Railway variables first, fall back to local .env variables
        self.host = os.getenv('MYSQLHOST') or os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306))
        self.database = os.getenv('MYSQL_DATABASE') or os.getenv('DB_NAME')
        self.username = os.getenv('MYSQLUSER') or os.getenv('DB_USER')
        self.password = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD')
    