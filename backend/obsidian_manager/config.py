import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # searches CWD and parents; also explicit fallback:
load_dotenv(Path.cwd() / ".env", override=False)

_vault_str = os.getenv("VAULT_PATH", "")
VAULT_PATH = Path(_vault_str).expanduser() if _vault_str else None
DB_PATH = Path(os.getenv("DB_PATH", "obsidian.db")).expanduser()
PORT = int(os.getenv("PORT", "8000"))
DATA_DIR = Path(os.getenv("DATA_DIR", "~/.obsidian-manager")).expanduser()
