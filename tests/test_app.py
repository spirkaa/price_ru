import logging

import pytest

from .context import app

URL_CELLS = [
    None,
    "wrong_value",
    '=HYPERLINK("https://price.ru/zhestkie-diski/seagate-st20000nm007d/";"ST20000NM007D")',
]
PRICE = 1234
TITLE = f"купить по цене от {PRICE} руб в интернет-магазинах"  # noqa: RUF001
CELL_VALUE = 15
NEW_PRICE = 42


class TestCell:
    """Cell mock."""

    value = CELL_VALUE


class TestWorksheet:
    """Worksheet mock."""

    def col_values(self, *args, **kwargs):
        return URL_CELLS

    def acell(self, *args, **kwargs):
        return TestCell()

    def update_acell(self, *args, **kwargs):
        """Update cell mock."""


class TestSpreadsheet:
    """Spreadsheet mock."""

    def worksheet(self, *args, **kwargs):
        return TestWorksheet()


class TestClient:
    """Client mock."""

    def open_by_key(self, *args, **kwargs):
        return TestSpreadsheet()


@pytest.fixture
def mocker_browser(mocker):
    """Fixture for browser."""
    mocker.patch("playwright.sync_api.PlaywrightContextManager.start")
    mocker.patch("playwright.sync_api.Playwright.firefox")
    yield mocker
    mocker.resetall()


@pytest.mark.usefixtures("mocker_browser")
def test_get_title(mocker):
    """Test - Get title."""
    browser = app.Browser()
    title = browser.get_title("http://test")
    assert isinstance(title, mocker.MagicMock)


@pytest.mark.usefixtures("mocker_browser")
def test_get_price_from_title(mocker):
    """Test - Get price from page title."""
    mocker.patch("price_ru.app.Browser.get_title", return_value=TITLE)
    browser = app.Browser()
    res = browser.get_price_from_title(TITLE)
    assert res == PRICE
    mocker.resetall()


@pytest.mark.usefixtures("mocker_browser")
def test_get_price_from_title_empty(mocker):
    """Test - Get price from page title - empty."""
    mocker.patch("price_ru.app.Browser.get_title", return_value="")
    browser = app.Browser()
    res = browser.get_price_from_title("")
    assert res is None
    mocker.resetall()


def test_gspread_client(mocker):
    """Test - Login to Google Spreadsheet."""
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch(
        "oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name"
    )
    mocker.patch("gspread.authorize")
    app.gspread_client("scope")
    app.gspread_client("scope", "key")
    app.gspread.authorize.assert_called()
    mocker.resetall()


def test_open_worksheet():
    """Test - Open Google Spreadsheet."""
    gc = TestClient()
    res = app.open_worksheet(gc, "id123", "title")
    assert isinstance(res, TestWorksheet)


def test_get_non_empty_cells():
    """Test - Get non-empty cells from Google Spreadsheet."""
    wks = TestWorksheet()
    res = app.get_non_empty_cells(wks, 5)
    assert res == URL_CELLS[1:]


def test_update_product_price_same(caplog):
    """Test - Update product price in cell - same."""
    wks = TestWorksheet()
    product = app.Product("price_same", CELL_VALUE, "F5")
    with caplog.at_level(logging.INFO):
        app.update_product_price(wks, product)
    assert f"Old price: {product.price}, New price: {product.price}" in caplog.text


def test_update_product_price_differ(caplog):
    """Test - Update product price in cell - differ."""
    wks = TestWorksheet()
    product = app.Product("price_differ", NEW_PRICE, "F5")
    with caplog.at_level(logging.INFO):
        app.update_product_price(wks, product)
    assert f"{product.cell} with {product.price}" in caplog.text


def test_update_product_price_none(caplog):
    """Test - Update product price in cell - none."""
    wks = TestWorksheet()
    product = app.Product("price_none", None, "F5")
    with caplog.at_level(logging.INFO):
        app.update_product_price(wks, product)
    assert caplog.text == ""


def test_main(mocker):
    """Test - Main function."""
    mocker.patch("price_ru.app.gspread_client")
    mocker.patch("price_ru.app.open_worksheet")
    mocker.patch("price_ru.app.get_non_empty_cells", return_value=URL_CELLS[1:])
    mocker.patch("price_ru.app.Browser.__init__", return_value=None)
    mocker.patch("price_ru.app.Browser.get_price_from_title")
    mocker.patch("price_ru.app.update_product_price")
    app.main()
    assert app.update_product_price.call_args[0][1].name == "ST20000NM007D   "
    mocker.resetall()
