import os
import pickle

WALLETS_FILE = "user_wallets.pkl"

def load_wallets():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}

def save_wallet(user_id: int, wallet_type: str, address: str):
    data = load_wallets()
    if user_id not in data:
        data[user_id] = {}
    data[user_id][wallet_type] = address
    with open(WALLETS_FILE, "wb") as f:
        pickle.dump(data, f)

def get_wallet(user_id: int, wallet_type: str) -> str:
    data = load_wallets()
    return data.get(user_id, {}).get(wallet_type, "not specified")