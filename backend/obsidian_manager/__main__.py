import sys
import uvicorn
from .config import PORT


def main():
    uvicorn.run("obsidian_manager.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    main()
