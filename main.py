import re
from datetime import datetime
from typing import Any, List, Tuple, Union

import numpy as np
import pandas as pd
import pdfplumber as ppb

from consts import (assets_cols, assets_dict, equity_cols, equity_dict_0,
                    equity_dict_1, exercise_cols, exercise_dict,
                    liabilities_cols, liabilities_dict, loss_cols, months_es,
                    profit_cols, profit_loss_dict)

pdf_file = "balance_sheets/continental/local/2015_12.pdf"


def open_pdf(pdf_file) -> List[str]:
    """
    Opens a pdf and return first page rows
    """
    with ppb.open(pdf_file) as pdf:
        p0 = pdf.pages[0]
        pdf_table = p0.extract_text().split("\n")
    return pdf_table


def get_title(pdf_table) -> str:
    """
    Returns the first row 'title' of the pdf table
    """
    return str(pdf_table[0])


def clean_table(pdf_table) -> List[Any]:
    """
    Cleans the pdf table rows by removing double spaces,
    then removes empty strings in lists
    """
    table_start = 2
    table_end = -1
    cleaned_table = [i.split("  ") for i in pdf_table[table_start:table_end]]
    cleaned_table = [list(filter(None, i)) for i in cleaned_table]
    return cleaned_table


def parse_title(title: str) -> datetime:
    """
    Extracts year, month and day of the balance sheet title
    using regex

        Params:
            title - balance title

        Returns:
            parsed_date - datetime obj
    """
    d, m, y = re.search(
        r'(?P<day>[\d]+) DE (?P<month>[A-Za-z]+) DE (?P<year>[\d]+)',
        title).groups()
    day = int(d.lstrip("0"))
    month = months_es[m] if m in months_es.keys() else ""
    year = int(y)
    parsed_date = datetime(year, month, day)
    return parsed_date


def get_indexes(term: str, table: List) -> Tuple[int, int]:
    """
    Retrieves the row and column indices of the table
    from a search term

        Params:
            term - search term
            table - pdf table

        Returns:
            row_number - row index
            col_number - column index
    """
    for row_number, row in enumerate(table):
        for col_number, _ in enumerate(row):
            if term in row[col_number]:
                return row_number, col_number


def amount_to_int(str_number: str) -> int:
    """
    Removes dots characters in a string number
    and parses it to int

        Params:
            str_number - string number

        Returns:
            number parsed to int
    """
    return int(str_number.replace('.', ''))


def list_or_first(x: List[str]) -> Union[List[str], str]:
    """
    Returns a list if the number of elements is
    greater than 1 else returns the first element of
    the list

        Params:
            x - list of strings

        Returns:
            returns list or first element
    """
    return x if len(x) > 1 else x[0]


def to_currency(n: int, currency: str = "USD") -> str:
    """
    Formats numbers as currency, in case of PYG
    currency replaces default thousand separator ',' as '.'
    """
    if currency == "PYG":
        return f"{n:,}".replace(",", ".")
    return f"{n:,}"


def get_amount(string_line: str) -> Union[List[str], str]:
    """
    Returns the result of string numbers matching
    the pattern using regex

        Params:
            string_line - string to extract numbers from

        Returns:
            list of strings matching pattern
    """
    result = re.findall(r'(\d+[\d\.?]*)', str(string_line))
    return list_or_first(result)


def assets_table(table: List) -> pd.DataFrame:
    """
    Returns assets dataframe parsed from pdf table
    """
    end_r, col = get_indexes(assets_dict["to"], table)

    assets_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_assets_list = [amount_to_int(i) for i in assets_list]

    assets_array = np.array(cleaned_assets_list).reshape(1, -1)
    assets = pd.DataFrame(assets_array, columns=assets_cols)
    assets['Total Activo'] = assets.sum(axis=1)

    return assets


def liabilities_table(table: List) -> pd.DataFrame:
    """
    Returns liabilities dataframe parsed from pdf table
    """
    end_r, col = get_indexes(liabilities_dict["to"], table)

    liabilities_list = [get_amount(i[col]) for i in table[:end_r + 1]]
    cleaned_liabilities_list = [amount_to_int(i) for i in liabilities_list]

    liabilities_array = np.array(cleaned_liabilities_list).reshape(1, -1)
    liabilities = pd.DataFrame(liabilities_array, columns=liabilities_cols)
    liabilities['Total Pasivo'] = liabilities.sum(axis=1)

    return liabilities


def equity_table(table: List) -> pd.DataFrame:
    """
    Returns equity dataframe parsed from pdf table
    """
    c1_from, _ = get_indexes(equity_dict_1["from"], table)
    c1_to, c1 = get_indexes(equity_dict_1["to"], table)
    c0_from, _ = get_indexes(equity_dict_0["from"], table)
    c0_to, c0 = get_indexes(equity_dict_0["to"], table)

    equity_list = [*[get_amount(i[c1]) for i in table[c1_from:c1_to + 1]],
                   *[get_amount(i[c0]) for i in table[c0_from:c0_to + 1]]]

    cleaned_equity_list = [amount_to_int(i) for i in equity_list]

    equity_array = np.array(cleaned_equity_list).reshape(1, -1)
    equity = pd.DataFrame(equity_array, columns=equity_cols)
    equity['Patrimonio'] = equity.sum(axis=1)

    return equity


def exercise_table(table: List) -> pd.DataFrame:
    """
    Returns exercise dataframe parsed from pdf table
    """
    str_r, _ = get_indexes(exercise_dict["from"], table)
    end_r, col = get_indexes(exercise_dict["to"], table)

    exercise_list = [get_amount(i[col]) for i in table[str_r:end_r + 1]]
    cleaned_exercise_list = [amount_to_int(i) for i in exercise_list]

    exercise_array = np.array(cleaned_exercise_list).reshape(1, -1)
    exercise = pd.DataFrame(exercise_array, columns=exercise_cols)
    # substract before taxes col with after taxes col
    exercise['Resultado del Ejercicio'] = exercise[exercise_cols[0]] - exercise[exercise_cols[1]]
    return exercise


def profit_loss_tables(table: List) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns profit and loss dataframes in one step
    because the pdf table format makes the columns merge
    when parsing tables from the file

        Params:
            table - pdf table

        Returns:
            loss - parsed loss df
            profit - parsed profit df
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
    loss = pd.DataFrame(loss_array, columns=loss_cols)
    loss['Total'] = loss.sum(axis=1)

    profit_array = np.array(cleaned_profit_list).reshape(1, -1)
    profit = pd.DataFrame(profit_array, columns=profit_cols)
    profit['Total Ganancias'] = profit.sum(axis=1)

    return profit, loss


def parse_tables(table: List):
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
    Returns the summary of a balance sheet.

    Example: summary(assets['Total Activo'][0], liabilities_and_equity['Total Pasivo y Patrimonio'][0],
                loss_and_exercise['Total Perdidas'][0], profit['Total Ganancias'][0])
    """
    print("Activo:", to_currency(assets_total, "PYG"))
    print("Pasivo y Patrimonio:", to_currency(liabilities_total, "PYG"))
    print("Perdidas:", to_currency(profit_total, "PYG"))
    print("Ganancias:", to_currency(loss_total, "PYG"))
