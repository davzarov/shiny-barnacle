from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "balance_sheets" / "continental"
DATASETS_DIR = BASE_DIR / "datasets"
# local currency directories
LOCAL_DIR = FILES_DIR / "local"
LOCAL_DONE_DIR = FILES_DIR / "local_done"
LOCAL_DATASETS_DIR = DATASETS_DIR / "local"
# foreign currency directories
FOREIGN_DIR = FILES_DIR / "foreign"
FOREIGN_DONE_DIR = FILES_DIR / "foreign_done"
FOREIGN_DATASETS_DIR = DATASETS_DIR / "foreign"
