from backend.database.connection import connection

class playerServices():

    def __init__(self):
        self.db = connection()

    def playerSearch(self, name):
        query = """
        SELECT id, first_name, last_name FROM players
        """