from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

from config import LOCAL_DATASETS_DIR, LOCAL_DIR
from consts import (assets_dict, equity_dict, exercise_dict, liabilities_dict,
                    profit_loss_dict)
from parsing import (check_pdf, clean_table, get_balance_date, get_table,
                     list_directory)
from utils import amount_to_int, get_amount, get_indexes, to_currency

# apt install libmagickwand-dev


def assets_df(table: List, balance_date: datetime) -> pd.DataFrame:
    """
    Returns assets dataframe parsed from table
    """

    end_r, col = get_indexes(assets_dict["to"], table)

    assets_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_assets_list = [amount_to_int(i) for i in assets_list]

    assets_array = np.array(cleaned_assets_list).reshape(1, -1)
    assets = pd.DataFrame(assets_array,
                          index=[balance_date],
                          columns=assets_dict["cols"])
    assets['Total Activo'] = assets.sum(axis=1)

    return assets


def liabilities_df(table: List, balance_date: datetime) -> pd.DataFrame:
    """
    Returns liabilities dataframe parsed from table
    """

    end_r, col = get_indexes(liabilities_dict["to"], table)

    liabilities_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_liabilities_list = [amount_to_int(i) for i in liabilities_list]

    liabilities_array = np.array(cleaned_liabilities_list).reshape(1, -1)
    liabilities = pd.DataFrame(liabilities_array,
                               index=[balance_date],
                               columns=liabilities_dict["cols"])
    liabilities['Total Pasivo'] = liabilities.sum(axis=1)

    return liabilities


def equity_df(table: List, balance_date: datetime) -> pd.DataFrame:
    """
    Returns equity dataframe parsed from table
    """

    c1_from, _ = get_indexes(equity_dict["col_1"]["from"], table)
    c1_to, c1 = get_indexes(equity_dict["col_1"]["to"], table)
    c0_from, _ = get_indexes(equity_dict["col_0"]["from"], table)
    c0_to, c0 = get_indexes(equity_dict["col_0"]["to"], table)

    equity_list = [*[get_amount(i[c1]) for i in table[c1_from:c1_to + 1]],
                   *[get_amount(i[c0]) for i in table[c0_from:c0_to + 1]]]

    cleaned_equity_list = [amount_to_int(i) for i in equity_list]

    equity_array = np.array(cleaned_equity_list).reshape(1, -1)
    equity = pd.DataFrame(equity_array,
                          index=[balance_date],
                          columns=equity_dict["cols"])

    return equity


def exercise_df(table: List, balance_date: datetime) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from table
    """

    str_r, _ = get_indexes(exercise_dict["from"], table)
    end_r, col = get_indexes(exercise_dict["to"], table)

    exercise_list = [get_amount(i[col]) for i in table[str_r:end_r + 1]]
    cleaned_exercise_list = [amount_to_int(i) for i in exercise_list]

    exercise_array = np.array(cleaned_exercise_list).reshape(1, -1)
    exercise = pd.DataFrame(exercise_array,
                            index=[balance_date],
                            columns=exercise_dict["cols"])

    # results after taxes
    exercise['Resultado del Ejercicio'] = exercise[exercise_dict["cols"][0]] - \
        exercise[exercise_dict["cols"][1]]

    return exercise


def profit_and_loss_df(table: List, balance_date: datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns profit and loss dataframes in one step in this case
    because the pdf table format makes the columns merge
    when parsing tables from the file
    """

    str_r, _ = get_indexes(profit_loss_dict["from"], table)
    end_r, _ = get_indexes(profit_loss_dict["to"], table)

    # merged profit and loss and remaining profit
    profit_loss_list = [get_amount(i) for i in table[str_r:end_r + 1]]
    remaining_profit_list = [get_amount(i) for i in table[end_r + 1:-1]]

    # join profit with remaining in single list
    cleaned_loss_list = [amount_to_int(i[0]) for i in profit_loss_list]
    cleaned_profit_list = [*[amount_to_int(i[1]) for i in profit_loss_list],
                           *[amount_to_int(j) for j in remaining_profit_list]]

    loss_array = np.array(cleaned_loss_list).reshape(1, -1)
    loss = pd.DataFrame(loss_array,
                        index=[balance_date],
                        columns=profit_loss_dict["loss_cols"])

    profit_array = np.array(cleaned_profit_list).reshape(1, -1)
    profit = pd.DataFrame(profit_array,
                          index=[balance_date],
                          columns=profit_loss_dict["profit_cols"])
    profit['Total'] = profit.sum(axis=1)

    return profit, loss


def get_all_df(table: List[str], balance_date: datetime):
    """
    Returns all tables from the loaded pdf
    """

    at = assets_df(table, balance_date)
    li = liabilities_df(table, balance_date)
    eq = equity_df(table, balance_date)
    ex = exercise_df(table, balance_date)
    pf, ls = profit_and_loss_df(table, balance_date)
    all_df = (at, li, eq, ex, pf, ls)

    return all_df


def final_liabilities_df(liabilities_df: pd.DataFrame, equity_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    totals = ['Total Pasivo', 'Patrimonio']

    # concat equity, exercise dfs and sum
    # total as Patrimonio
    eq_ex_df = pd.concat([equity_df, exercise_df], axis=1)
    eq_ex_df['Patrimonio'] = eq_ex_df.sum(axis=1)

    # concat liabilities, equity_exercise dfs
    # and sum total as Total Pasivo y Patrimonio
    final_df = pd.concat([liabilities_df, eq_ex_df], axis=1)
    final_df['Total Pasivo y Patrimonio'] = final_df[totals].sum(axis=1)

    return final_df


def final_loss_df(loss_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    loss_df['Resultado del Ejercicio'] = pd.Series(exercise_df['Resultado del Ejercicio'])
    loss_df['Total'] = loss_df.sum(axis=1)

    return loss_df


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
    # to prevent using hardcoding file exclusions
    # that not conform is_landscape function
    excludes: List[str] = [
        "2015_12.pdf",  # -> not landscape
        "2016_12.pdf",  # -> not opening fixed file
        "2017_12.pdf",  # -> not landscape
        "2018_01.pdf",  # -> cannot extract text file
        "2018_02.pdf",  # -> cannot extract text file
        "2020_09.pdf",  # -> cannot extract text file
    ]

    valid_files: List[Path] = []

    for f in list_directory(directory):
        # ignore file in excludes
        if f.name in excludes:
            continue

        valid = check_pdf(f, directory)
        valid_files.append(valid)

    return valid_files


# file 2018_10.pdf get_amount for equity_df returns
# ['860.678.300.000', '735.310.999.372', '35.188.363.384', '676.689.283.044', ['0', '00']]
# and amount_to_int raises -> 'list' object has no attribute 'replace'
# [TODO] try pattern -> r'(\d+[\d\.?]*)(?:\,\d+)?' to get number without decimals
def main() -> None:
    files = validate_files(LOCAL_DIR)
    assets_concat_list: List[pd.DataFrame] = []
    liabilities_concat_list: List[pd.DataFrame] = []
    equity_concat_list: List[pd.DataFrame] = []
    exercise_concat_list: List[pd.DataFrame] = []
    profit_concat_list: List[pd.DataFrame] = []
    loss_concat_list: List[pd.DataFrame] = []

    for i, file in enumerate(files, start=1):
        table = get_table(file)
        cleaned_table = clean_table(table)

        # balance date is obtained
        # parsing the balance sheet title
        balance_date = get_balance_date(str(table[0]))

        at, li, eq, ex, pf, ls = get_all_df(cleaned_table, balance_date)

        assets_concat_list.append(at)
        liabilities_concat_list.append(li)
        equity_concat_list.append(eq)
        exercise_concat_list.append(ex)
        profit_concat_list.append(pf)
        loss_concat_list.append(ls)

        print(f"{i} - {file.name} done")

        # move parsed files to
        # prevent duplication
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
    final_liabilities = final_liabilities_df(liabilities_df, equity_df, exercise_df)
    final_profit = pd.concat(profit_concat_list).sort_index()
    final_loss = final_loss_df(loss_df, exercise_df)

    final_assets.to_csv(LOCAL_DATASETS_DIR / "assets.csv")
    final_liabilities.to_csv(LOCAL_DATASETS_DIR / "liabilities.csv")
    final_profit.to_csv(LOCAL_DATASETS_DIR / "profit.csv")
    final_loss.to_csv(LOCAL_DATASETS_DIR / "loss.csv")
    print("All tasks done!")


if __name__ == "__main__":
    main()
