import os, json, hashlib
from . import misc

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache_json")

os.makedirs(CACHE_DIR, exist_ok=True)

def load_cache(key):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    # misc.log_print(key, path)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(key, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    # misc.log_print(key, path, data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
def md5_hash(text: str) -> str:
    """
    Return the MD5 hex digest of the given text.
    """
    # ensure we’re hashing bytes
    data = text.encode('utf-8')
    # compute MD5 and return as hex string
    return hashlib.md5(data).hexdigest()