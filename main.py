import re
from datetime import datetime
from typing import List, Set, Union

import numpy as np
import pandas as pd
import pdfplumber as ppb

pdf_file = "balance_sheets/continental/local/2015_12.pdf"

# open pdf and return first page rows
with ppb.open(pdf_file) as pdf:
    p0 = pdf.pages[0]
    rows = p0.extract_text().split("\n")

# datetime format YYYY-MM-DD
months = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SETIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12
}

# get balance title
title = rows[0]
# clean double spaces
cleaned_table = [i.split("  ") for i in rows[2:-1]]
# clean empty strings
cleaned_table = [list(filter(None, i)) for i in cleaned_table]


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
    month = months[m] if m in months.keys() else ""
    year = int(y)
    parsed_date = datetime(year, month, day)
    return parsed_date


def get_index_for_term(term: str, table: List) -> Set[int]:
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


def str_to_int(str_number: str) -> int:
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


def get_str_num(string_line: str) -> Union[List[str], str]:
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
    columns = ["Disponible", "Valores Publicos", "Creditos S. Financiero",
               "Creditos S. no Financiero", "Creditos Diversos", "Creditos Vencidos",
               "Inversiones", "Bienes de Uso", "Cargos Diferidos"]

    end_r, _ = get_index_for_term("CARGOS DIFERIDOS", table)

    assets_list = [get_str_num(i[0]) for i in table[:end_r + 1]]
    cleaned_assets_list = [str_to_int(i) for i in assets_list]

    assets_array = np.array(cleaned_assets_list).reshape(1, -1)
    assets = pd.DataFrame(assets_array, columns=columns)
    assets['Total Activo'] = assets.sum(axis=1)
    return assets


def liabilities_table(table: List) -> pd.DataFrame:
    columns = ["Obligaciones S. Financiero", "Obligaciones S. no Financiero",
               "Diversas", "Provisiones y Previsiones"]

    end_r, _ = get_index_for_term("PROVISIONES Y PREVISIONES", table)

    liabilities_list = [get_str_num(i[1]) for i in table[:end_r + 1]]
    cleaned_liabilities_list = [str_to_int(i) for i in liabilities_list]

    liabilities_array = np.array(cleaned_liabilities_list).reshape(1, -1)
    liabilities = pd.DataFrame(liabilities_array, columns=columns)
    liabilities['Total Pasivo'] = liabilities.sum(axis=1)
    return liabilities


def patrimonio_table(table: List) -> pd.DataFrame:
    columns = ["Capital Social", "Aportes no Capitalizados",
               "Ajustes al Patrimonio", "Reservas", "Resultados Acumulados"]

    col1_1, _ = get_index_for_term("CAPITAL SOCIAL", table)
    col1_2, _ = get_index_for_term("APORTES NO CAPITALIZADOS", table)
    col0_1, _ = get_index_for_term("AJUSTES AL PATRIMONIO", table)
    col0_2, _ = get_index_for_term("RESULTADOS ACUMULADOS", table)

    patrimonio_list = [
        *[get_str_num(i[1]) for i in table[col1_1:col1_2 + 1]],
        *[get_str_num(i[0]) for i in table[col0_1:col0_2 + 1]]]
    cleaned_patrimonio_list = [str_to_int(i) for i in patrimonio_list]

    patrimonio_array = np.array(cleaned_patrimonio_list).reshape(1, -1)
    patrimonio = pd.DataFrame(patrimonio_array, columns=columns)
    patrimonio['Patrimonio'] = patrimonio.sum(axis=1)
    return patrimonio


def exercise_table(table: List) -> pd.DataFrame:
    columns = ["Antes del Impuesto", "Despues de Impuesto"]

    str_r, _ = get_index_for_term("Resultado del ejercicio antes del impuesto", table)
    end_r, _ = get_index_for_term("Menos: Impuesto a la renta", table)

    exercise_list = [get_str_num(i[0]) for i in table[str_r:end_r + 1]]
    cleaned_exercise_list = [str_to_int(i) for i in exercise_list]

    exercise_array = np.array(cleaned_exercise_list).reshape(1, -1)
    exercise = pd.DataFrame(exercise_array, columns=columns)
    # substract before taxes col with after taxes col
    exercise['Resultado del Ejercicio'] = exercise[columns[0]] - exercise[columns[1]]
    return exercise


def profit_loss_tables(table: List) -> Set[pd.DataFrame]:
    """
    Extract the profit and loss tables in one step
    because the pdf format makes the columns merge in
    the file

        Params:
            table - pdf table

        Returns:
            loss - parsed loss df
            profit - parsed profit df
    """
    loss_columns = ["Obligacion S. Financiero", "Obligacion S. no Financiero",
                    "Valuacion", "Incobrabilidad",
                    "Servicio", "Otras Perdidas Operativas",
                    "Extraordinarias", "Ajuste de Ejercicios Anteriores"]

    profit_columns = ["Creditos Vigentes S. Financiero", "Creditos Vigentes S. no Financiero",
                      "Creditos Vencidos", "Valuacion",
                      "Rentas y Diferencia Publicos y Privados", "Desafectacion de Previsones",
                      "Servicio", "Otras Ganancias Operativas",
                      "Extraordinarias", "Ajuste de Ejercicios Anteriores"]

    str_r, _ = get_index_for_term(
        "PERDIDAS POR OBLIGACION POR INTERMEDIACION FINANCIERA S. FINANCIERO", table)
    end_r, _ = get_index_for_term("AJUSTES DE RESULTADOS DE EJERCICIOS ANTERIORES", table)

    # extract merged list
    profit_loss_list = [get_str_num(i) for i in table[str_r:end_r + 1]]
    # extract remaining profit list
    remaining_profit_list = [get_str_num(i) for i in table[end_r + 1:-1]]
    # append loss elements to its own list
    cleaned_loss_list = [str_to_int(i[0]) for i in profit_loss_list]
    # join profit elements with the
    # remaining elements in a single list
    cleaned_profit_list = [
        *[str_to_int(i[1]) for i in profit_loss_list],
        *[str_to_int(j) for j in remaining_profit_list]]

    # convert lists to arrays
    loss_array = np.array(cleaned_loss_list).reshape(1, -1)
    profit_array = np.array(cleaned_profit_list).reshape(1, -1)

    # load arrays to dataframes
    loss = pd.DataFrame(loss_array, columns=loss_columns)
    loss['Total Perdida'] = loss.sum(axis=1)

    profit = pd.DataFrame(profit_array, columns=profit_columns)
    profit['Total Ganancia'] = profit.sum(axis=1)

    return profit, loss


patrimonio = patrimonio_table(cleaned_table)
print(patrimonio)
