import logging
from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("SIMULATION_INPUTS")


class StudioInputs(BaseModel):
    num_wells_list: Optional[List[Optional[int]]] = []
    num_fracs_list: Optional[List[Optional[int]]] = []
    future_production: Optional[List[Optional[float]]] = []
    gas_exp_params: Optional[List[Optional[float]]] = None
    oil_exp_params: Optional[List[Optional[float]]] = None
    num_til_days: Optional[int] = 0
    api_params: Optional[dict] = {}
    simulation_start: Optional[str] = None
    well_efficiency_factor: Optional[float] = 1
    crew_efficiency_factor: Optional[float] = 1
    well_frac_ratio: Optional[float] = None
    simulation_type: Optional[str] = None
    production_type: Optional[str] = None
    sim_duration: Optional[int] = None

    @field_validator("simulation_type")
    def validate_simulation_type(cls, v):
        if v not in ["Forward", "Inverse", "Breakeven"]:
            raise ValueError("simulation_type must be 'Forward', 'Inverse', or 'Breakeven'.")
        return v

    @field_validator("production_type")
    def validate_production_type(cls, v, values):
        if values.data.get("simulation_type") in ["Inverse", "Breakeven"] and v not in ["Gas", "Oil"]:
            raise ValueError("production_type must be 'Gas' or 'Oil' for Inverse or Breakeven simulations.")
        return v

    @field_validator("future_production")
    def validate_future_production(cls, v, values):
        if values.data.get("simulation_type") == "Inverse" and not v:
            raise ValueError("future_production cannot be empty for Inverse simulations.")
        return v

    @field_validator("num_til_days")
    def validate_num_til_days(cls, v):
        if v is not None and v <= 0:
            raise ValueError("num_til_days must be positive.")
        return v

    @field_validator("num_wells_list", "num_fracs_list", "future_production", mode="before")
    def validate_positive_list_items(cls, v):
        if v is not None:
            for item in v:
                if item is not None and item <= 0:
                    raise ValueError("All elements of the list must be positive if they are not None.")
        return v

    @field_validator("gas_exp_params", "oil_exp_params")
    def validate_exp_params(cls, v):
        if v is not None:
            if len(v) != 3:
                raise ValueError("exp_params must have exactly three values: a, b, and c.")
            a, b, c = v
            if a is not None and a <= 0:
                raise ValueError("Parameter 'a' must be positive if it is not None.")
            if b is not None and b >= 0:
                raise ValueError("Parameter 'b' must be negative if it is not None.")
            if c is not None and c < 0:
                raise ValueError("Parameter 'c' must be non-negative if it is not None.")
            if a is not None and c is not None and a <= c:
                raise ValueError("Parameter 'a' must be greater than 'c' if both are not None.")
        return v

class StudioInputsHandler:
    def __init__(self, input_dict: dict):
        logger.debug("Initializing StudioInputsHandler with input dictionary.")
        self.params = StudioInputs(**input_dict)

        max_length = max(
            len(self.params.num_wells_list),
            len(self.params.num_fracs_list),
            len(self.params.future_production),
        )

        if not self.params.num_wells_list:
            self.params.num_wells_list = [None] * max_length
        if not self.params.num_fracs_list:
            self.params.num_fracs_list = [None] * max_length
        if not self.params.future_production:
            self.params.future_production = [None] * max_length

        num_months_list = list(range(1, max_length + 1))

        if (
            len(self.params.num_wells_list) != len(self.params.num_fracs_list)
            or len(self.params.num_fracs_list) != len(self.params.future_production)
        ):
            logger.error("num_wells_list, num_fracs_list, and future_production must all be the same length.")
            raise ValueError("num_wells_list, num_fracs_list, and future_production must all be the same length.")

        logger.debug("Validated input lists length.")

        self.api_params = self.params.api_params
        self.num_wells_list = self.params.num_wells_list
        self.num_months_list = num_months_list
        self.num_fracs_list = self.params.num_fracs_list
        self.gas_exp_params = self.params.gas_exp_params
        self.oil_exp_params = self.params.oil_exp_params
        self.num_til_days = self.params.num_til_days
        self.future_production = self.params.future_production
        self.simulation_start = self.params.simulation_start
        self.well_efficiency_factor = self.params.well_efficiency_factor
        self.crew_efficiency_factor = self.params.crew_efficiency_factor
        self.well_frac_ratio = self.params.well_frac_ratio
        self.simulation_type = self.params.simulation_type
        self.production_type = self.params.production_type
        self.sim_duration = self.params.sim_duration

        logger.debug("StudioInputsHandler initialized successfully.")

class WellFracRange(BaseModel):
    wells_range: List[int]
    frac_range: List[int]
    til_range: List[int]

    @field_validator("wells_range", "frac_range", "til_range")
    def validate_range(cls, v):
        if len(v) != 2 or v[0] <= 0 or v[1] <= 0 or v[0] > v[1]:
            raise ValueError("Invalid range: must be positive and the first element must be less than the second element")
        return v


class SimulationInputs(BaseModel):
    simulation_start: Optional[str] = Field(
        default_factory=lambda: datetime.today().replace(day=1).strftime("%Y-%m-%d")
    )
    well_efficiency_factor: Optional[float] = 1
    crew_efficiency_factor: Optional[float] = 1
    well_frac_ratio: Optional[float] = None
    gas_exp_params: Optional[List[Optional[float]]] = None
    oil_exp_params: Optional[List[Optional[float]]] = None
    simulation_type: Optional[str] = None
    production_type: Optional[str] = None
    num_simulations: Optional[int] = 1
    well_frac_ranges: Optional[List[Dict[str, Optional[List[int]]]]] = None

    @field_validator("simulation_start")
    def validate_date(cls, v):
        if v is not None:
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {v}. Expected format: YYYY-MM-DD")
        return v

    @field_validator(
        "well_efficiency_factor", "crew_efficiency_factor", "well_frac_ratio"
    )
    def validate_positive_number(cls, v):
        if v is not None and v <= 0:
            raise ValueError(f"Value must be positive: {v}")
        return v

    @field_validator("gas_exp_params", "oil_exp_params")
    def validate_exponential_params(cls, v):
        if v is not None:
            if len(v) != 3:
                raise ValueError(
                    "exp_params must have exactly three values: a, b, and c."
                )
            a, b, c = v
            if a is not None and a <= 0:
                raise ValueError("Parameter 'a' must be positive if it is not None.")
            if b is not None and b >= 0:
                raise ValueError("Parameter 'b' must be negative if it is not None.")
            if c is not None and c <= 0:
                raise ValueError("Parameter 'c' must be positive if it is not None.")
        return v

    @field_validator("well_frac_ranges")
    def validate_well_frac_ranges(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("well_frac_ranges must be a list of dictionaries")
            for params in v:
                if not isinstance(params, dict):
                    raise ValueError("Each item in well_frac_ranges must be a dictionary")
                WellFracRanges(**params)  # Validate each dictionary
        return v


class WellFracRanges(BaseModel):
    wells_range: Optional[List[int]] = None
    frac_range: Optional[List[int]] = None
    til_range: Optional[List[int]] = None

    @field_validator("wells_range", "frac_range", "til_range")
    def validate_range(cls, v):
        if v is not None:
            if len(v) != 2 or v[0] <= 0 or v[1] <= 0 or v[0] > v[1]:
                raise ValueError(
                    "Invalid range: must be positive and the first element must be less than the second element"
                )
        return v


class SimulationInputsHandler:
    def __init__(self, nested_params: dict):
        """
        Initialize SimulationInputsHandler with the provided nested parameters.
        """
        logger.debug("Initializing SimulationInputsHandler with provided parameters.")

        # Extract and validate all parameters
        self.simulation_inputs = SimulationInputs(**nested_params)

        logger.debug(
            f"Parameters validated: simulation_start={self.simulation_inputs.simulation_start}, "
            f"well_efficiency_factor={self.simulation_inputs.well_efficiency_factor}, crew_efficiency_factor={self.simulation_inputs.crew_efficiency_factor}, "
            f"well_frac_ratio={self.simulation_inputs.well_frac_ratio}, gas_exp_params={self.simulation_inputs.gas_exp_params}, oil_exp_params={self.simulation_inputs.oil_exp_params}, "
            f"well_frac_ranges={self.simulation_inputs.well_frac_ranges}"
        )

        # Initialize well frac ranges
        self.well_frac_ranges = self.simulation_inputs.well_frac_ranges or []
        self.simulation_duration = len(self.well_frac_ranges)
        self.simulation_type = self.simulation_inputs.simulation_type
        self.production_type = self.simulation_inputs.production_type
        self.num_simulations = self.simulation_inputs.num_simulations
        self.gas_exp_params = self.simulation_inputs.gas_exp_params
        self.oil_exp_params = self.simulation_inputs.oil_exp_params
        self.simulation_start = self.simulation_inputs.simulation_start
        self.well_efficiency_factor = self.simulation_inputs.well_efficiency_factor
        self.crew_efficiency_factor = self.simulation_inputs.crew_efficiency_factor
        self.well_frac_ratio = self.simulation_inputs.well_frac_ratio
        logger.info(
            f"SimulationInputsHandler initialized successfully with duration: {self.simulation_duration} months."
        )
