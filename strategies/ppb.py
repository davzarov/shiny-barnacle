from pathlib import Path
from typing import List

import pandas as pd
import pdfplumber as pdf
from pdfplumber.page import Page
from utils import amounts_to_list, get_date, list_to_df
from utils.consts import assets_cols, liabilities_cols, loss_cols, profit_cols


def extract(file: Path) -> List[pd.DataFrame]:
    """
    Returns Dataframes extracted from balance
    sheets using pdfplumber strategy
    """

    extracted_dataframes: List[pd.DataFrame] = []

    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        title = p0.extract_text().split("\n")[0]
        tables = p0.extract_tables()

    publish_date = get_date(title)
    at_list = amounts_to_list(tables[0][1][0])
    li_list = amounts_to_list(tables[1][1][0])
    ls_list = amounts_to_list(tables[3][1][0])
    pf_list = amounts_to_list(tables[4][1][0])

    assets_df = list_to_df(at_list, publish_date, assets_cols)
    assets_df['Total Activo'] = assets_df.sum(axis=1)

    liabs_df = list_to_df(li_list, publish_date, liabilities_cols)
    liabs_df['Total Pasivo y Patrimonio'] = liabs_df[['Total Pasivo', 'Patrimonio']] \
        .sum(axis=1)

    loss_df = list_to_df(ls_list, publish_date, loss_cols)
    loss_df['Total'] = loss_df.sum(axis=1)

    profit_df = list_to_df(pf_list, publish_date, profit_cols)
    profit_df['Total'] = profit_df.sum(axis=1)

    extracted_dataframes = [assets_df, liabs_df, loss_df, profit_df]

    return extracted_dataframes
