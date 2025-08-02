import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "kanji_learning.db"

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def register_user(username, password):
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, password_hash, created_at, total_score) VALUES (?, ?, ?, 0)", (username, hashed, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def delete_user(username):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    #cur.execute("DELETE FROM history WHERE user_id=?", (username,)) history.user_id は ON DELETE CASCADE 指定済
    cur.execute("DELETE FROM users WHERE user_id=?", (username,))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE user_id = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row and verify_password(password, row[0]):
        return True
    return False
    
def exist_user(username):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM users WHERE user_id=?)", (username,))
    is_exist = (cur.fetchone()[0] == 1)
    conn.close()
    return is_exist

def update_total_score(user_id, score):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("UPDATE users SET total_score = total_score + ? WHERE user_id = ?", (score, user_id))
    conn.commit()
    conn.close()