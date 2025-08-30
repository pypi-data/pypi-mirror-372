import logging
from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, field_validator, root_validator

from synmax.hyperion import ApiPayload

logger = logging.getLogger("API_CLIENT")

class ApiParams(BaseModel):
    pagination_start: Optional[int] = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    forecast_run_date: Optional[str] = None
    production_month: Optional[List[int]] = None
    first_production_month_start: Optional[str] = None
    first_production_month_end: Optional[str] = None
    state_code: Optional[List[str]] = None
    region: Optional[List[str]] = None
    sub_region: Optional[List[str]] = None
    county: Optional[List[str]] = None
    operator: Optional[List[str]] = None
    api: Optional[List[int]] = None
    aggregate_by: Optional[List[str]] = None
    aggregation_type: Optional[str] = None
    service_company: Optional[List[str]] = None
    frac_class: Optional[List[str]] = None
    rig_class: Optional[List[str]] = None
    completion_class: Optional[List[str]] = None
    category: Optional[List[str]] = None
    modeled: Optional[bool] = None
    state_reported: Optional[bool] = None

    @field_validator('end_date', 'first_production_month_end', 'first_production_month_start', 'start_date', mode='before')
    def validate_date(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"{v} must be a valid date in 'YYYY-MM-DD' format.")
        return v

    @field_validator('state_code', mode='before')
    def validate_state_code(cls, v):
        valid_state_codes = {'TX', 'PA', 'OH', 'OK', 'WV', 'NM', 'ND', 'CO', 'LA', 'WY'}
        if v:
            if not isinstance(v, list):
                v = [v]
            for code in v:
                if code not in valid_state_codes:
                    raise ValueError(f"{code} is not a valid state code.")
        return v

    @field_validator('region', mode='before')
    def validate_region(cls, v):
        valid_regions = {'Gulf', 'West', 'NorthEast', 'MidWest', 'Canada'}
        if v:
            if not isinstance(v, list):
                v = [v]
            for region in v:
                if region not in valid_regions:
                    raise ValueError(f"{region} is not a valid region.")
        return v

    @field_validator('sub_region', mode='before')
    def validate_sub_region(cls, v):
        valid_sub_regions = {
            'Central - TX', 'North - TX', 'South - TX', 'West - TX', 'Haynesville - TX',
            'Haynesville - LA', 'N LA', 'S LA', 'SW PA', 'NE PA', 'OH', 'WV', 'Wyoming',
            'North Dakota', 'Colorado wo SJ', 'NewMexico', 'Permian-NM', 'OK'
        }
        if v:
            if not isinstance(v, list):
                v = [v]
            for sub_region in v:
                if sub_region not in valid_sub_regions:
                    raise ValueError(f"{sub_region} is not a valid sub-region.")
        return v

    @field_validator('start_date', 'first_production_month_start')
    def validate_start_date(cls, v):
        if v:
            start = datetime.strptime(v, "%Y-%m-%d")
            if start > datetime.now() + timedelta(days=90):
                raise ValueError("start_date cannot be more than 3 months into the future.")
        return v

    @root_validator(pre=True)
    def validate_date_range(cls, values):
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        first_production_month_start = values.get('first_production_month_start')
        first_production_month_end = values.get('first_production_month_end')

        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start >= end:
                raise ValueError("start_date must be less than end_date.")

        if first_production_month_start and first_production_month_end:
            start = datetime.strptime(first_production_month_start, "%Y-%m-%d")
            end = datetime.strptime(first_production_month_end, "%Y-%m-%d")
            if start >= end:
                raise ValueError("first_production_month_start must be less than first_production_month_end.")

        return values

class InitializeAPI:
    def __init__(self, access_token: str, params: ApiPayload):
        """
        Initialize the API client with the provided access token and parameters.
        """
        self.params = self.convert_to_dict(params)  # Convert ApiPayload to dictionary
        self.params = ApiParams(**self.params)  # Use Pydantic model for validation
        logger.info("ApiClient initialized successfully.")

    def convert_to_dict(self, api_payload: ApiPayload) -> dict:
        """
        Convert ApiPayload object to dictionary.
        """
        return {
            "pagination_start": api_payload.pagination_start,
            "start_date": api_payload.start_date.strftime("%Y-%m-%d") if api_payload.start_date else None,
            "end_date": api_payload.end_date.strftime("%Y-%m-%d") if api_payload.end_date else None,
            "forecast_run_date": api_payload.forecast_run_date.strftime("%Y-%m-%d") if api_payload.forecast_run_date else None,
            "production_month": api_payload.production_month,
            "first_production_month_start": api_payload.first_production_month_start.strftime("%Y-%m-%d") if api_payload.first_production_month_start else None,
            "first_production_month_end": api_payload.first_production_month_end.strftime("%Y-%m-%d") if api_payload.first_production_month_end else None,
            "state_code": api_payload.state_code,
            "region": api_payload.region,
            "sub_region": api_payload.sub_region,
            "county": api_payload.county,
            "operator": api_payload.operator,
            "api": api_payload.api,
            "aggregate_by": api_payload.aggregate_by,
            "aggregation_type": api_payload.aggregation_type,
            "service_company": api_payload.service_company,
            "frac_class": api_payload.frac_class,
            "rig_class": api_payload.rig_class,
            "completion_class": api_payload.completion_class,
            "category": api_payload.category,
            "modeled": api_payload.modeled,
            "state_reported": api_payload.state_reported,
        }

    def create_payload(self) -> ApiPayload:
        """
        Create an ApiPayload object using the provided parameters.
        """
        logger.debug("Creating ApiPayload with provided parameters.")
        payload = ApiPayload(**self.params.dict())
        logger.info("ApiPayload created successfully.")
        return payload