from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pdfplumber as pdf
from pdfplumber.page import Page
from utils import get_date


def extract(file: Path) -> Tuple[datetime, List[List[int]]]:
    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        title = p0.extract_text().split("\n")[0]
        tables = p0.extract_tables()

    publish_date = get_date(title)
    at_list = get_assets_list(tables[0])
    li_list = get_liabilities_list(tables[1])
    loss_list = get_loss_list(tables[3])
    profit_list = get_profit_list(tables[4])

    extracted_lists = [at_list,
                       li_list,
                       loss_list,
                       profit_list]

    return publish_date, extracted_lists


def get_assets_list(assets_list: List[str]) -> List[int]:
    pass


def get_liabilities_list(liabilities_list: List[str]) -> List[int]:
    pass


def get_loss_list(loss_list: List[str]) -> List[int]:
    pass


def get_profit_list(profit_list: List[str]) -> List[int]:
    pass
