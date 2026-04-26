import bcrypt
from db import c, conn

def create_user(u, p):
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (u, hashed))
        conn.commit()
        return True
    except:
        return False

def login_user(u, p):
    c.execute("SELECT password FROM users WHERE username=?", (u,))
    data = c.fetchone()
    if data and bcrypt.checkpw(p.encode(), data[0]):
        return True
    return False