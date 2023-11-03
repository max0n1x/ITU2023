from sqlite3 import connect, Error
from src.config import DATABASE_FILE
from src.crypto import Crypto
from src.models import Optional
import os


class Database:

    def __init__(self) -> None:
        """ create a database connection to a SQLite database """
        try:

            self.conn = connect(
                os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'), DATABASE_FILE))

            self.conn.execute('''CREATE TABLE IF NOT EXISTS items (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT,
                            price REAL NOT NULL,
                            contact_email TEXT,
                            contact_phone TEXT,
                            image_path TEXT,
                            author_id INTEGER NOT NULL);
            ''')

            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            encrypted_password TEXT NOT NULL,
                            key TEXT NOT NULL);
            ''')

            self.conn.commit()

        except Error as e:
            print(e)
            exit(1)

    def insert_item(self, **item) -> bool:
        """ insert a new item into the items table """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            INSERT INTO items (name, description, price, contact_email, contact_phone, image_path)
            VALUES (:name, :description, :price, :contact_email, :contact_phone, :image_path)
            ''', item)

            self.conn.commit()

            return True
        
        except Error as e:

            print(e)
            return False

    def get_items(self) -> list:
        """ get all items from the items table """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            SELECT * FROM items
            ''')

            rows = cursor.fetchall()
            keys = ('id', 'name', 'description', 'price', 'contact_email', 'contact_phone', 'image_path')

            return [{key: value for key, value in zip(keys, row)} for row in rows]
        
        except Error as e:

            print(e)
            return []

    def get_item(self, item_id: int) -> dict:
        """ get a single item from the items table """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            SELECT * FROM items WHERE id = :id
            ''', {'id': item_id})

            row = cursor.fetchone()
            keys = ('id', 'name', 'description', 'price', 'contact_email', 'contact_phone', 'image_path')

            return {key: value for key, value in zip(keys, row)} if row else {}
        
        except Error as e:

            print(e)
            return {}

    def delete_item(self, item_id: int) -> bool:
        """ delete a single item from the items table """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            DELETE FROM items WHERE id = :id
            ''', {'id': item_id})

            self.conn.commit()

            return True
        
        except Error as e:

            print(e)
            return False

    def update_item(self, item_id: int, **item) -> bool:
        """ update a single item from the items table """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            UPDATE items SET name = :name, description = :description, price = :price, contact_email = :contact_email,
            contact_phone = :contact_phone, image_path = :image_path WHERE id = :id
            ''', {'id': item_id, **item})

            self.conn.commit()

            return True
        
        except Error as e:

            print(e)
            return False
        
    def register_user(self, **user) -> int:
        """ register a new user if username is not taken """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            SELECT * FROM users WHERE username = :username
            ''', {'username': user['username']})

            row = cursor.fetchone()

            if row:
                return -1
            
            crypto = Crypto()
            encrypted = crypto.encrypt(user['password'])

            cursor.execute('''
            INSERT INTO users (username, encrypted_password, key)
            VALUES (:username, :encrypted_password, :key)
            ''', {'username': user['username'], **encrypted})

            self.conn.commit()

            return 0
        
        except Error as e:

            print(e)
            return -2
        
    def login_user(self, **user) -> int:
        """ login a user and return user id """
        try:

            cursor = self.conn.cursor()

            cursor.execute('''
            SELECT * FROM users WHERE username = :username
            ''', {'username': user['username']})

            row = cursor.fetchone()

            if row:

                crypto = Crypto()
                decrypted = crypto.decrypt(row[2], row[3])

                if decrypted == user['password']:
                    return row[0]
                
            return -1
        except Error as e:

            print(e)
            return -2
        
    # def update_user(self, user_id : int, **user) -> bool:
    #     """ update a single user if correct password is provided, if new password is provided, it will be encrypted and old password checked to be correct before iupdate"""

        
    # def get_user(self, user_id : int) -> dict:
    #     """ get a single user from the users table """
    #     try:
    #         cursor = self.conn.cursor()
    #         cursor.execute('''
    #         SELECT * FROM users WHERE id = :id
    #         ''', {'id': user_id})
    #         row = cursor.fetchone()
    #         keys = ('id', 'username', 'password')
    #         return {key: value for key, value in zip(keys, row)} if row else {}
    #     except Error as e:
    #         print(e)
    #         return {}


    def __del__(self) -> None:
        """ close the database connection """
        self.conn.close()
