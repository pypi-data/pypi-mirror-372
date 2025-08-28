import hashlib
import sqlite3

class AuthManager:
    def __init__(self):
        conn = sqlite3.connect('webloop.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        conn = sqlite3.connect('webloop.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, self.hash_password(password)))
        conn.commit()
        conn.close()

    def authenticate(self, username, password):
        conn = sqlite3.connect('webloop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, self.hash_password(password)))
        user = c.fetchone()
        conn.close()
        return user is not None
