from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / 'balance_sheets' / "continental"
LOCAL_CURRENCY_DIR = FILES_DIR / "local"
FOREIGN_CURRENCY_DIR = FILES_DIR / "foreign"
