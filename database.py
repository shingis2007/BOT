import json
import os
from datetime import datetime

DB_FILE = "data/database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        os.makedirs("data", exist_ok=True)
        default = {
            "users": {},
            "arizalar": [],
            "murojaatlar": [],
            "tadbirlar": [],
            "elanlar": []
        }
        save_db(default)
        return default
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    os.makedirs("data", exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_user(user_id, full_name, username):
    db = load_db()
    db["users"][str(user_id)] = {
        "full_name": full_name,
        "username": username or "",
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_db(db)

def add_ariza(user_id, full_name, text):
    db = load_db()
    db["arizalar"].append({
        "id": len(db["arizalar"]) + 1,
        "user_id": user_id,
        "full_name": full_name,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "yangi"
    })
    save_db(db)

def add_murojaat(user_id, full_name, text):
    db = load_db()
    db["murojaatlar"].append({
        "id": len(db["murojaatlar"]) + 1,
        "user_id": user_id,
        "full_name": full_name,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "yangi"
    })
    save_db(db)

def add_tadbir(nomi, sana, joy, tavsif):
    db = load_db()
    db["tadbirlar"].append({
        "id": len(db["tadbirlar"]) + 1,
        "nomi": nomi,
        "sana": sana,
        "joy": joy,
        "tavsif": tavsif
    })
    save_db(db)

def get_tadbirlar():
    db = load_db()
    return db["tadbirlar"]

def get_arizalar():
    db = load_db()
    return db["arizalar"]

def get_murojaatlar():
    db = load_db()
    return db["murojaatlar"]

def get_all_users():
    db = load_db()
    return db["users"]
