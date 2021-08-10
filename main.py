from pathlib import Path
from typing import List

import pandas as pd

from strategies.ppb import extract
from utils import list_directory, to_currency
from utils.consts import LOCAL_DATASETS_DIR, LOCAL_DIR
from utils.pages import check_page_orientation


def summary(assets_total: int, liabilities_total: int, profit_total: int, loss_total: int) -> None:
    """
    Returns the summary of a balance sheet
    """

    print("Activo:", to_currency(assets_total, "PYG"))
    print("Pasivo y Patrimonio:", to_currency(liabilities_total, "PYG"))
    print("Perdidas:", to_currency(profit_total, "PYG"))
    print("Ganancias:", to_currency(loss_total, "PYG"))


def validate_files(directory: Path) -> List[Path]:
    # [TODO] improve page orientation detection
    exclude_files: List[str] = [
        "2015_12.pdf",  # -> not landscape
        "2016_12.pdf",  # -> not landscape, not opening fixed file
        "2017_12.pdf",  # -> not landscape
        "2018_01.pdf",  # -> cannot extract text
        "2018_02.pdf",  # -> cannot extract text
        "2018_05.pdf",  # -> failed extract_tables strategy
        "2018_06.pdf",  # -> failed extract_tables strategy
        "2018_09.pdf",  # -> failed extract_tables strategy
        "2018_11.pdf",  # -> failed extract_tables strategy
        "2018_12.pdf",  # -> failed extract_tables strategy
        "2019_09.pdf",  # -> failed extract_tables strategy
        "2019_11.pdf",  # -> failed extract_tables strategy
        "2020_09.pdf",  # -> cannot extract text
    ]

    dec_2015 = LOCAL_DIR / "2015_12.pdf"
    dec_2017 = LOCAL_DIR / "2017_12.pdf"
    false_positives = [dec_2015, dec_2017]

    valid_files: List[Path] = []

    for f in list_directory(directory):
        if f.name in exclude_files:
            continue

        valid = check_page_orientation(f, directory)
        valid_files.append(valid)

    valid_files.extend(false_positives)

    return valid_files


def main() -> None:
    files = validate_files(LOCAL_DIR)
    assets_concat_list = []
    liabilities_concat_list = []
    loss_concat_list = []
    profit_concat_list = []

    for i, file in enumerate(files, start=1):
        assets_df, liabilities_df, loss_df, profit_df = extract(file)

        assets_concat_list.append(assets_df)
        liabilities_concat_list.append(liabilities_df)
        loss_concat_list.append(loss_df)
        profit_concat_list.append(profit_df)
        print(f"{i} - {file.name} done...")

    print("All files parsed, creating DataFrames...")
    final_assets = pd.concat(assets_concat_list).sort_index()
    final_liabilities = pd.concat(liabilities_concat_list).sort_index()
    final_loss = pd.concat(loss_concat_list).sort_index()
    final_profit = pd.concat(profit_concat_list).sort_index()

    final_assets.to_csv(LOCAL_DATASETS_DIR / "assets.csv")
    final_liabilities.to_csv(LOCAL_DATASETS_DIR / "liabilities.csv")
    final_profit.to_csv(LOCAL_DATASETS_DIR / "profit.csv")
    final_loss.to_csv(LOCAL_DATASETS_DIR / "loss.csv")
    print("All tasks done!")


if __name__ == "__main__":
    main()
