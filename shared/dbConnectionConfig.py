import os
from dotenv import load_dotenv

load_dotenv()

class dbConnect:

    def __init__(self):
        self.host = os.getenv('MYSQLHOST')
        self.port = int(os.getenv('MYSQLPORT', 3306))  # Default port if not set
        self.database = os.getenv('MYSQL_DATABASE')
        self.username = os.getenv('MYSQLUSER')
        self.password = os.getenv('MYSQLPASSWORD')