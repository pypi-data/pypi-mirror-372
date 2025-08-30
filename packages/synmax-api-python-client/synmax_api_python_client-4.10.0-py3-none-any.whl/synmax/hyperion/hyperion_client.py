import logging
import os

import pandas

from synmax.common import ApiClient, ApiClientAsync
from synmax.helpers.implicit_filters import apply_implicit_filters
from synmax.hyperion.hyperion_payload import ApiPayload

LOGGER = logging.getLogger(__name__)


class ServiceUnavailableError(Exception):
    pass


class HyperionApiClient(object):
    def __init__(self, access_token: str = None, local_server=False, async_client=True, tddm_disable: bool = False):
        """

        :param access_token:
        :param local_server:
        :param async_client:  disabled - cannot run in async mode due to http 429 throttle limit
        :param tddm_disable:  (default: False) - disable TDDM printout if True
        """

        if access_token is None:
            access_token = os.getenv("access_token")
        self.access_key = access_token

        if local_server:
            self._base_uri = "http://127.0.0.1:8080/"
        else:
            self._base_uri = "https://hyperion.api.synmax.com/"

        async_client = False  # do not run in async to avoid http 429 throttle limit
        if async_client:
            LOGGER.info("Initializing async client")
            self.api_client = ApiClientAsync(access_token=access_token)
        else:
            self.api_client = ApiClient(access_token=access_token)

        self.api_client_sync = ApiClient(access_token=access_token)

        self.api_client.tdqm_disable = tddm_disable
        self.api_client_sync.tdqm_disable = tddm_disable

    # create get/set properties for tqdm_disable
    @property
    def tdqm_disable(self):
        return self.api_client.tdqm_disable

    @tdqm_disable.setter
    def tdqm_disable(self, value: bool):
        self.api_client.tdqm_disable = value
        self.api_client_sync.tdqm_disable = value

    # GET

    def fetch_regions(self) -> pandas.DataFrame:
        return self.api_client_sync.get(
            f"{self._base_uri}/v3/regions", return_json=True
        )

    def fetch_dtils(self) -> pandas.DataFrame:
        return self.api_client_sync.get(f"{self._base_uri}/v3/dtils", return_json=True)

    def fetch_operator_classification(self) -> pandas.DataFrame:
        return self.api_client_sync.get(
            f"{self._base_uri}/v3/operatorclassification", return_json=True
        )

    def fetch_pipeline_scrape_status(self) -> pandas.DataFrame:
        return self.api_client_sync.get(
            f"{self._base_uri}/v3/pipelinescrapestatus", return_json=True
        )

    def fetch_tils(self) -> pandas.DataFrame:
        return self.api_client_sync.get(f"{self._base_uri}/v3/tils", return_json=True)

    def fetch_tils_expanded(self) -> pandas.DataFrame:
        return self.api_client_sync.get(f"{self._base_uri}/v3/tils_expanded", return_json=True)

    def fetch_til_wells(self) -> pandas.DataFrame:
        return self.api_client_sync.get(f"{self._base_uri}/v3/til_wells", return_json=True)

    def fetch_til_wells_expanded(self) -> pandas.DataFrame:
        return self.api_client_sync.get(f"{self._base_uri}/v3/til_wells_expanded", return_json=True)


    def fetch_forecast_run_dates(self) -> pandas.DataFrame:
        return self.api_client_sync.get(
            f"{self._base_uri}/v3/shorttermforecasthistorydates", return_json=True
        )

    # POST
    def daily_fracked_feet(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/dailyfrackedfeet", payload=payload, return_json=True
        )

    def long_term_forecast(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/longtermforecast", payload=payload, return_json=True
        )

    def well_completion(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/completions", payload=payload, return_json=True
        )

    def ducs_by_operator(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/ducsbyoperator", payload=payload, return_json=True
        )

    def frac_crews(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/fraccrews", payload=payload, return_json=True
        )

    # @apply_implicit_filters(implicit_filter_type="sub_region", target_function="ProductionByWell")
    def production_by_well(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/productionbywell", payload=payload, return_json=True
        )

    def rigs(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/rigs", payload=payload, return_json=True
        )

    # @apply_implicit_filters(implicit_filter_type="sub_region", target_function="Well")
    def wells(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/wells", payload=payload, return_json=True
        )

    @apply_implicit_filters(
        implicit_filter_type="sub_region", target_function="ShortTermForecast"
    )
    def short_term_forecast(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/shorttermforecast", payload=payload, return_json=True
        )

    # @apply_implicit_filters(implicit_filter_type="sub_region", target_function="ShortTermForecastHistory")
    def short_term_forecast_history(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        # raise ServiceUnavailableError("503 error - Service currently under maintenance")
        return self.api_client.post(f"{self._base_uri}/v3/shorttermforecasthistory", payload=payload, return_json=True)

    # @apply_implicit_filters(implicit_filter_type="sub_region", target_function="ShortTermForecastDeclines")
    def short_term_forecast_declines(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/shorttermforecastdeclines",
            payload=payload,
            return_json=True,
        )

    def short_term_forecast_aggregated_history(
        self, payload: ApiPayload = ApiPayload()
    ) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/stfaggregatedhistory", payload=payload, return_json=True
        )

    def daily_production(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/dailyproduction", payload=payload, return_json=True
        )

    # @apply_implicit_filters(implicit_filter_type="sub_region", target_function="pipelinescrapes")
    def pipeline_scrapes(self, payload: ApiPayload = ApiPayload()) -> pandas.DataFrame:
        return self.api_client.post(
            f"{self._base_uri}/v3/pipelinescrapes", payload=payload, return_json=True
        )
