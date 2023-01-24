from dealabs import Dealabs, Deal
from unittest.mock import patch, MagicMock
import json


def check_deal_fields(deal):
    if type(deal) is Deal:
        deal = deal.json()

    assert "id" in deal
    assert "type" in deal
    assert "title" in deal
    assert "description" in deal
    assert "status" in deal
    assert "price" in deal
    assert "nextBestPrice" in deal
    assert "priceReduction" in deal
    assert "priceDiscount" in deal
    assert "image" in deal
    assert "redirectUrl" in deal
    assert "url" in deal
    assert "updatedAt" in deal
    assert "createdAt" in deal
    assert "publishedAt" in deal
    assert "merchant" in deal


def test_constructor_empty():
    dealabs = Dealabs()

    assert dealabs is not None
    assert dealabs.minimum_discount == 90
    assert dealabs.free_products == 0
    assert dealabs.expire_notification == 0
    assert dealabs.open_dealabs == 1
    assert dealabs.priority_only_first == 1
    assert dealabs.refresh_seconds == 0


def test_constructor_with_parameters():
    dealabs = Dealabs(10, 1, 1, 0, 0)

    assert dealabs is not None
    assert dealabs.minimum_discount == 10
    assert dealabs.free_products == 1
    assert dealabs.expire_notification == 1
    assert dealabs.open_dealabs == 0
    assert dealabs.priority_only_first == 0
    assert dealabs.refresh_seconds == 0


def test_setPushOver():
    dealabs = Dealabs()
    dealabs.setPushOver("token", "user")
    assert dealabs.token == "token"
    assert dealabs.user == "user"


@patch('dealabs.Dealabs._getThreads')
def test_getDeals_check_fields(mock_getThreads):
    with open('tests/mocks/deals.json') as file:
        mock_deals = json.load(file)

    mock_getThreads.return_value = mock_deals
    dealabs = Dealabs()

    deals = dealabs.getDeals(False)

    # Check ordered by updatedAt asc
    for i in range(0, len(deals) - 1):
        assert deals[i].updatedAt <= deals[i + 1].updatedAt

    # Check all fields
    for deal in deals:
        assert hasattr(deal, '_addedModeration')
        check_deal_fields(deal)


@patch('dealabs.Dealabs._getThreads')
def test_getDeals_check_deactivated(mock_getThreads):
    with open('tests/mocks/deals.json') as file:
        mock_deals = json.load(file)

    mock_getThreads.return_value = mock_deals
    dealabs = Dealabs()

    for deal in dealabs.getDeals(False):
        if deal.id == "2496398":
            assert deal.isDeactivated() == True
        elif deal.id == "2496417":
            assert deal.isDeactivated() == True


@patch('dealabs.Dealabs._getThreads')
def test_getDeals_check_location(mock_getThreads):
    with open('tests/mocks/deals.json') as file:
        mock_deals = json.load(file)

    mock_getThreads.return_value = mock_deals
    dealabs = Dealabs()

    for deal in dealabs.getDeals(False):
        # isLocal and not isNational
        if deal.id == "2496418":
            assert deal.isLocal() == True

        # not isLocal and not selectedLocations
        elif deal.id == "2496420":
            assert deal.isLocal() == False

        # isLocal and isNational
        elif deal.id == "2496421":
            assert deal.isLocal() == False


@patch('dealabs.Dealabs._getThreads')
def test_getDeals_check_error(mock_getThreads):
    with open('tests/mocks/deals.json') as file:
        mock_deals = json.load(file)

    mock_getThreads.return_value = mock_deals
    dealabs = Dealabs()

    for deal in dealabs.getDeals(False):
        # in Title
        if deal.id == "2496446":
            assert deal.isError() == True

        # in Description
        elif deal.id == "2496447":
            assert deal.isError() == True

        # in Groups
        elif deal.id == "2496443":
            assert deal.isError() == True


@patch('dealabs.Dealabs._getThreads')
def test_getDeals_check_free(mock_getThreads):
    with open('tests/mocks/deals.json') as file:
        mock_deals = json.load(file)

    mock_getThreads.return_value = mock_deals
    dealabs = Dealabs()

    for deal in dealabs.getDeals(False):
        # in Title
        if deal.id == "2496442":
            assert deal.isFree() == True

        # in Price
        elif deal.id == "2496436":
            assert deal.isFree() == True

        # in Groups
        elif deal.id == "2496439":
            assert deal.isFree() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_fields(mock_getThread):
    with open('tests/mocks/deal_fields.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    check_deal_fields(deal)

    assert deal.priceReduction == 170
    assert deal.priceDiscount == 94.44
    assert deal.getHash() == "5200926d6bf01b884013ef7cf4013561"
    assert deal.image is not None
    assert deal.redirectUrl is not None


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_deactivated(mock_getThread):
    with open('tests/mocks/deal_deactivated.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isDeactivated() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_location_true(mock_getThread):
    with open('tests/mocks/deal_location_true.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isLocal() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_location_false(mock_getThread):
    with open('tests/mocks/deal_location_false.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isLocal() == False


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_location_false2(mock_getThread):
    with open('tests/mocks/deal_location_false2.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isLocal() == False


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_error_false(mock_getThread):
    with open('tests/mocks/deal_error_false.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isError() == False


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_error_true_title(mock_getThread):
    with open('tests/mocks/deal_error_true_title.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isError() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_error_true_desc(mock_getThread):
    with open('tests/mocks/deal_error_true_desc.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isError() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_error_true_group(mock_getThread):
    with open('tests/mocks/deal_error_true_group.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isError() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_free_false(mock_getThread):
    with open('tests/mocks/deal_free_false.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isFree() == False


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_free_true_title(mock_getThread):
    with open('tests/mocks/deal_free_true_title.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isFree() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_free_true_price(mock_getThread):
    with open('tests/mocks/deal_free_true_price.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isFree() == True


@patch('dealabs.Dealabs._getThread')
def test_getDeal_check_free_true_group(mock_getThread):
    with open('tests/mocks/deal_free_true_group.json') as file:
        mock_deal = json.load(file)

    mock_getThread.return_value = mock_deal
    dealabs = Dealabs()

    deal = dealabs.getDeal(0)
    assert deal.isFree() == True
