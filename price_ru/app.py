import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    log_level: str
    table_id: str
    sheet_title: str
    title_rows_count: int
    url_col_num: int
    price_col_ltr: str
    scope: str = "https://spreadsheets.google.com/feeds"

    def __init__(self):
        try:
            self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            self.table_id = os.environ["TABLE_ID"]
            self.sheet_title = os.environ["SHEET_TITLE"]
            self.title_rows_count = int(os.environ["TITLE_ROWS_COUNT"])
            self.url_col_num = int(os.environ["URL_COL_NUM"])
            self.price_col_ltr = os.environ["PRICE_COL_LTR"]
        except KeyError as err:
            err.add_note(f"\nEnvironment variable {err} must be set")
            raise err

        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)s:%(funcName)s] %(message)s",
            level=self.log_level,
        )
        logging.getLogger("google.auth.transport.requests").setLevel(logging.WARNING)
        logging.getLogger("oauth2client").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)


@dataclass
class Product:
    name: str
    price: int | None
    cell: str


class Browser:
    """Playwright Browser."""

    def __init__(self) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=True)
        self.page = self.browser.new_page()

    def get_title(self, url: str) -> str:
        """Get page title."""
        self.page.goto(url)
        return self.page.title()

    def get_price_from_title(self, url: str) -> int | None:
        """Get price from page title."""
        price_regex = re.compile(r"от\s+(\d+)\s+руб")
        title = self.get_title(url)
        price = price_regex.search(title)
        if not price:
            return None
        return int(price.group(1))


def gspread_client(scope: str, key_file: str | None = None) -> gspread.Client:
    """Login to Google Spreadsheet."""
    if key_file is None:
        key_file = str(Path(__file__).parent.absolute() / "cred.json")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)
    return gspread.authorize(credentials)


def open_worksheet(
    gc: gspread.Client, table_id: str, sheet_title: str
) -> gspread.Worksheet:
    """Open Google Spreadsheet."""
    return gc.open_by_key(table_id).worksheet(sheet_title)


def get_non_empty_cells(wks: gspread.Worksheet, col_num: int) -> list[str]:
    """Get non-empty cells from Google Spreadsheet."""
    col_values = wks.col_values(col_num, value_render_option="FORMULA")
    return [item for item in col_values if item]


def update_product_price(wks: gspread.Worksheet, product: Product) -> None:
    """Update product price in cell."""
    if not product.price:
        return
    old_price = int(wks.acell(product.cell).value)
    price_change = product.price - old_price
    logger.info(
        f"{product.name} --- Old price: {old_price}, "
        f"New price: {product.price}, Change: {price_change}"
    )
    if price_change != 0:
        logger.info(
            f"{product.name} --- Updating cell {product.cell} with {product.price}"
        )
        wks.update_acell(product.cell, product.price)


def run(config: Config) -> None:
    gc = gspread_client(config.scope)
    wks = open_worksheet(gc, config.table_id, config.sheet_title)
    url_cells = get_non_empty_cells(wks, config.url_col_num)
    browser = Browser()
    for idx, cell in enumerate(url_cells, 1 + config.title_rows_count):
        if "HYPERLINK" not in cell:
            continue
        cell_splitted = cell.split('"')
        url = cell_splitted[1]
        name = f"{cell_splitted[3]:<16}"
        product = Product(
            name=name,
            price=browser.get_price_from_title(url),
            cell=f"{config.price_col_ltr}{idx}",
        )
        update_product_price(wks, product)


def main() -> None:
    """Main function."""
    config = Config()
    run(config)


if __name__ == "__main__":
    main()
