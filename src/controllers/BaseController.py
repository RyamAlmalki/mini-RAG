from helper.config import get_settings, Settings
import os 
import random
import string

class BaseController:
    def __init__(self):
        self.app_settings: Settings = get_settings()
        
        # __file__ = src/controllers/BaseController.py
        # os.path.dirname(__file__) = src/controllers
        # os.path.dirname(os.path.dirname(__file__)) = src
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )

        self.files_dir = os.path.join(self.base_dir, "assets/files")

        self.databse_dir = os.path.join(self.base_dir, "assets/database")


    def generate_random_string(self, length: int = 10) -> str:
        """Generate a random string of fixed length."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))
    
    
    def get_database_path(self, database_name:str) -> str:
        
        database_path = os.path.join(self.databse_dir, database_name)

        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        return database_path