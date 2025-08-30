from pydantic import BaseModel
from typing import Optional, List, Union, Literal
from datetime import date


class PayloadModelBase(BaseModel):
    pagination_start: Optional[int] = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    forecast_run_date: Optional[date] = None
    production_month: Optional[Union[int, List[int]]] = None
    first_production_month_start: Optional[date] = None
    first_production_month_end: Optional[date] = None
    state_code: Optional[Union[str, List[str]]] = None
    region: Optional[Union[str, List[str]]] = None
    sub_region: Optional[Union[str, List[str]]] = None
    county: Optional[Union[str, List[str]]] = None
    operator: Optional[Union[str, List[str]]] = None
    api: Optional[Union[int, List[int]]] = None
    aggregate_by: Optional[Union[str, List[str]]] = None
    aggregation_type: Optional[Literal["sum", "average", "count"]] = None
    service_company: Optional[Union[str, List[str]]] = None
    frac_class: Optional[Union[str, List[str]]] = None
    rig_class: Optional[Union[str, List[str]]] = None
    completion_class: Optional[Union[str, List[str]]] = None
    category: Optional[Union[str, List[str]]] = None
    modeled: Optional[bool] = None
    state_reported: Optional[bool] = None
    start_date_min: Optional[date] = None
    start_date_max: Optional[date] = None
    end_date_min: Optional[date] = None
    end_date_max: Optional[date] = None

    # nerc_id: Optional[Union[str, List[str]]] = None

    def payload(self, pagination_start=None):
        # just intercept the payload calls so they aren't relayed to `object`
        pass
