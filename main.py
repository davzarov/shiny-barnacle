from datetime import datetime
from pathlib import Path
from strategies.default import extract
from typing import List

import numpy as np
import pandas as pd

from consts import (LOCAL_DATASETS_DIR, LOCAL_DIR, assets_dict, equity_dict,
                    exercise_dict, liabilities_dict, loss_dict, profit_dict)
from utils import list_directory, to_currency
from utils.pages import check_page_orientation


def assets_df(assets_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns assets dataframe parsed from table
    """

    assets_array = np.array(assets_list).reshape(1, -1)
    assets_df = pd.DataFrame(assets_array,
                             index=[balance_date],
                             columns=assets_dict["cols"])
    assets_df['Total Activo'] = assets_df.sum(axis=1)

    return assets_df


def liabilities_df(liabilities_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns liabilities dataframe parsed from table
    """

    liabilities_array = np.array(liabilities_list).reshape(1, -1)
    liabilities_df = pd.DataFrame(liabilities_array,
                                  index=[balance_date],
                                  columns=liabilities_dict["cols"])
    liabilities_df['Total Pasivo'] = liabilities_df.sum(axis=1)

    return liabilities_df


def equity_df(equity_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns equity dataframe parsed from table
    """

    equity_array = np.array(equity_list).reshape(1, -1)
    equity_df = pd.DataFrame(equity_array,
                             index=[balance_date],
                             columns=equity_dict["cols"])

    return equity_df


def exercise_df(exercise_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from table
    """

    exercise_array = np.array(exercise_list).reshape(1, -1)
    exercise_df = pd.DataFrame(exercise_array,
                               index=[balance_date],
                               columns=exercise_dict["cols"])
    # calculate results after taxes
    exercise_df['Resultado del Ejercicio'] = exercise_df[exercise_dict["cols"][0]] - \
        exercise_df[exercise_dict["cols"][1]]

    return exercise_df


def profit_df(profit_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from table
    """

    profit_array = np.array(profit_list).reshape(1, -1)
    profit_df = pd.DataFrame(profit_array,
                             index=[balance_date],
                             columns=profit_dict["cols"])
    profit_df['Total'] = profit_df.sum(axis=1)

    return profit_df


def loss_df(loss_list: List[int], balance_date: datetime) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from table
    """

    loss_array = np.array(loss_list).reshape(1, -1)
    loss_df = pd.DataFrame(loss_array,
                           index=[balance_date],
                           columns=loss_dict["cols"])

    return loss_df


def final_liabilities_df(liabilities_df: pd.DataFrame, equity_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    totals = ['Total Pasivo', 'Patrimonio']

    # concat equity, exercise dfs and sum
    # total as Patrimonio
    eq_ex_df = pd.concat([equity_df, exercise_df], axis=1)
    eq_ex_df['Patrimonio'] = eq_ex_df.sum(axis=1)

    # concat liabilities, equity_exercise dfs
    # and sum total as Total Pasivo y Patrimonio
    final_liabilities_df = pd.concat([liabilities_df, eq_ex_df], axis=1)
    final_liabilities_df['Total Pasivo y Patrimonio'] = final_liabilities_df[totals] \
        .sum(axis=1)

    return final_liabilities_df


def final_loss_df(loss_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    loss_df['Resultado del Ejercicio'] = pd.Series(
        exercise_df['Resultado del Ejercicio'])
    loss_df['Total'] = loss_df.sum(axis=1)

    return loss_df


def get_all_df(table: List[str], balance_date: datetime):
    """
    Returns all tables from the loaded pdf
    """

    at = assets_df(table, balance_date)
    li = liabilities_df(table, balance_date)
    eq = equity_df(table, balance_date)
    ex = exercise_df(table, balance_date)
    # profit_and_loss_df(table, balance_date)
    pf, ls = pd.DataFrame(), pd.DataFrame()
    all_df = (at, li, eq, ex, pf, ls)

    return all_df


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
        "2020_09.pdf",  # -> cannot extract text
    ]

    valid_files: List[Path] = []

    for f in list_directory(directory):
        if f.name in exclude_files:
            continue

        valid = check_page_orientation(f, directory)
        valid_files.append(valid)

    return valid_files


def main() -> None:
    files = validate_files(LOCAL_DIR)
    assets_concat_list: List[pd.DataFrame] = []
    liabilities_concat_list: List[pd.DataFrame] = []
    equity_concat_list: List[pd.DataFrame] = []
    exercise_concat_list: List[pd.DataFrame] = []
    profit_concat_list: List[pd.DataFrame] = []
    loss_concat_list: List[pd.DataFrame] = []

    for i, file in enumerate(files, start=1):
        publish_date, extracted_lists = extract(file)

        # [TODO]
        at, li, eq, ex, pf, ls = get_all_df(extracted_lists, publish_date)

        assets_concat_list.append(at)
        liabilities_concat_list.append(li)
        equity_concat_list.append(eq)
        exercise_concat_list.append(ex)
        profit_concat_list.append(pf)
        loss_concat_list.append(ls)

        print(f"{i} - {file.name} done")

        # # move parsed files
        # try:
        #     move_file(file, LOCAL_DONE_DIR)
        # except shutil.Error:
        #     copy_file(file, LOCAL_DONE_DIR)
        #     remove_file(file)

    print("All files parsed, creating DataFrames...")
    liabilities_df = pd.concat(liabilities_concat_list).sort_index()
    equity_df = pd.concat(equity_concat_list).sort_index()
    exercise_df = pd.concat(exercise_concat_list).sort_index()
    loss_df = pd.concat(loss_concat_list).sort_index()

    final_assets = pd.concat(assets_concat_list).sort_index()
    final_liabilities = final_liabilities_df(
        liabilities_df, equity_df, exercise_df)
    final_profit = pd.concat(profit_concat_list).sort_index()
    final_loss = final_loss_df(loss_df, exercise_df)

    final_assets.to_csv(LOCAL_DATASETS_DIR / "assets.csv")
    final_liabilities.to_csv(LOCAL_DATASETS_DIR / "liabilities.csv")
    final_profit.to_csv(LOCAL_DATASETS_DIR / "profit.csv")
    final_loss.to_csv(LOCAL_DATASETS_DIR / "loss.csv")
    print("All tasks done!")


if __name__ == "__main__":
    main()
