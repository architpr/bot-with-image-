import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")
if not GOOGLE_API_KEY:
    # Not raising error strictly if we don't use it, but for this hybrid plan we need it.
    pass

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
ASSETS_DIR = os.path.join(DATA_DIR, "assets")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
