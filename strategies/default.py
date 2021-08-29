from pathlib import Path
from typing import List, Tuple

import pandas as pd
import pdfplumber as pdf
from pdfplumber.page import Page
from settings.conf import assets_cols, liabilities_cols, loss_cols, profit_cols
from utils import find_amounts, get_date, get_index, list_to_df, to_int

assets_dict = {
    "from": None,
    "to": "CARGOS DIFERIDOS"
}

liabilities_dict = {
    "from": None,
    "to": "PROVISIONES Y PREVISIONES"
}

equity_dict = {
    "col_0": {
        "from": "AJUSTES AL PATRIMONIO",
        "to": "RESULTADOS ACUMULADOS"
    },
    "col_1": {
        "from": "CAPITAL SOCIAL",
        "to": "APORTES NO CAPITALIZADOS"
    }
}

exercise_dict = {
    "from": "Resultado del ejercicio antes del impuesto",
    "to": "Menos: Impuesto a la renta"
}

profit_loss_dict = {
    "from": "PERDIDAS POR OBLIGACION POR INTERMEDIACION FINANCIERA S. FINANCIERO",
    "to": "AJUSTES DE RESULTADOS DE EJERCICIOS ANTERIORES"
}


def extract(file: Path) -> List[pd.DataFrame]:
    """
    Returns Dataframes extracted from balance
    sheets using default strategy
    """
    tbl_start: int = 2
    tbl_end: int = -1

    with pdf.open(file) as f:
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

    assets_df = list_to_df(at_list, publish_date, assets_cols[:-1])
    assets_df['Total Activo'] = assets_df.sum(axis=1)

    liabilities_df = list_to_df(li_list, publish_date, liabilities_cols[:4])
    liabilities_df['Total Pasivo'] = liabilities_df.sum(axis=1)

    equity_df = list_to_df(eq_list, publish_date, liabilities_cols[6:11])

    exercise_df = list_to_df(ex_list, publish_date, liabilities_cols[12:14])
    exercise_df['Resultado del Ejercicio'] = exercise_df[liabilities_cols[12]] \
        - exercise_df[liabilities_cols[13]]

    eq_and_ex_df = pd.concat([equity_df, exercise_df], axis=1)
    eq_and_ex_df['Patrimonio'] = eq_and_ex_df.sum(axis=1)

    liabilities_equity_df = pd.concat([liabilities_df, eq_and_ex_df], axis=1)
    liabilities_equity_df['Total Pasivo y Patrimonio'] = liabilities_equity_df[['Total Pasivo', 'Patrimonio']] \
        .sum(axis=1)

    loss_df = list_to_df(ls_list, publish_date, loss_cols[:-2])
    loss_df['Resultado del Ejercicio'] = pd.Series(
        exercise_df['Resultado del Ejercicio'])
    loss_df['Total'] = loss_df.sum(axis=1)

    profit_df = list_to_df(pt_list, publish_date, profit_cols[:-1])
    profit_df['Total'] = profit_df.sum(axis=1)

    return [assets_df, liabilities_df, loss_df, profit_df]


def get_assets_list(cleaned_table: List[List[str]]) -> List[int]:
    row, col = get_index(assets_dict["to"], cleaned_table)
    assets_list = [find_amounts(i[col]) for i in cleaned_table[:row + 1]]
    cleaned_assets_list = [to_int(i) for i in assets_list]

    return cleaned_assets_list


def get_liabilities_list(cleaned_table: List[List[str]]) -> List[int]:
    row, col = get_index(liabilities_dict["to"], cleaned_table)
    liabilities_list = [find_amounts(i[col]) for i in cleaned_table[:row + 1]]
    cleaned_liabilities_list = [to_int(i) for i in liabilities_list]

    return cleaned_liabilities_list


def get_equity_list(cleaned_table: List[List[str]]) -> List[int]:
    c1_from, _ = get_index(equity_dict["col_1"]["from"], cleaned_table)
    c1_to, c1 = get_index(equity_dict["col_1"]["to"], cleaned_table)
    c0_from, _ = get_index(equity_dict["col_0"]["from"], cleaned_table)
    c0_to, c0 = get_index(equity_dict["col_0"]["to"], cleaned_table)

    equity_list = [*[find_amounts(i[c1]) for i in cleaned_table[c1_from:c1_to + 1]],
                   *[find_amounts(i[c0]) for i in cleaned_table[c0_from:c0_to + 1]]]

    cleaned_equity_list = [to_int(i) for i in equity_list]

    return cleaned_equity_list


def get_exercise_list(cleaned_table: List[List[str]]) -> List[int]:
    start_row, _ = get_index(exercise_dict["from"], cleaned_table)
    end_row, col = get_index(exercise_dict["to"], cleaned_table)
    exercise_list = [find_amounts(i[col])
                     for i in cleaned_table[start_row:end_row + 1]]
    cleaned_exercise_list = [to_int(i) for i in exercise_list]

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
    profit_loss_list = [find_amounts(i)
                        for i in cleaned_table[str_r:end_r + 1]]

    # remaining profit
    remaining_profit_list = [find_amounts(i)
                             for i in cleaned_table[end_r + 1:-1]]

    cleaned_loss_list = [to_int(i[0]) for i in profit_loss_list]

    # join profit with remaining in single list
    cleaned_profit_list = [*[to_int(i[1]) for i in profit_loss_list],
                           *[to_int(j) for j in remaining_profit_list]]

    return cleaned_profit_list, cleaned_loss_list
