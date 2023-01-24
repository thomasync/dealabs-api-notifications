from dealabs import Dealabs, Utils
from unittest.mock import patch
import os


def test_getCookies():
    dealabs = Dealabs()
    cookies = dealabs.getCookies(False)

    assert cookies is not None
    assert "xsrf_t" in cookies
    assert "pepper_session" in cookies
    assert os.path.exists(Utils.getCacheFolder() + "cookies.json")

    cookies_from_cache = dealabs.getCookies(True)
    assert cookies_from_cache is not None
    assert cookies == cookies_from_cache


@patch('dealabs.Dealabs.getCookies')
def test_getDeals_without_cookies(mock_getCookies):
    mock_getCookies.return_value = []

    dealabs = Dealabs()
    deals = dealabs.getDeals(False)

    assert mock_getCookies.call_count == 3
    assert deals is not None
    assert len(deals) == 0


def test_getDeals_without_inModeration():
    dealabs = Dealabs()
    deals = dealabs.getDeals(False)

    assert deals is not None
    assert len(deals) > 0


def test_getDeals_with_inModeration():
    dealabs = Dealabs()
    deals = dealabs.getDeals(True)

    assert deals is not None
    assert len(deals) > 0
