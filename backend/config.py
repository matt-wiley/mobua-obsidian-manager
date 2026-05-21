import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

VAULT_PATH = Path(os.environ["VAULT_PATH"]).expanduser()
DB_PATH = Path(os.getenv("DB_PATH", "obsidian.db")).expanduser()
PORT = int(os.getenv("PORT", "8000"))
