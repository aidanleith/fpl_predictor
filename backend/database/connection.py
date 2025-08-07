import mysql.connector
from mysql.connector import Error, pooling
from shared.dbConnectionConfig import dbConnect

'''
Class to establish a connection pool for api use.
'''
class connection:
    
    #class variable shared across all instances, singleton
    pool = None
    
    def __init__(self):
        self.config = dbConnect()
        #create pool only once 
        if connection.pool is None:
            self._create_pool()

    def _create_pool(self):
        """Create the connection pool - called only once"""
        try:
            connection.pool = pooling.MySQLConnectionPool(
                pool_name="fpl_pool",
                pool_size=10,  #maximum 10 connections in pool
                pool_reset_session=True,  #reset session variables when connection returned
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                host=self.config.host,
                port=self.config.port,
                autocommit=False  #manual commit control
            )
            print(f"Connection pool created successfully with {connection.pool.pool_size} connections")
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise e

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return connection.pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            raise e

    def execute_query(self, query, params=None, fetch_results=True):
        """
        Execute a query using connection from pool
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query
            fetch_results (bool): Whether to fetch and return results
            
        Returns:
            list: Query results (if fetch_results=True)
            int: Number of affected rows (if fetch_results=False)
        """
        conn = None
        cursor = None
        try:
            #get connection from pool
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)  #return results as dictionaries
            
            #execute query
            cursor.execute(query, params or ())
            
            if fetch_results:
                #for SELECT queries
                results = cursor.fetchall()
                return results
            else:
                #for INSERT, UPDATE, DELETE queries
                conn.commit()
                return cursor.rowcount
                
        except Error as e:
            if conn:
                conn.rollback()  #rollback on error
            print(f"Database error: {e}")
            raise e
        finally:
            #always close cursor and return connection to pool
            if cursor:
                cursor.close()
            if conn:
                conn.close()  #this returns connection to pool, doesn't actually close it

    def execute_many(self, query, params_list):
        """
        Execute the same query multiple times with different parameters
        Useful for bulk inserts/updates. Params_list elements should be in order corresponding to each SQL query.
        
        Args:
            query (str): SQL query to execute
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of affected rows
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
            
        except Error as e:
            if conn:
                conn.rollback()
            print(f"Database error in executemany: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    