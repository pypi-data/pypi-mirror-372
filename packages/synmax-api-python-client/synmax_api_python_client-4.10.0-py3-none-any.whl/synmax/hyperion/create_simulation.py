import dataclasses as dc
import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from typing import Literal

import pandas as pd
import requests
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from pydantic import BaseModel

from synmax.hyperion import ApiPayload, HyperionApiClient
from synmax.hyperion.process_api import InitializeAPI
from synmax.hyperion.process_inputs import SimulationInputsHandler, StudioInputsHandler

logger = logging.getLogger("CREATE_SIMULATION")

@dc.dataclass
class SimulationResults:
    request_id: str
    studio_inputs_df: pd.DataFrame
    input_curve_df: pd.DataFrame
    user_forecast_df: pd.DataFrame
    num_wells_df: pd.DataFrame
    num_fracs_df: pd.DataFrame

class Production_Simulation:
    """
    The Production_Simulation class is used to run simulations using the Hyperion API.

    There are two main methods to run simulations:
    - run_simulation(): This method runs a single simulation using the provided parameters.
    - run_multiple_simulations(): This method runs multiple simulations using the provided parameters.

    In general, the steps to run a simulation are as follows:
    1. Initialize the Hyperion API client.
    ` client = HyperionApiClient(access_token="your_access_token")`
    2. Initialize the Production_Simulation class with the client and a payload.
    ` payload = ApiPayload(start_date="2020-06-01", sub_region=["West - TX"])`
    Note that the payload is used to restrict the production data that will be used for the simulation. For example, if you only want to use production data from New Mexico, you can set the payload to only include New Mexico production.  Also, the start date defines the history that will be used to define the type curve, if one is not specificied.
    3. Define the parameters for the simulation.
    ```
        params = {
            "simulation_type": "Forward",
            "num_wells_list": [450, 500] * 12,
            "num_til_days": 30,
            "efficiency_factor": 1.1,
            "well_frac_ratio": 3,
            "simulation_start": "2024-11-01",
        }
    ```
    4. Run the simulation using the run_simulation() or run_multiple_simulations() method.
    ` results = production_simulation.run_simulation(params)`
    5. The results will be returned as a SimulationResults dataclass, which contains DataFrames for the studio inputs, input curve, user forecast, number of wells, and number of fracs.
    6. Different simulations can be run by changing the parameters in the params dictionary, and recalling the run_simulation() or run_multiple_simulations() method.  This will use the same "base data" from the payload, but will run the simulation with the new parameters.


    see @synmax/hyperion/process_inputs/StudioInputs or @synmax/hyperion/process_inputs/SimulationInputsHandler for details on the parameters to be provided for each type of simulation"""


    def __init__(self, client: HyperionApiClient, payload: ApiPayload):
        logger.debug("Initializing CreateSimulation with provided client, payload.")
        self.client = client
        self.payload = self._process_payload(payload)
        logging.info(f"Processed payload: {self.payload}")
        self.executor = ThreadPoolExecutor(max_workers=5)
        logging.info("Querying data for simulation. This may take a few minutes.")
        self._send_defaults_request(self.payload)
        self.simulation_defaults = self._clean_and_rename_defaults(self.defaults)
        logger.info("CreateSimulation initialized successfully.")

    def _clean_and_rename_defaults(self, defaults: dict) -> dict:
        cleaned_defaults = {
            "average_active_frac_crews": round(defaults.get("avg_fracs", 0), 2),
            "average_wells_completed": round(defaults.get("avg_wells", 0), 2),
            "last_gas_production": round(defaults.get("avg_gas", 0), 2),
            "last_oil_production": round(defaults.get("avg_oil", 0), 2),
            "well_frac_ratio": round(defaults.get("avg_well_frac_ratio", 0), 2),
            "gas_exp_params": [
                round(defaults.get("gas_ipr_def", 0), 2),
                round(defaults.get("gas_decl_def", 0), 2),
                round(defaults.get("gas_min_def", 0), 2)
            ],
            "oil_exp_params": [
                round(defaults.get("oil_ipr_def", 0), 2),
                round(defaults.get("oil_decl_def", 0), 2),
                round(defaults.get("oil_min_def", 0), 2)
            ],
            "operator_breakdown": sorted(
                [{"operator": k, "value": v} for k, v in defaults.get("operator_breakdown", {}).items()],
                key=lambda x: x['value'],
                reverse=True
            )
        }
        return cleaned_defaults

    def _process_payload(self, payload: ApiPayload) -> ApiPayload:
        logger.debug("Processing payload through InitializeAPI.")
        api_initializer = InitializeAPI(access_token=self.client.access_key, params=payload)
        processed_payload = api_initializer.params
        logger.debug(f"Processed payload: {processed_payload}")
        return processed_payload


    @staticmethod
    def _process_params(params: dict) -> SimulationInputsHandler | StudioInputsHandler:
        logger.debug("Processing params dictionary.")
        if "well_frac_ranges" in params:
            logger.debug("Detected SimulationInputs structure.")
            simulation_inputs_handler = SimulationInputsHandler(params)
            logger.debug(f"SimulationInputsHandler created: {simulation_inputs_handler}")
            return simulation_inputs_handler
        else:
            logger.debug("Detected StudioInputs structure.")
            if params['simulation_type'] == 'Flat':
                params['simulation_type'] = 'Breakeven'
            studio_inputs_handler = StudioInputsHandler(params)
            logger.debug(f"StudioInputsHandler created: {studio_inputs_handler}")
            return studio_inputs_handler

    def _build_simulation_payload(self, input_obj: SimulationInputsHandler | StudioInputsHandler) -> dict:
        """
        Build the payload to send to the simulation API from an inputs handler.

        Args:
            input_obj (SimulationInputsHandler | StudioInputsHandler): The inputs handler object.

        Returns:
            dict: The payload to send to the simulation API.
        """
        logger.debug("Building simulation payload.")
        common_payload = {
            "gas_exp_params": input_obj.gas_exp_params,
            "oil_exp_params": input_obj.oil_exp_params,
            "api_params": self.payload.model_dump(),
            "simulation_start": input_obj.simulation_start,
            "well_efficiency_factor": input_obj.well_efficiency_factor,
            "crew_efficiency_factor": input_obj.crew_efficiency_factor,
            "well_frac_ratio": input_obj.well_frac_ratio,
            "simulation_type": input_obj.simulation_type,
            "access_token": self.client.access_key,
        }
        logger.debug(f"Common payload: {common_payload}")

        if input_obj.simulation_type == "Forward":
            service_payload = {
                **common_payload,
                "num_wells_list": input_obj.num_wells_list,
                "num_fracs_list": input_obj.num_fracs_list,
            }
        elif input_obj.simulation_type == "Inverse":
            service_payload = {
                **common_payload,
                "future_production": input_obj.future_production,
                "production_type": input_obj.production_type,
            }
        elif input_obj.simulation_type == "Breakeven":
            service_payload = {
                **common_payload,
                "production_type": input_obj.production_type,
                "sim_duration": input_obj.sim_duration,
            }
        elif input_obj.simulation_type == "ForwardSimulation":
            service_payload = {
                **common_payload,
                "production_type": input_obj.production_type,
                "num_simulations": input_obj.num_simulations,
                "well_frac_ranges": input_obj.well_frac_ranges,
            }
        else:
            raise ValueError("Invalid simulation type. Must be one of 'Forward', 'Inverse', 'Breakeven', or 'ForwardSimulation'.")

        logger.debug(f"Service payload: {service_payload}")
        return service_payload


    def _run_simulation_core(self, service_payload: dict) -> dict[SimulationResults] | SimulationResults:
        service_payload["request_id"] = self.request_id = str(uuid.uuid4())
        logger.info(f"Simulations request sent with request ID: {self.request_id}.")
        return self._send_simulation_request(service_payload)

    def _send_simulation_request(self, data: dict) -> dict[SimulationResults] | SimulationResults:
        logger.debug("Sending simulation request.")
        url = "https://production-studio-1050800409605.us-central1.run.app/run-simulation"
        headers = {
            "Content-Type": "application/json"
        }
        cleaned_payload = {k: v for k, v in self.payload.model_dump().items() if v is not None and k != 'pagination_start'}
        payload = {**data, "access_token": self.client.access_key, "api_params": cleaned_payload}
        payload = convert_dates_to_strings(payload)
        json_data = json.dumps(payload, cls=DateTimeEncoder)

        response = requests.post(url, headers=headers, data=json_data)
        self.status_code = response.status_code
        self.response = response.text

        logger.debug(f"Request ID: {self.request_id} - Request: {json_data}")
        logger.debug(f"Request ID: {self.request_id} - Response: {self.response}")

        if response.ok:
            try:
                self.results = json.loads(self.response)
                logger.info("Simulation request successful")
                logger.info("Simulation request successful")
                return self._process_results(data["request_id"])
            except json.JSONDecodeError:
                self.results = None
                self.error = "Failed to parse JSON response"
                logger.error(self.error)
        else:
            self.results = None
            self.error = f"Request failed with status code {self.status_code} and response: {response.reason}"
            logger.error(self.error)

        return None

    def _send_defaults_request(self, data: dict) -> None:
        logger.debug("Sending defaults request.")
        url = "https://production-studio-1050800409605.us-central1.run.app/calculate_defaults"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {'api_params': data, 'access_token': self.client.access_key}
        payload = convert_dates_to_strings(payload)
        json_data = json.dumps(payload, cls=DateTimeEncoder)

        response = requests.post(url, headers=headers, data=json_data)
        self.status_code = response.status_code
        self.response = response.text

        if response.ok:
            try:
                self.defaults = json.loads(self.response)
                logger.info("Defaults request successful")
            except json.JSONDecodeError:
                self.defaults = None
                self.error = "Failed to parse JSON response"
                logger.error(self.error)
        else:
            self.defaults = None
            self.error = f"Request failed with status code {self.status_code} and response: {response.reason}"
            logger.error(self.error)

    def _process_results(self, request_id: str) -> dict[str, SimulationResults] | SimulationResults:
        """
        Get the returned JSON and convert it to DataFrames in SimulationResults.

        Args:
            request_id (str): The request ID for the simulation.

        Returns:
            dict[str, SimulationResults] or SimulationResults: A dataclass containing the DataFrames for the simulation results (for forward and reverse), or a dict of SimulationResults if multiple.
        """
        if not self.results:
            logger.error("No results to process.")
            return None

        try:
            ret_val = {}
            for key, value in self.results.items():
                logger.debug(f"Processing results for simulation {key}")

                # Convert JSON data to DataFrames
                studio_inputs_df = pd.DataFrame([value['studio_inputs']])
                input_curve_df = pd.DataFrame(value['input_curve']['coordinate_values'])

                # Combine all keys in user_forecast into a single DataFrame with a column for the keys
                user_forecast_data = []
                for forecast in value['user_forecast']:
                    for coordinate in forecast['coordinate_values']:
                        coordinate['first_production_month'] = forecast['first_production_month']
                        user_forecast_data.append(coordinate)
                user_forecast_df = pd.DataFrame(user_forecast_data)

                num_wells_historical_df = pd.DataFrame(value['num_wells']['historical'])
                num_wells_historical_df['source'] = 'historical'
                num_wells_simulated_df = pd.DataFrame(value['num_wells']['simulated'])
                num_wells_simulated_df['source'] = 'simulated'
                num_wells_df = pd.concat([num_wells_historical_df, num_wells_simulated_df]).reset_index(drop=True)

                num_fracs_historical_df = pd.DataFrame(value['num_fracs']['historical'])
                num_fracs_historical_df['source'] = 'historical'
                num_fracs_simulated_df = pd.DataFrame(value['num_fracs']['simulated'])
                num_fracs_simulated_df['source'] = 'simulated'
                num_fracs_df = pd.concat([num_fracs_historical_df, num_fracs_simulated_df]).reset_index(drop=True)

                # Convert date columns to yyyy-mm-dd format
                date_columns = ['date', 'production_month', 'first_production_month']
                for df in [input_curve_df, user_forecast_df, num_wells_df, num_fracs_df]:
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

                # Store the DataFrames in the SimulationResults dataclass
                results = SimulationResults(
                    request_id=request_id,
                    studio_inputs_df=studio_inputs_df,
                    input_curve_df=input_curve_df,
                    user_forecast_df=user_forecast_df,
                    num_wells_df=num_wells_df,
                    num_fracs_df=num_fracs_df
                )
                ret_val[key] = results
                logger.debug(f"DataFrames created for simulation {key}")

            # Return a single SimulationResults object if only one result exists
            if len(ret_val) == 1:
                return ret_val.popitem()[1]
            return ret_val


        except Exception as e:
            self.error = str(e)
            logger.error(f"Error processing results: {self.error}")


        return None

    def run_simulation(self, params: dict) -> SimulationResults:
        logger.info(f"Running {params['simulation_type']} simulation.")
        input_obj = self._process_params(params)
        service_payload = self._build_simulation_payload(input_obj)
        return self._run_simulation_core(service_payload)

    def run_multiple_simulations(self, params: dict) -> dict[SimulationResults] | SimulationResults:
        logger.info("Running multiple simulations.")
        input_obj = self._process_params(params)
        service_payload = self._build_simulation_payload(input_obj)
        if 'num_simulations' in params:
            service_payload['num_simulations'] = params['num_simulations']
        else:
            raise ValueError("num_simulations key is missing in the params dictionary.")

        return self._run_simulation_core(service_payload)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)


def convert_dates_to_strings(data):
    if isinstance(data, dict):
        return {k: convert_dates_to_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_strings(v) for v in data]
    elif isinstance(data, (datetime, date)):
        return data.strftime('%Y-%m-%d')
    elif isinstance(data, BaseModel):
        return data.dict()
    else:
        return data