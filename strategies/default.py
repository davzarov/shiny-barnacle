from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

import pdfplumber as ppb
from consts import (assets_dict, equity_dict, exercise_dict, liabilities_dict,
                    profit_loss_dict)
from pdfplumber.page import Page
from utils import amount_to_int, get_amount, get_date, get_index


def extract(file: Path) -> Tuple[datetime, List[List[int]]]:
    """
    Removes double spaces and empty strings, returning 
    the title and a cleaned list of lists
    """
    tbl_start: int = 2
    tbl_end: int = -1

    with ppb.open(file) as f:
        p0: Page = f.pages[0]
        table = p0.extract_text().split("\n")

    title = table[0]
    cleaned_table = [i.split("  ") for i in table[tbl_start:tbl_end]]
    cleaned_table = [list(filter(None, i)) for i in cleaned_table]

    publish_date = get_date(title)
    at_list = get_assets_list(cleaned_table)
    li_list = get_liabilities_list(cleaned_table)
    eq_list = get_equity_list(cleaned_table)
    ex_list = get_exercise_list(cleaned_table)
    pt_list, ls_list = get_profit_and_loss_lists(cleaned_table)

    extracted_lists = [at_list,
                       li_list,
                       eq_list,
                       ex_list,
                       pt_list,
                       ls_list]

    return publish_date, extracted_lists


def get_assets_list(cleaned_table: List[List[str]]) -> List[int]:
    row, col = get_index(assets_dict["to"], cleaned_table)
    assets_list = [get_amount(i[col]) for i in cleaned_table[:row + 1]]
    cleaned_assets_list = [amount_to_int(i) for i in assets_list]

    return cleaned_assets_list


def get_liabilities_list(cleaned_table: List[List[str]]) -> List[int]:
    row, col = get_index(liabilities_dict["to"], cleaned_table)
    liabilities_list = [get_amount(i[col]) for i in cleaned_table[:row + 1]]
    cleaned_liabilities_list = [amount_to_int(i) for i in liabilities_list]

    return cleaned_liabilities_list


def get_equity_list(cleaned_table: List[List[str]]) -> List[int]:
    c1_from, _ = get_index(equity_dict["col_1"]["from"], cleaned_table)
    c1_to, c1 = get_index(equity_dict["col_1"]["to"], cleaned_table)
    c0_from, _ = get_index(equity_dict["col_0"]["from"], cleaned_table)
    c0_to, c0 = get_index(equity_dict["col_0"]["to"], cleaned_table)

    equity_list = [*[get_amount(i[c1]) for i in cleaned_table[c1_from:c1_to + 1]],
                   *[get_amount(i[c0]) for i in cleaned_table[c0_from:c0_to + 1]]]

    cleaned_equity_list = [amount_to_int(i) for i in equity_list]

    return cleaned_equity_list


def get_exercise_list(cleaned_table: List[List[str]]) -> List[int]:
    start_row, _ = get_index(exercise_dict["from"], cleaned_table)
    end_row, col = get_index(exercise_dict["to"], cleaned_table)
    exercise_list = [get_amount(i[col])
                     for i in cleaned_table[start_row:end_row + 1]]
    cleaned_exercise_list = [amount_to_int(i) for i in exercise_list]

    return cleaned_exercise_list


def get_profit_and_loss_lists(cleaned_table: List[List[str]]) -> Tuple[List[int], List[int]]:
    """
    Returns profit and loss lists in one step in this case
    because the pdf table format makes the columns merge
    when parsing tables from the file
    """

    str_r, _ = get_index(profit_loss_dict["from"], cleaned_table)
    end_r, _ = get_index(profit_loss_dict["to"], cleaned_table)

    # merged profit and loss
    profit_loss_list = [get_amount(i) for i in cleaned_table[str_r:end_r + 1]]

    # remaining profit
    remaining_profit_list = [get_amount(i)
                             for i in cleaned_table[end_r + 1:-1]]

    cleaned_loss_list = [amount_to_int(i[0]) for i in profit_loss_list]

    # join profit with remaining in single list
    cleaned_profit_list = [*[amount_to_int(i[1]) for i in profit_loss_list],
                           *[amount_to_int(j) for j in remaining_profit_list]]

    return cleaned_profit_list, cleaned_loss_list
