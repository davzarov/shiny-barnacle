from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
import pdfplumber as pdf
from pdfplumber.page import Page
from utils import amounts_to_int, get_date, list_to_df
from utils.consts import assets_cols, liabilities_cols, loss_cols, profit_cols

# settings for pdfplumber extract_tables method
table_settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    # "keep_blank_chars": True,
    # "snap_tolerance": 4
}

assets_liabs_idxs = [[25, 33],
                     [36, 45],
                     [53, 56],
                     [65, 69],
                     [72, 75],
                     [81, None],
                     [83, 85],
                     [89, 92],
                     [95, 99],
                     [None, 103],
                     [None, 105],
                     [None, 108],
                     [None, 112],
                     [None, 119],
                     [None, 125],
                     [128, 133]]

loss_profit_idxs = [[171, 181],
                    [191, 202],
                    [206, 214],
                    [218, 222],
                    [226, 237],
                    [241, 245],
                    [248, 252],
                    [259, 263],
                    [None, 266],
                    [None, 273],
                    [277, None],
                    [279, 281]]


def extract_using_tables(file: Path):

    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        title = p0.extract_text().split("\n")[0]
        tables = p0.extract_tables()

    return title, tables


def extract_using_words_visual(file: Path) -> None:

    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        im = p0.to_image(resolution=300)
        im.save(f'{file.stem}-before.jpg')
        im.debug_tablefinder()
        im.draw_rects(p0.extract_words())
        im.save(f'{file.stem}-after-words.jpg')
        im.reset().draw_rects(p0.extract_words(keep_blank_chars=True))
        im.save(f'{file.stem}-after-keeping-blanks.jpg')


def extract_using_words(file: Path) -> Tuple[str, List[Dict[str, Any]]]:

    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        words = p0.extract_words()

    title = " ".join([i['text'] for i in words[0:10]])

    return title, words


def string_tables_from_words(words: List[Dict[str, Any]]) -> List[str]:

    assets_indexes = [i[0] for i
                      in assets_liabs_idxs
                      if i[0] is not None]
    assets_table = " ".join([words[i]['text'] for i in assets_indexes])
    liabs_indexes = [i[1] for i
                     in assets_liabs_idxs
                     if i[1] is not None]
    liabs_table = " ".join([words[i]['text'] for i in liabs_indexes])
    loss_indexes = [i[0] for i
                    in loss_profit_idxs
                    if i[0] is not None]
    loss_table = " ".join([words[i]['text'] for i in loss_indexes])
    profit_indexes = [i[1] for i
                      in loss_profit_idxs
                      if i[1] is not None]
    profit_table = " ".join([words[i]['text'] for i in profit_indexes])

    return [assets_table, liabs_table, loss_table, profit_table]


def extract(file: Path) -> Union[List[pd.DataFrame], None]:
    """
    Returns Dataframes extracted from balance
    sheets using pdfplumber strategy
    """

    if not file.is_file():
        return None

    # title, tables = extract_using_tables(file)
    title, words = extract_using_words(file)
    tables = string_tables_from_words(words)

    publish_date = get_date(title)
    at_list = amounts_to_int(tables[0])  # [0][1][0] IndexError
    li_list = amounts_to_int(tables[1])  # [1][1][0] IndexError
    ls_list = amounts_to_int(tables[2])  # [3][1][0] IndexError
    pf_list = amounts_to_int(tables[3])  # [4][1][0] IndexError

    assets_df = list_to_df(at_list, publish_date, assets_cols)
    assets_df['Total Activo'] = assets_df.sum(axis=1)

    liabs_df = list_to_df(li_list, publish_date, liabilities_cols)
    liabs_df['Total Pasivo y Patrimonio'] = liabs_df[['Total Pasivo', 'Patrimonio']] \
        .sum(axis=1)

    loss_df = list_to_df(ls_list, publish_date, loss_cols)
    loss_df['Total'] = loss_df.sum(axis=1)

    profit_df = list_to_df(pf_list, publish_date, profit_cols)
    profit_df['Total'] = profit_df.sum(axis=1)

    return [assets_df, liabs_df, loss_df, profit_df]
