import re
from datetime import datetime
from typing import List, Set

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
            publish_date - datetime obj
    """
    d, m, y = re.search(
        r'(?P<day>[\d]+) DE (?P<month>[A-Za-z]+) DE (?P<year>[\d]+)',
        title).groups()
    day = int(d.lstrip("0"))
    month = months[m] if m in months.keys() else ""
    year = int(y)
    publish_date = datetime(year, month, day)
    return publish_date


# get row and column index by search term
def get_index_for_term(term: str, table: List) -> Set:
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


def str_num_to_int(str_number: str):
    """
    Removes dots characters in a string number
    and parses it to int

        Params:
            str_number - string number

        Returns:
            number parsed to int
    """
    return int(str_number.replace('.', ''))


def extract_str_num(text) -> List:
    return re.findall(r'(\d+[\d\.?]*)', str(text))


def activo_ll(table: List) -> List:
    cleaned_activo: List = []
    end_row, _ = get_index_for_term("CARGOS DIFERIDOS", table)
    activo = [extract_str_num(i[0])[0] for i in table[:end_row + 1]]
    cleaned_activo = [str_num_to_int(i) for i in activo]
    return cleaned_activo


def pasivo_ll(table: List) -> List:
    cleaned_pasivo: List = []
    end_row, _ = get_index_for_term("PROVISIONES Y PREVISIONES", table)
    pasivo = [extract_str_num(i[1])[0] for i in table[:end_row + 1]]
    cleaned_pasivo = [str_num_to_int(i) for i in pasivo]
    return cleaned_pasivo


def patrimonio_ll(table: List) -> List:
    cleaned_patrimonio: List = []
    col1_1, _ = get_index_for_term("CAPITAL SOCIAL", table)
    col1_2, _ = get_index_for_term("APORTES NO CAPITALIZADOS", table)
    col0_1, _ = get_index_for_term("AJUSTES AL PATRIMONIO", table)
    col0_2, _ = get_index_for_term("RESULTADOS ACUMULADOS", table)
    patrimonio = [
        *[extract_str_num(i[1])[0] for i in table[col1_1:col1_2 + 1]],
        *[extract_str_num(i[0])[0] for i in table[col0_1:col0_2 + 1]]]
    cleaned_patrimonio = [str_num_to_int(i) for i in patrimonio]
    return cleaned_patrimonio


def ejercicio_ll(table: List) -> List:
    cleaned_ejercicio: List = []
    ini_r, _ = get_index_for_term("Resultado del ejercicio antes del impuesto", table)
    fin_r, _ = get_index_for_term("Menos: Impuesto a la renta", table)
    ejercicio = [extract_str_num(i[0])[0] for i in table[ini_r:fin_r + 1]]
    cleaned_ejercicio = [str_num_to_int(i) for i in ejercicio]
    return cleaned_ejercicio


def perdida_ganancia_ll(table: List) -> Set:
    """
    Extract the profit and loss tables in one step
    because the pdf format makes the columns jumble

        Params:
            table - pdf table

        Returns:
            cleaned_perdida - parsed perdidas table
            cleaned_ganancia - parsed ganancias table
    """
    cleaned_perdida: List[int] = []
    cleaned_ganancia: List[int] = []

    ini_r, _ = get_index_for_term(
        "PERDIDAS POR OBLIGACION POR INTERMEDIACION FINANCIERA S. FINANCIERO", table)
    fin_r, _ = get_index_for_term("AJUSTES DE RESULTADOS DE EJERCICIOS ANTERIORES", table)

    perdida_ganancia = [extract_str_num(i) for i in table[ini_r:fin_r + 1]]
    ganancia_offset = [extract_str_num(i)[0] for i in table[fin_r + 1:-1]]

    cleaned_perdida = [str_num_to_int(i[0]) for i in perdida_ganancia]
    cleaned_ganancia = [
        *[str_num_to_int(i[1]) for i in perdida_ganancia],
        *[str_num_to_int(j) for j in ganancia_offset]]
    return cleaned_perdida, cleaned_ganancia


print(activo_ll(cleaned_table))
