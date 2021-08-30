from pathlib import Path
from typing import List

import pandas as pd

from settings.conf import LOCAL_DATASETS_DIR, LOCAL_DIR, blacklisted
from strategies.ppb import extract
from utils import list_directory
from utils.pages import check_page_orientation


def validate_files(directory: Path) -> List[Path]:
    valid_files: List[Path] = []
    for f in list_directory(directory):
        if f.name in blacklisted:
            continue

        valid = check_page_orientation(f, directory)
        valid_files.append(valid)

    return valid_files


def main() -> None:
    files = validate_files(LOCAL_DIR)
    files_len = len(files)
    assets_list = []
    liabs_list = []
    loss_list = []
    profit_list = []

    for i, file in enumerate(files, start=1):
        print(f"[INFO]: attempting {file.name}")
        dfs = extract(file)

        assets_list.append(dfs[0])
        liabs_list.append(dfs[1])
        loss_list.append(dfs[2])
        profit_list.append(dfs[3])

        print(f"[OK]: {i}/{files_len} - {file.name} done...")

    print("[INFO]: All files parsed, creating DataFrames...")
    assets = pd.concat(assets_list).sort_index()
    liabs = pd.concat(liabs_list).sort_index()
    loss = pd.concat(loss_list).sort_index()
    profit = pd.concat(profit_list).sort_index()

    assets.to_csv(LOCAL_DATASETS_DIR / "assets.csv")
    liabs.to_csv(LOCAL_DATASETS_DIR / "liabilities.csv")
    profit.to_csv(LOCAL_DATASETS_DIR / "profit.csv")
    loss.to_csv(LOCAL_DATASETS_DIR / "loss.csv")
    print("[END]: All tasks done!")


if __name__ == "__main__":
    main()
