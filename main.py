from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

from consts import (assets_dict, equity_dict, exercise_dict, liabilities_dict,
                    profit_loss_dict)
from parsing import check_pdf, list_directory
from utils import amount_to_int, get_amount, get_indexes, to_currency


def validate_files(directory: Path) -> List[Path]:
    # [TODO] improve page orientation detection
    # to prevent using hardcoding file exclusions
    # that not conform is_landscape function
    excludes: List[str] = ["2015_12.pdf", "2017_12.pdf"]

    valid_files: List[Path] = []

    for f in list_directory(directory):
        # ignore file in excludes
        if f.name in excludes:
            continue

        valid = check_pdf(f, directory)
        valid_files.append(valid)

    return valid_files


def assets_table(table: List) -> pd.DataFrame:
    """
    Returns assets dataframe parsed from table
    """

    end_r, col = get_indexes(assets_dict["to"], table)

    assets_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_assets_list = [amount_to_int(i) for i in assets_list]

    assets_array = np.array(cleaned_assets_list).reshape(1, -1)
    assets = pd.DataFrame(assets_array, columns=assets_dict["cols"])
    assets['Total Activo'] = assets.sum(axis=1)

    return assets


def liabilities_table(table: List) -> pd.DataFrame:
    """
    Returns liabilities dataframe parsed from table
    """

    end_r, col = get_indexes(liabilities_dict["to"], table)

    liabilities_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_liabilities_list = [amount_to_int(i) for i in liabilities_list]

    liabilities_array = np.array(cleaned_liabilities_list).reshape(1, -1)
    liabilities = pd.DataFrame(liabilities_array, columns=liabilities_dict["cols"])
    liabilities['Total Pasivo'] = liabilities.sum(axis=1)

    return liabilities


def equity_table(table: List) -> pd.DataFrame:
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
    equity = pd.DataFrame(equity_array, columns=equity_dict["cols"])

    return equity


def exercise_table(table: List) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from table
    """

    str_r, _ = get_indexes(exercise_dict["from"], table)
    end_r, col = get_indexes(exercise_dict["to"], table)

    exercise_list = [get_amount(i[col]) for i in table[str_r:end_r + 1]]
    cleaned_exercise_list = [amount_to_int(i) for i in exercise_list]

    exercise_array = np.array(cleaned_exercise_list).reshape(1, -1)
    exercise = pd.DataFrame(exercise_array, columns=exercise_dict["cols"])
    # substract before taxes col with after taxes col
    exercise['Resultado del Ejercicio'] = exercise[exercise_dict["cols"][0]] - \
        exercise[exercise_dict["cols"][1]]

    return exercise


def profit_loss_tables(table: List) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
    loss = pd.DataFrame(loss_array, columns=profit_loss_dict["loss_cols"])
    loss['Total'] = loss.sum(axis=1)

    profit_array = np.array(cleaned_profit_list).reshape(1, -1)
    profit = pd.DataFrame(profit_array, columns=profit_loss_dict["profit_cols"])
    profit['Total Ganancias'] = profit.sum(axis=1)

    return profit, loss


def get_tables(table: List):
    """
    Returns all tables from the loaded pdf
    """

    assets = assets_table(table)
    liabilities = liabilities_table(table)
    equity = equity_table(table)
    exercise = exercise_table(table)
    profit, loss = profit_loss_tables(table)
    parsed_tables = (assets, liabilities, equity, exercise, profit, loss)

    return parsed_tables


def loss_table(loss_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    loss_totals = ['Total', 'Resultado del Ejercicio']
    loss_and_exercise_df = pd.concat([loss_df, exercise_df], axis=1)
    loss_and_exercise_df['Total Perdidas'] = loss_and_exercise_df[loss_totals].sum(axis=1)

    return loss_and_exercise_df


def liabilities_and_equity_table(liabilities_df: pd.DataFrame, equity_df: pd.DataFrame, exercise_df: pd.DataFrame) -> pd.DataFrame:
    liability_totals = ['Total Pasivo', 'Patrimonio', 'Resultado del Ejercicio']
    liabilities_and_equity_df = pd.concat([liabilities_df, equity_df, exercise_df], axis=1)
    liabilities_and_equity_df['Total Pasivo y Patrimonio'] = liabilities_and_equity_df[liability_totals] \
        .sum(axis=1)

    return liabilities_and_equity_df


def summary(assets_total: int, liabilities_total: int, profit_total: int, loss_total: int) -> None:
    """
    Returns the summary of a balance sheet
    """

    print("Activo:", to_currency(assets_total, "PYG"))
    print("Pasivo y Patrimonio:", to_currency(liabilities_total, "PYG"))
    print("Perdidas:", to_currency(profit_total, "PYG"))
    print("Ganancias:", to_currency(loss_total, "PYG"))
