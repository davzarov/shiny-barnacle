import os
import re
import secrets
import shutil
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

MESES = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SEPTIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12
}

MONTHS = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}


def list_directory(dir: Path) -> Generator[Path, None, None]:
    for file in dir.iterdir():
        if file.exists() and file.is_file():
            yield file


def is_empty(dir: Path) -> bool:
    """checks if directory is empty"""

    return not any(dir.iterdir())


def make_file(dir: Path, f: Path, ext: Optional[str]) -> Path:
    """outputs a file in a dir using the current file name"""

    random_hash = secrets.token_urlsafe(8)
    output = dir / (f"{f.stem}_{random_hash}{f.suffix}")

    if ext:
        output = dir / (f"{f.stem}_{random_hash}{ext}")

    if not output.exists():
        output.touch()

    return output


def move_file(origin: Path, destination: Path) -> None:
    shutil.move(os.fspath(origin), os.fspath(destination))


def copy_file(origin: Path, destination: Path) -> None:
    shutil.copy(os.fspath(origin), os.fspath(destination))


def remove_file(file: Path) -> None:
    file.unlink()


def list_or_first(x: List[str]) -> Union[List[str], str]:
    """
    Returns a list if the number of elements is
    greater than 1 else returns the first element of
    that list
    """

    return x if len(x) > 1 else x[0]


def to_currency(n: int, currency: str = "USD") -> str:
    """
    Returns numbers formatted as currency, in case of PYG
    currency replaces default thousand separator ',' with '.'
    """

    if currency == "PYG":
        return str(n).translate(str.maketrans(",.", ".,"))

    return f"{n:,}"


def summary(assets_total: int, liabilities_total: int, profit_total: int, loss_total: int) -> None:
    """
    Returns the summary of a balance sheet
    """

    print("Activo:", to_currency(assets_total, "PYG"))
    print("Pasivo y Patrimonio:", to_currency(liabilities_total, "PYG"))
    print("Perdidas:", to_currency(profit_total, "PYG"))
    print("Ganancias:", to_currency(loss_total, "PYG"))


def find_amounts(s: str) -> List[str]:
    """
    Returns the result of string numbers matching
    the pattern 000.000.000.000 using regex
    """

    pattern = r'(\d+[\d\.?]*)(?:\,\d+)?'  # decimal aware
    result = re.findall(pattern, str(s))

    return result


def get_date(title: str, lang: str = "es") -> datetime:
    """
    Extracts year, month and day of the balance sheet title
    using regex
    """

    d, m, y = re.search(
        r'(?P<day>[\d]+) DE (?P<month>[A-Za-z]+) DE (?P<year>[\d]+)',
        title).groups()
    day = int(d.lstrip("0"))
    month = int(MESES[m]) if lang == "es" else int(MONTHS[m])
    year = int(y)
    parsed_date = datetime(year, month, day)

    return parsed_date


def is_digit(str_value: str) -> bool:
    """Checks if a string represents a digit after replacing 
    thousand and decimal separators"""

    return str_value.replace(".", "").replace(",", "").isdigit()


def to_int(str_number: str) -> int:
    """
    Removes thousand separators and parses it to int
    """

    return int(str_number.replace('.', ''))


def amounts_to_int(str_amounts: List[str]) -> List[int]:
    """
    Returns a list of integers (amounts) extracted from
    string tables
    """

    cleaned_list = [to_int(i) for i in find_amounts(str_amounts)]
    return cleaned_list


def list_to_df(cleaned_list: List[int], published_date: datetime, columns: List[str]) -> pd.DataFrame:
    """
    Returns a DataFrame representing a table from the
    balance sheet
    """

    list_to_array = np.array(cleaned_list).reshape(1, -1)
    df = pd.DataFrame(list_to_array,
                      index=[published_date],
                      columns=columns)
    return df


def get_index(term: str, table: List[str]) -> Tuple[int, int]:
    """
    Retrieves the row and column indices of the table
    for a search term
    """

    for row_number, row in enumerate(table):
        for col_number, _ in enumerate(row):
            if term in row[col_number]:
                return row_number, col_number
