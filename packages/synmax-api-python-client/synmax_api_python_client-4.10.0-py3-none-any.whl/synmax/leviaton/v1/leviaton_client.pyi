from typing import Literal, Union
from synmax.openapi.client import Result
from datetime import date
class LeviatonApiClient:
    def healthcheck(self) -> Result:
        """Returns the health status of the API"""
        ...
    def vessels(self,imos: list[int] = ...,mmsis: list[int] = ...,names: list[str] = ...,polygons: list[list[list[float]]] = ...) -> Result:
        """Returns detailed information about vessels, their position, and next most likely destination."""
        ...
    def vessels_details(self,imos: list[int] = ...,mmsis: list[int] = ...,names: list[str] = ...,polygons: list[list[list[float]]] = ...) -> Result:
        """Returns detailed information about vessels, their position, and detailed predictions incl. prediction scores about their next destination."""
        ...
    def vessels_history(self,imos: list[int] = ...,mmsis: list[int] = ...,names: list[str] = ...,polygons: list[list[list[float]]] = ...,from_timestamp: str = ...,to_timestamp: str = ...) -> Result:
        """Returns detailed information about vessel activity and their position history."""
        ...
    def transactions(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,from_timestamp: str = ...,to_timestamp: str = ...) -> Result:
        """Returns a detailed list of historic and forecasted future transactions, including the volume, vessels, and terminals involved. The data is refreshed every hour."""
        ...
    def transactions_details(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,from_timestamp: str = ...,to_timestamp: str = ...) -> Result:
        """Returns a list of transaction details with multi-step ahead predicted transactions including prediction scores. The data is refreshed every hour."""
        ...
    def transactions_history(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,from_timestamp: str = ...,to_timestamp: str = ...) -> Result:
        """Returns a history of transactions, including the volume, vessels, and terminals involved"""
        ...
    def transactions_forecast(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...) -> Result:
        """Returns a list of forecasted transactions, including the volume, vessels, and terminals involved. The forecasts are refreshed on an hourly basis."""
        ...
    def transactions_forecast_details(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...) -> Result:
        """Returns a list of forecasted transactions, including a detailed route prediction breakdown. The forecasts are refreshed on an hourly basis."""
        ...
    def transactions_forecast_history(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,forecast_run_at: str) -> Result:
        """Returns historic versions of Leviaton's forecasted transactions, including the volume, vessels, and terminals involved. Fetch a *forecast_run_at_timestamp* using /forecast_run_at_timestamps endpoints and use that date to view a historic version of our forecasted transactions."""
        ...
    def transactions_forecast_history_details(self,imos: list[int] = ...,origin_terminals: list[str] = ...,origin_terminal_ids: list[str] = ...,origin_countries: list[str] = ...,origin_country_codes: list[str] = ...,origin_regions: list[str] = ...,origin_polygons: list[list[list[float]]] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_regions: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,forecast_run_at: str) -> Result:
        """Returns a version of Leviaton's detailed history of forecasted transactions, including a detailed route prediction breakdown. Fetch a *forecast_run_at_timestamp* using /forecast_run_at_timestamps endpoints and use that date to view a historic version of our forecasted transactions."""
        ...
    def volume_flows(self,destination_terminals: list[str] = ...,destination_terminal_ids: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,destination_regions: list[str] = ...,loading_origin_terminals: list[str] = ...,loading_origin_terminal_ids: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,from_timestamp: str = ...,to_timestamp: str = ...,forecast_run_at: str) -> Result:
        """Returns LNG volumes transferred to specified terminals or countries over a given time period.
The volume_flows endpoint calculates the LNG volume transferred to a set of destination terminals/countries (and optionally from a set of origin terminals/countries) for a given time range. For historical time periods this is simply the observed number of transactions that occurred at the destinations.
For future time periods, forecasted volumes are calculated. Forecasted volumes are calculated using the route_score_weighted_volume field from the transactions/forecast endpoint. The route_score_weighted_volume is the volume of a potential transaction multiplied by the likelihood of that transaction occurring. Forecast volumes are the sum of the route_score_weighted_volume for the destinations in the given time period. Note that this means partial transactions are included in the forecast volume. Uncertainties in the forecast volume are estimated using our uncertainty in the forecast transaction timestamp.

- Historical data:

  - Shows actual observed transaction volumes.

- Forecasted data:

  - Predicts future volumes based on:

    - Potential vessel arrivals and their cargo volumes
    - Probability of each arrival occurring
    - Arrival time uncertainties
"""
        ...
    def volume_flows_history(self,destination_terminals: list[str] = ...,destination_countries: list[str] = ...,destination_country_codes: list[str] = ...,destination_polygons: list[list[list[float]]] = ...,destination_regions: list[str] = ...,loading_origin_terminals: list[str] = ...,loading_origin_countries: list[str] = ...,loading_origin_country_codes: list[str] = ...,loading_origin_regions: list[str] = ...,loading_origin_polygons: list[list[list[float]]] = ...,transaction_type: Literal['loading', 'offloading'] = ...,from_timestamp: str = ...,to_timestamp: str = ...) -> Result:
        """Returns historic versions of Leviaton's LNG volumes transferred to specified terminals or countries over a given time period.
The volume_flows endpoint calculates the LNG volume transferred to a set of destination terminals/countries (and optionally from a set of origin terminals/countries) for a given time range. For historical time periods this is simply the observed number of transactions that occurred at the destinations.
For future time periods, forecasted volumes are calculated. Forecasted volumes are calculated using the route_score_weighted_volume field from the transactions/forecast endpoint. The route_score_weighted_volume is the volume of a potential transaction multiplied by the likelihood of that transaction occurring. Forecast volumes are the sum of the route_score_weighted_volume for the destinations in the given time period. Note that this means partial transactions are included in the forecast volume. Uncertainties in the forecast volume are estimated using our uncertainty in the forecast transaction timestamp.

- Historical data:

  - Shows actual observed transaction volumes.

- Forecasted data:

  - Predicts future volumes based on:

    - Potential vessel arrivals and their cargo volumes
    - Probability of each arrival occurring
    - Arrival time uncertainties
"""
        ...
    def terminals(self,countries: list[str] = ...,regions: list[str] = ...,names: list[str] = ...,unrefcodes: list[str] = ...,ids: list[str] = ...,polygons: list[list[list[float]]] = ...,category: Literal['Liquefaction', 'Regasification'] = ...) -> Result:
        """Returns a list of detailed information about all liquefaction and regasification LNG terminals."""
        ...
    def countries(self,names: list[str] = ...,unrefcodes: list[str] = ...,ids: list[str] = ...,polygons: list[list[list[float]]] = ...) -> Result:
        """Returns a list of ISO 3166 country names, ISO 3166 Alpha-2 country codes, and the countries polygons including their EEZ (except United States of America -> USA). Any of these values can be used to narrow down API requests on other endpoints."""
        ...
    def regions(self,names: list[str] = ...,ids: list[str] = ...,polygons: list[list[list[float]]] = ...,include_polygons: bool = ...) -> Result:
        """Returns a list of polygons commonly used regions in an LNG context. These polygons can be used to narrow down results on other endpoints. Example polygons are "JKTC"
"North West Europe", "Europe w/o Norway",  "Europe w. Turkey", "North America",
"South America", "Middle East", "West Africa", "South East Asia", "South Asia",
"Asia w/o Middle East"
"""
        ...
    def forecast_run_at_timestamps(self) -> Result:
        """Returns the distinct timestamps and the IDs of all previous forecast runs"""
        ...