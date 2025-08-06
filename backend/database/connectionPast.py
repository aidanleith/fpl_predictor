from shared.dbConnectionConfig import dbConnect
import mysql.connector
from mysql.connector import Error

class connection:
    def __init__(self):
         self.connection = None
         self.cursor = None
         self.config = dbConnect()

    def connect(self):
            try:
                self.connection = mysql.connector.connect(
                    user = self.config.username,
                    password = self.config.password,
                    database = self.config.database,
                    host = self.config.host,
                    port = self.config.port
                )

                if self.connection.is_connected():
                    self.cursor = self.connection.cursor()
                return True

            except Error as e:
                return False
            
    def disconnect(self) -> bool:
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None and self.connection.is_connected():
                self.connection.close()
            return True
        
        except Error as e:
            return False
    
    def getCursor(self):
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                raise Exception("Could not establish database connection")
        return self.cursor
    
    def commit(self):
        if not self.connection:
            print("Not connected")
            return False
        self.connection.commit()