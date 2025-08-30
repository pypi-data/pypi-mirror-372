import datetime as dt
import json

import pandas as pd
import pytest
import pytest_check as ptc

# need to import the hyperion_client to force the correct import order for implicit filters.
import synmax.hyperion.hyperion_client as hc  # noqa
from synmax.helpers.implicit_filters import update_payload_with_implicit_filters
from synmax.hyperion import ApiPayload, add_daily, get_fips


def test_daily_func():
    df = pd.DataFrame(
        {
            "date": ["2022-01-01", "2022-02-01", "2024-02-01"],
            "gas_monthly": [1000, 2000, 2000],
            "oil_monthly": [2000, 3000, 3000],
            "water_monthly": [8000, 9000, 9000],
        }
    )

    result_df = pd.DataFrame(
        {
            "date": ["2022-01-01", "2022-02-01", "2024-02-01"],
            "gas_monthly": [1000, 2000, 2000],
            "oil_monthly": [2000, 3000, 3000],
            "water_monthly": [8000, 9000, 9000],
            "gas_daily": [32.25806451612903, 71.42857142857143, 68.9655172414],
            "oil_daily": [64.51612903225806, 107.14285714285714, 103.448275862],
            "water_daily": [258.06451612903226, 321.42857142857144, 310.344827586],
        }
    )

    return_df = add_daily(df)

    with ptc.check:
        pd.testing.assert_frame_equal(return_df, result_df)

    df.drop(columns=["water_monthly"], inplace=True)

    result_df.drop(columns=["water_monthly", "water_daily"], inplace=True)

    return_df = add_daily(df)

    with ptc.check:
        pd.testing.assert_frame_equal(return_df, result_df)

    new_column = [555, 555, 555]

    df["new_column"] = new_column

    result_df["new_column"] = new_column
    # put the new column after the montly columns
    result_df = result_df[["date", "gas_monthly", "oil_monthly", "new_column", "gas_daily", "oil_daily"]]

    return_df = add_daily(df)

    with ptc.check:
        pd.testing.assert_frame_equal(return_df, result_df)


def test_add_fips():
    df = get_fips()
    ptc.equal(df.shape[0], 3195, "FIPS data incorrect")
