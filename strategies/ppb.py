from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
import pdfplumber as pdf
from pdfplumber.page import Page
from settings.conf import assets_cols, liabilities_cols, loss_cols, profit_cols
from utils import amounts_to_int, get_date, is_digit, list_to_df

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
    # [i][1][0] for each table
    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        title = p0.extract_text().split("\n")[0]
        tables = p0.extract_tables()

    return title, tables


table_settings = {"horizontal_strategy": "text",
                  "vertical_strategy": "text",
                  "text_tolerance": 1}


def extract_using_words_visual(file: Path) -> None:
    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        im = p0.to_image(resolution=300)
        im.save(f'{file.stem}-before.jpg')
        im.debug_tablefinder(table_settings)
        im.save(f'{file.stem}-after-table.jpg')
        im.reset().draw_rects(p0.extract_words())
        im.save(f'{file.stem}-after-words.jpg')


def extract_using_words(file: Path) -> Tuple[str, List[Dict[str, Any]]]:

    with pdf.open(file) as f:
        p0: Page = f.pages[0]
        words = p0.extract_words()

    title = " ".join([i['text'] for i in words[0:10]])

    return title, words


def check_indexes(words: List[Dict[str, Any]], indexes: List[Union[int, None]], adjustment: int = 1):
    """recursive function that checks if element in current index 
    is a digit else corrects that index"""

    # for each get index and check if value is digit
    false_digits = [(i, is_digit(words[x]['text']))
                    for i, x in enumerate(indexes)
                    if x is not None]
    # adjust index if element cannot be parsed to int (False)
    corrected = [indexes[x] + adjustment if y is False else indexes[x]
                 for x, y
                 in false_digits]
    # finally if not all values are digits (True)
    if all([is_digit(words[x]['text']) for x in corrected]) is False:
        # run the function again with new indexes
        return check_indexes(words, corrected, adjustment)
    else:
        # return corrected indexes
        return corrected


def string_tables_from_words(words: List[Dict[str, Any]]) -> List[str]:

    assets_indexes = [i[0] for i
                      in assets_liabs_idxs
                      if i[0] is not None]

    checked_assets_indexes = check_indexes(words,
                                           assets_indexes)

    assets_table = " ".join([words[i]['text']
                             for i
                             in checked_assets_indexes])

    liabs_indexes = [i[1] for i
                     in assets_liabs_idxs
                     if i[1] is not None]

    checked_liabs_indexes = check_indexes(words,
                                          liabs_indexes)

    liabs_table = " ".join([words[i]['text']
                            for i
                            in checked_liabs_indexes])

    loss_indexes = [i[0] for i
                    in loss_profit_idxs
                    if i[0] is not None]

    checked_loss_indexes = check_indexes(words,
                                         loss_indexes)

    loss_table = " ".join([words[i]['text']
                           for i
                           in checked_loss_indexes])

    profit_indexes = [i[1] for i
                      in loss_profit_idxs
                      if i[1] is not None]

    checked_profit_indexes = check_indexes(words,
                                           profit_indexes)

    profit_table = " ".join([words[i]['text']
                             for i
                             in checked_profit_indexes])

    return [assets_table, liabs_table, loss_table, profit_table]


def extract(f: Path) -> Union[List[pd.DataFrame], None]:
    """
    Returns Dataframes extracted from balance
    sheets using pdfplumber strategy
    """

    if not f.is_file():
        return None

    title, words = extract_using_words(f)
    tables = string_tables_from_words(words)

    publish_date = get_date(title)
    at_list = amounts_to_int(tables[0])
    li_list = amounts_to_int(tables[1])
    ls_list = amounts_to_int(tables[2])
    pf_list = amounts_to_int(tables[3])

    assets_df = list_to_df(at_list, publish_date, assets_cols)
    liabs_df = list_to_df(li_list, publish_date, liabilities_cols)
    loss_df = list_to_df(ls_list, publish_date, loss_cols)
    profit_df = list_to_df(pf_list, publish_date, profit_cols)

    return [assets_df, liabs_df, loss_df, profit_df]
