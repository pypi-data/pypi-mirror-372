import json
import httpx
import logging
from pydantic import BaseModel
from typing import Any, Dict, Optional, Type, Iterator
from prance import ResolvingParser
import time
import importlib

from itertools import islice
import pandas as pd

from synmax.openapi.utils import change_signature, get_annotation, get_body_model, get_param_model

class OpenAPIClient:
    def __init__(self,
                 base_uri: str = "",
                 headers: Optional[Dict[str, str]] = None,
                 logger: Optional[logging.Logger] = None,
                 timeout = 15.0,
                 retries = 3,
                 retry_sleep = 20,
                 ):
        self._base_uri = base_uri.rstrip('/')
        self._retries = retries
        self._retry_sleep = retry_sleep
        self._timeout = timeout
        accept_header = {"Accept": "application/x-ndjson"}
        base_headers = headers or {}
        self._client = httpx.Client(
            headers=dict(base_headers, **accept_header),
            timeout=timeout,
        )
        self._logger = logger or logging.getLogger(__name__)
        parser = ResolvingParser(self._spec, backend = 'openapi-spec-validator')
        self._openapi = parser.specification
        self._paths = self._openapi.get("paths", {})
        self._generate_methods()
        self._logger.info(f"Initialized client for {self._base_uri}")


    def _generate_methods(self):
        for path, methods in self._paths.items():
            for method, details in methods.items():
                method_name = details.get("x-method-name", None)
                if method_name is None:
                    continue
                param_model = get_param_model(details.get("parameters", []), method_name)
                body_model = get_body_model(details.get("requestBody", {}), method_name)
                full_url = f"{self._base_uri}{path}"
                request_func = self._create_request_function(method, full_url, param_model, body_model)
                request_func.__name__ = method_name
                setattr(self, method_name, request_func.__get__(self))


    @classmethod
    def _dump_stub(cls) -> str:
        if not hasattr(cls, '_spec'):
            message = f"Class '{cls.__name__}' is missing required attribute: '_spec'"
            raise AttributeError(message)
        t = type(cls.__name__, (OpenAPIClient,), {"_spec": cls._spec})
        return t()._get_annotations()


    @classmethod
    def _write_stub(cls):
        module = cls.__module__
        origin = importlib.util.find_spec(module).origin
        outfile = f"{origin}i"
        with open(outfile, "w") as file:
            file.write(cls._dump_stub())
        print(f"wrote class stub to {outfile}")


    def _get_annotations(self) -> str:
        lines = []
        lines.append("from typing import Literal, Union")
        lines.append("from synmax.openapi.client import Result")
        lines.append("from datetime import date")
        lines.append(f"class {self.__class__.__name__}:")

        tab = "    "

        for path, methods in self._paths.items():
            for method, details in methods.items():
                method_name = details.get("x-method-name", details.get("operationId", None))
                if method_name is None:
                    continue
                param_model = get_param_model(details.get("parameters", []), method_name)
                body_model = get_body_model(details.get("requestBody", {}), method_name)
                annotation = get_annotation([param_model, body_model])
                description = details.get("summary", None)
                if description is None:
                    description = " "
                else:
                    description = f"\n{tab}{tab}\"\"\"{description}\"\"\"\n{tab}{tab}"

                lines.append(f"{tab}def {method_name}({annotation}) -> Result:{description}...")
        return "\n".join(lines)


    def _create_request_function(self, method: str, full_url: str, param_model: Optional[Type[BaseModel]], body_model: Optional[Type[BaseModel]]):
        def request_func(self, **kwargs) -> Result:
            def generator() -> Iterator[Dict[str, Any]]:
                param_dict = None
                if param_model:
                    data = param_model(**kwargs).model_dump(mode='json')
                    param_dict = {k: v for k, v in data.dict().items() if v is not None}
                body_dict = None
                if body_model:
                    data = body_model(**kwargs).model_dump(mode='json')
                    body_dict = {k: v for k, v in data.items() if v is not None}
                self._logger.info(f"Making request to {full_url}")
                retry_count = 0
                can_retry = True
                while can_retry:
                    try:
                        with self._client.stream(
                                method.upper(),
                                full_url,
                                params=param_dict if param_model else None,
                                json=body_dict if body_model else None,
                                ) as response:
                            if response.is_error:
                                for chunk in response.iter_text():
                                    self._logger.error(f"Error response fom api server. Status code: {response.status_code}")
                                    self._logger.error(chunk)
                            response.raise_for_status()
                            total_bytes = 0
                            total_records = 0
                            last_message = time.time()
                            buffer = ""
                            for chunk in response.iter_bytes():
                                total_bytes += len(chunk)
                                buffer += chunk.decode("utf-8")
                                while "\n" in buffer:
                                    line, buffer = buffer.split("\n", 1)
                                    if line.strip():
                                        can_retry = False # if we get any response, interrupt retry logic
                                        yield json.loads(line)
                                        total_records += 1
                                now = time.time()
                                if now - last_message >= 1:
                                    last_message = now
                                    self._logger.debug(f"Got {total_records} total records, {total_bytes} total bytes")
                            if buffer.strip():  # last record has no newline
                                yield json.loads(buffer)
                                total_records += 1
                            self._logger.debug(f"Got {total_records} total records, {total_bytes} total bytes")
                        break
                    except httpx.ReadTimeout:
                        retry_count += 1
                        retry_text = ""
                        can_retry = can_retry and retry_count <= self._retries
                        if can_retry:
                            retry_text = f"Retry {retry_count}/{self._retries}. Sleep {self._retry_sleep}s."
                        self._logger.error(f"Request timed out ({self._timeout}s). {retry_text}")
                        time.sleep(self._retry_sleep)

            return Result(generator())

        signature = {}
        for model in (param_model, body_model):
            if model:
                for field_name, field in model.__annotations__.items():
                    is_optional = model.__fields__[field_name].default is None
                    signature[field_name] = Optional[field] if is_optional else field
        return change_signature(request_func, signature)

    def close(self):
        self._client.close()



class Result(Iterator[Dict[str, Any]]):
    def __init__(self, generator):
        self._generator = generator

    def __iter__(self):
        return self._generator

    def __next__(self):
        return next(self._generator)

    def df(self, chunk_size = 100000) -> pd.DataFrame:
        def batched():
            it = iter(self)
            while True:
                batch = list(islice(it, chunk_size))
                if not batch:
                    break
                yield batch
        chunks = []
        for batch in batched():
            chunks.append(pd.DataFrame(batch))
        if len(chunks) > 0:
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.DataFrame()
        return df

    # TODO: save_csv(self, path)
