import re
from typing import List, Tuple, Union


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
        return f"{n:,}".replace(",", ".")

    return f"{n:,}"


def get_amount(s: str) -> Union[List[str], str]:
    """
    Returns the result of string numbers matching
    the pattern 000.000.000.000 using regex
    """
    # not aware of decimals
    # raising 'list' object has
    # no attribute 'replace'
    # old_pattern = r'(\d+[\d\.?]*)'
    pattern = r'(\d+[\d\.?]*)(?:\,\d+)?'
    result = re.findall(pattern, str(s))

    return list_or_first(result)


def amount_to_int(str_number: str) -> int:
    """
    Removes dots of numbers and parses it to int
    """

    return int(str_number.replace('.', ''))


def get_indexes(term: str, table: List[str]) -> Tuple[int, int]:
    """
    Retrieves the row and column indices of the table
    for a search term
    """

    for row_number, row in enumerate(table):
        for col_number, _ in enumerate(row):
            if term in row[col_number]:
                return row_number, col_number
