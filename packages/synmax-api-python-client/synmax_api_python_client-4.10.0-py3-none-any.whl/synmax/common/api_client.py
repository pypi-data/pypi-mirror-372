import asyncio
import logging
from typing import Optional, TypeAlias

import aiohttp
import pandas
import requests
import urllib3
from aioretry import (
    RetryInfo,
    # retry,
    # Tuple[bool, Union[int, float]]
    RetryPolicyStrategy,
)
from requests.adapters import HTTPAdapter
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
from tqdm import tqdm
from urllib3 import Retry

from synmax.common.model import PayloadModelBase

# disable insecure https request warnings
urllib3.disable_warnings()

# logging.basicConfig(level=logging.INFO) only the top-level application should do this
LOGGER = logging.getLogger(__name__)

_api_timeout = 60
_retry_limit = 10
PARALLEL_REQUESTS = 25

Request_data_t: TypeAlias = Optional[dict | list[tuple] | bytes]


class ApiClientBase:
    """Docstring for ApiClientBase

    :param access_token:
    :type access_token: str
    :param tqdm_disable:  (Default value = False)  Set to True to disable tqdm progress bar
    :type tqdm_disable: bool

    """
    def __init__(self, access_token:str, tqdm_disable:bool=False):
        self.access_key = access_token
        self.session = requests.Session()
        self.session.verify = False
        # update headers
        self.session.headers.update(self.headers)

        # HTTPAdapter
        retry_strategy = Retry(
            total=_retry_limit,
            backoff_factor=2,
            status_forcelist=[408, 500, 502, 503, 504, 505],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.tdqm_disable = tqdm_disable

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "access_key": self.access_key,
            "User-Agent": "Synmax-api-client/1.0.1/python",
        }

    @staticmethod
    def _return_response(response: requests.models.Response, return_json: bool = False) -> Optional[requests.models.Response | dict]:
        """
        Returns None if not ok or error, else returns response or json data, depending on the return_json flag.
        :param response: - the Repsonse object to test
        :param return_json: whether to return json data or not
        :return: the comnplete response object or json data, depending on the return_json flag
        """
        # response.raise_for_status()
        if not response.ok:
            # logging.error('Error in response. %s')
            return None

        if return_json:
            json_data = response.json()
            if "error" in json_data:
                # raise Exception(json_data['error'])
                logging.error(json_data["error"])
                return None
            return json_data

        return response


class ApiClient(ApiClientBase):

    # TODO - remove return_json in the function signature - it must always return_json for the funciotn to work properly.
    @retry(
        wait=wait_random_exponential(multiplier=15, min=20, max=60),
        before_sleep=before_sleep_log(LOGGER, logging.DEBUG),
        retry=retry_if_exception_type(requests.exceptions.HTTPError),
        stop=stop_after_attempt(_retry_limit),
        reraise=True,
    )
    def get(self, url: str, params: Request_data_t = None, return_json: bool = False, **kwargs) -> pandas.DataFrame:
        r"""Sends a GET request.


        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param return_json:
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        LOGGER.info(url)
        response = self.session.get(url, params=params, timeout=_api_timeout, **kwargs)

        if response.status_code == 429:
            resp_headers = response.headers
            LOGGER.warning(
                "Too Many Requests, rate_limit_request_count: %s",
                resp_headers.get("rate_limit_request_count"),
            )
            raise requests.exceptions.HTTPError("Too Many Requests")

        # it must always return_json for the funciotn to work properly.
        json_result = self._return_response(response, return_json=True)

        if json_result:
            df = pandas.DataFrame(json_result["data"])
            return df

        return None

    @retry(
        wait=wait_random_exponential(multiplier=15, min=20, max=60),
        before_sleep=before_sleep_log(LOGGER, logging.DEBUG),
        retry=retry_if_exception_type(requests.exceptions.HTTPError),
        stop=stop_after_attempt(_retry_limit),
        reraise=True,
    )
    def _post_retry(self, url: str, data: Request_data_t, timeout: int, **kwargs) -> requests.Response:
        response = self.session.post(url, data=data, timeout=timeout, **kwargs)

        if response.status_code == 429:
            resp_headers = response.headers
            LOGGER.warning(
                "Too Many Requests, rate_limit_request_count: %s",
                resp_headers.get("rate_limit_request_count"),
            )
            raise requests.exceptions.HTTPError("Too Many Requests")

        return response

    # TODO - remove return_json in the function signature - it must always return_json for the funciotn to work properly.
    def post(
        self, url, payload: PayloadModelBase = None, return_json=False, **kwargs
    ) -> pandas.DataFrame:
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param payload: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param return_json:
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        LOGGER.info("Payload data: %s", payload)

        data_list: list[dict] = []
        got_first_page = False
        total_count = -1
        pagination = {}

        with tqdm(
            desc=f"Querying API {url} pages", total=1, dynamic_ncols=True, miniters=0, disable=self.tdqm_disable
        ) as progress_bar:
            while (
                not got_first_page
                or total_count >= pagination["start"] + pagination["page_size"]
            ):
                progress_bar.refresh()
                response = self._post_retry(
                    url, data=payload.payload(), timeout=_api_timeout, **kwargs
                )
                if response.status_code == 401:
                    progress_bar.update()
                    LOGGER.error(response.text)
                    return pandas.DataFrame()
                #  it must always return_json for the funciotn to work properly.
                json_result = self._return_response(response, return_json=True)
                if isinstance(json_result, list):
                    return pandas.DataFrame(json_result)

                if json_result is None or json_result.get("pagination") is None:
                    LOGGER.warning("No data for the given filter criteria")
                    return pandas.DataFrame()

                pagination = json_result["pagination"]
                if not got_first_page:
                    total_count = pagination["total_count"]
                    total_pages = (
                        pagination["total_count"] // pagination["page_size"]
                    )
                    total_pages = (
                        total_pages + 1
                        if total_count % pagination["page_size"] > 0
                        else 0
                    )
                    progress_bar.reset(total=total_pages)
                    LOGGER.info(
                        "Total data size: %s, total pages to scan: %s",
                        total_count,
                        total_pages,
                    )
                    got_first_page = True

                data_list.extend(json_result["data"])
                payload.pagination_start = (
                    pagination["start"] + pagination["page_size"]
                )
                progress_bar.update()
        payload.pagination_start = 0
        LOGGER.info("Total response data: %s", len(data_list))
        df = pandas.DataFrame(data_list)
        return df

#everything below this line is dead, unused code  (async might be used in the future)
    def post_v1(
        self, url, payload: PayloadModelBase = None, return_json=False, **kwargs
    ) -> pandas.DataFrame:
        """Sends a POST request.

        :deprecated: Use :meth:`post` instead.  May be removed in the future

        :param url: URL for the new :class:`Request` object.
        :param payload: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param return_json:
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        LOGGER.info("Payload data: %s", payload)

        data_list: list[dict] = []

        response = self.session.post(url, data=payload.payload(), timeout=_api_timeout, **kwargs)
        json_result = self._return_response(response, return_json)
        data_list.extend(json_result["data"])

        pagination = json_result["pagination"]
        total_count = pagination["total_count"]
        total_pages = pagination["total_count"] // pagination["page_size"]
        total_pages = total_pages + 1 if total_count % pagination["page_size"] > 0 else 0

        # first page fetched in the above
        total_pages -= 1

        LOGGER.info("Total data size: %s, total pages to scan: %s", total_count, total_pages)

        with tqdm(
            desc=f"Querying API {url} pages",
            total=total_pages,
            dynamic_ncols=True,
            miniters=0,
            disable=self.tdqm_disable,
        ) as progress_bar:
            while total_count >= pagination["start"] + pagination["page_size"]:
                try:
                    progress_bar.refresh()
                    payload.pagination_start = pagination["start"] + pagination["page_size"]
                    response = self.session.post(url, data=payload.payload(), timeout=_api_timeout, **kwargs)
                    json_result = self._return_response(response, return_json)

                    pagination = json_result["pagination"]
                    data_list.extend(json_result["data"])
                    progress_bar.update()
                except Exception as e:
                    _ = e
                    pass
        payload.pagination_start = 0
        LOGGER.info("Total response data: %s", len(data_list))
        df = pandas.DataFrame(data_list)
        return df


def retry_policy(info: RetryInfo) -> RetryPolicyStrategy:
    """
    - It will always retry until succeeded
    - If fails for the first time, it will retry immediately,
    - If it fails again,
      aioretry will perform a 100ms delay before the second retry,
      200ms delay before the 3rd retry,
      the 4th retry immediately,
      100ms delay before the 5th retry,
      etc...
    """
    # LOGGER.info('retry_policy: since -> %s, going to sleep sec --> %s', info.since, info.fails)
    # return False, (info.fails - 1) % 3 * 0.1

    return False, info.fails


class ApiClientAsync(ApiClientBase):
    """
        :deprecated: use :class:`ApiClient` Maybe removed in the future
    """

    async def _post_async(
        self,
        url: str,
        payload: PayloadModelBase,
        data_list,
        progress_bar,
        page_size: int,
        total_pages: int,
        connector: aiohttp.TCPConnector,
    ):
        """

        :param url:
        :param payload:
        :param data_list:
        :param progress_bar:
        :param page_size:
        :param total_pages:
        :param connector:
        :return:
        """

        semaphore = asyncio.Semaphore(PARALLEL_REQUESTS)
        session = aiohttp.ClientSession(connector=connector, headers=self.headers)

        @retry(retry_policy)
        async def fetch_from_api(page_number):
            async with semaphore:
                _data = payload.payload(pagination_start=page_number * page_size)
                async with session.post(url, data=_data, timeout=_api_timeout, verify_ssl=False) as async_resp:
                    async_resp.raise_for_status()
                    json_data = await async_resp.json()
                    if "error" in json_data:
                        # raise Exception(json_data['error'])
                        logging.error(json_data["error"])
                        return None
                    return json_data

        tasks = [fetch_from_api(_page) for _page in range(1, total_pages + 1)]
        for task in asyncio.as_completed(tasks):
            try:
                json_result = await task
                if json_result:
                    data_list.extend(json_result["data"])
            except Exception as e:
                LOGGER.exception(e, exc_info=True)
            progress_bar.update()
        await session.close()

    def post(self, url, payload: PayloadModelBase = None, return_json: bool = False, **kwargs) -> pandas.DataFrame:
        r"""
        Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param payload: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param return_json:
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        LOGGER.info("Payload data: %s", payload)

        data_list: list[dict] = []

        with tqdm(
            desc=f"Querying API {url} pages", total=1, dynamic_ncols=True, miniters=0, disable=self.tdqm_disable
        ) as progress_bar:
            response = self.session.post(
                url, data=payload.payload(), timeout=_api_timeout, **kwargs
            )
            if response.status_code == 401:
                progress_bar.update()
                LOGGER.error(response.text)
                return pandas.DataFrame()

            json_result = self._return_response(response, return_json)
            pagination = json_result["pagination"]
            total_count = pagination["total_count"]
            total_pages = pagination["total_count"] // pagination["page_size"]
            total_pages = total_pages + 1 if total_count % pagination["page_size"] > 0 else 0
            page_size = pagination["page_size"]
            progress_bar.reset(total=total_pages)

            LOGGER.info("Total data size: %s, total pages to scan: %s", total_count, total_pages)

            data_list.extend(json_result["data"])

            if total_pages > 1:
                connector = aiohttp.TCPConnector(limit=PARALLEL_REQUESTS, limit_per_host=PARALLEL_REQUESTS)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    self._post_async(
                        url,
                        payload,
                        data_list,
                        progress_bar,
                        page_size,
                        total_pages,
                        connector,
                    )
                )
                connector.close()

        payload.pagination_start = 0
        LOGGER.info("Total response data: %s", len(data_list))
        df = pandas.DataFrame(data_list)
        return df
