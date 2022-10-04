import logging
import os
import re
from pathlib import Path

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

load_dotenv()

TABLE_ID = os.getenv("TABLE_ID")
SHEET_TITLE = os.getenv("SHEET_TITLE")
TITLE_ROWS_COUNT = int(os.getenv("TITLE_ROWS_COUNT"))
URL_COL_NUM = int(os.getenv("URL_COL_NUM"))
PRICE_COL_LTR = os.getenv("PRICE_COL_LTR")

SCOPE = ["https://spreadsheets.google.com/feeds"]

logger = logging.getLogger("__name__")
logging.getLogger("google.auth.transport.requests").setLevel(logging.WARNING)
logging.getLogger("oauth2client").setLevel(logging.WARNING)


def main() -> None:
    key_file = str(Path(__file__).parent.absolute() / "cred.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, SCOPE)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(TABLE_ID).worksheet(SHEET_TITLE)
    url_cells = [
        item
        for item in wks.col_values(URL_COL_NUM, value_render_option="FORMULA")
        if item
    ]

    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        for idx, cell in enumerate(url_cells, 1 + TITLE_ROWS_COUNT):
            if "HYPERLINK" in cell:
                price_cell = PRICE_COL_LTR + str(idx)

                url = cell.split('"')[1]
                name = cell.split('"')[3]

                page.goto(url)
                page.wait_for_selector("h1")

                title = page.title()
                new_price = int(re.search(r"от\s+(\d+)\s+руб", title).group(1))

                if new_price:
                    old_price = int(wks.acell(price_cell).value)
                    price_change = new_price - old_price

                    logger.info(
                        f"{name:<16} --- Old price: {old_price}, New price: {new_price}, Change: {price_change}"  # noqa
                    )

                    if price_change != 0:
                        logger.info(
                            f"{name:<16} --- Updating cell {price_cell} with {new_price}"
                        )
                        wks.update_acell(price_cell, new_price)
        browser.close()


if __name__ == "__main__":
    __version__ = "0.0.1"
    logging.basicConfig(
        format="%(asctime)s [%(levelname)8s] [%(name)s:%(lineno)s:%(funcName)20s()] --- %(message)s",  # noqa
        level=logging.INFO,
    )

    main()
