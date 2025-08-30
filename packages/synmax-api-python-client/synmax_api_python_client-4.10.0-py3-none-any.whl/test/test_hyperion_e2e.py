import datetime as dt
import logging

import pytest
import pytest_check as ptc
from synmax.hyperion import ApiPayload, HyperionApiClient

logging.basicConfig(level=logging.DEBUG)


# check for access token, and skip tests if not available
pytestmark = pytest.mark.skip("Shouldn't really be testing e2e")

@pytest.fixture(scope="module", autouse=True)
def client() -> HyperionApiClient:
    """tests if access token is available and works


    Returns:
        HyperionApiClient: constructed client
    """

    # requires access token to be set in the environment
    client = HyperionApiClient(local_server=False)

    if client.access_key is None:
        pytest.skip(reason="No access token available", allow_module_level=True)

    try:
        client.fetch_regions()
        return client
    except Exception as e:
        pytest.skip(reason=f"Client access Failed: {e}", allow_module_level=True)


# these are all integration-level tests, so they are not unit tests.  They are actually hitting the API, need internet access and a valid access token to run.  Needless to say, they are tightly coupled to the API and it's performance.  They only test if the endpoint returns.
def test_fetch_region(client):
    _ = client.fetch_regions()
    pass


def test_fetch_long_term_forecast(client):
    _ = client.long_term_forecast()


def test_fetch_operator_classification(client):
    _ = client.fetch_operator_classification()


def test_fetch_daily_fracked_feet(client):
    _ = client.daily_fracked_feet()


# Test - POST


def test_well_completion(client):
    payload = ApiPayload(
        start_date=dt.date(2021, 5, 1),
        end_date=dt.date(2022, 12, 25),
        state_code="CO",
        operator_name="GREAT WESTERN OPERATING COMPANY LLC",
    )

    result_df = client.well_completion(payload)
    ptc.equal(result_df.shape[0], 1495, f"Well completion count incorrect, expected 1495, got {result_df.shape[0]}")


@pytest.mark.parametrize("state, expected_rows", [("CO", 771), ("LA", 2416), ("ND", 1582), ("NM", 5623), ("OH", 576), ("OK", 2638), ("PA", 1423), ("TX", 18127), ("WV", 853), ("WY", 800)])
def test_rigs(client, state, expected_rows):
    payload = ApiPayload(start_date=dt.date(2021, 12, 1), end_date=dt.date(2022, 1, 31), state_code=state)
    result_df = client.rigs(payload)
    ptc.equal(result_df.shape[0], expected_rows, f"Rig data incorrect, expected {expected_rows} rows, got {result_df.shape[0]}")


def test_ducs_by_operator(client):
    payload = ApiPayload(
        start_date="2021-01-01",
        end_date="2021-01-31",
        aggregate_by="operator",
        operator="LIME ROCK RESOURCES LP",
    )

    result_df = client.ducs_by_operator(payload)
    ptc.equal(result_df.shape[0], 31, f"DUCS count incorrect, expected 31, got {result_df.shape[0]}")


@pytest.mark.xfail(reason="API function non-existent")
def test_production_by_county_and_operator(client):
    payload = ApiPayload(
        start_date="1929-04-01",
        end_date="1934-01-01",
        operator_name="Stephens Production Company",
        state_code="AR",
    )
    result_df = client.production_by_county_and_operator(payload)
    ptc.equal(result_df.shape[0], 0, f"Production by county and operator count incorrect, expected 0, got {result_df.shape[0]}")


def test_frac_crews(client):
    payload = ApiPayload(start_date="2021-01-01", end_date="2021-02-02")

    result_df = client.frac_crews(payload)
    ptc.equal(result_df.shape[0], 5536, f"Frack crew count incorrect, expected 5536, got {result_df.shape[0]}")


def test_production_by_well(client):
    # payload = ApiPayload(start_date='2016-01-01', end_date='2016-01-31', production_month=529)
    # payload = ApiPayload(state_code='WY', start_date='2017-01-01', end_date='2017-12-31',
    # operator_name='CITATION OIL & GAS CORP', region='west', sub_region='Wyoming')
    payload = ApiPayload(start_date=dt.date(2021, 1, 1), end_date=dt.date(2021, 2, 1), sub_region="SW PA")
    result_df = client.production_by_well(payload)
    ptc.equal(result_df.shape[0], 72297, f"Production by well count incorrect, expected 72297, got {result_df.shape[0]}")
    # with multiprocessing.Pool(processes=5) as pool:
    #     data_list = []  # [payload for _ in range(0, 5)]
    #     message = "API query progress"
    #     list(
    #         tqdm(
    #             pool.imap(client.production_by_well, data_list),
    #             desc=message,
    #             total=len(data_list),
    #             dynamic_ncols=True,
    #             miniters=0,
    #         )
    #     )


def test_short_term_forecast(client):
    # payload = ApiPayload(start_date=dt.date(2021, 8, 29), end_date=dt.date(2022, 9, 29))
    payload = ApiPayload(start_date=dt.date(2024, 8, 1), end_date=dt.date(2024, 9, 1), sub_region=["SW PA"])
    result_df = client.short_term_forecast(payload)
    ptc.equal(result_df.shape[0], 65918, f"Short term forecast count incorrect, expected 65918, got {result_df.shape[0]}")


@pytest.mark.skip(reason="Docs say not to use.")
def test_short_term_forecast_history(client):
    payload = ApiPayload(start_date=dt.date(2021, 8, 29), end_date=dt.date(2021, 9, 10))
    result_df = client.short_term_forecast_history(payload)
    print(result_df.count())

    payload = ApiPayload(start_date=dt.date(2020, 1, 1))
    result_df = client.short_term_forecast(payload)


def test_pipeline_scrapes(client):
    payload = ApiPayload(start_date=dt.date(2024, 1, 1), end_date=dt.date(2024, 1, 10), state_code=["AR"])
    result_df = client.pipeline_scrapes(payload)
    ptc.equal(result_df.shape[0], 8399, f"Pipeline scrapes count incorrect, expected 8399, got {result_df.shape[0]}")


def test_fetch_pipeline_scrape_status(client):
    result_df = client.fetch_pipeline_scrape_status()
    yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    ptc.is_in(yesterday, result_df["date"].to_list(), f"Pipeline scrape status not available for {yesterday}")


# def well_bug_test():
#     payload = ApiPayload(
#         start_date=dt.date(2015, 1, 1),
#         end_date=dt.date(2040, 12, 31),
#         state_code=["CO", "KS", "MT", "ND", "NE", "NM", "OK", "TX", "WY"],
#     )

#     wells_df = client.wells(payload)
#     print(wells_df.count())
