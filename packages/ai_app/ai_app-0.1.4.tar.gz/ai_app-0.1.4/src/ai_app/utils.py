import base64
import datetime
import enum
import functools
import importlib
import itertools
import logging
import os
import pathlib
import re
import site
import tempfile
import threading
import time
import urllib
import zlib
from types import ModuleType, TracebackType
from typing import Callable, Iterable, Literal, Self

import bidict
import cachetools.func
import fastapi
import gradio_client
import langchain_core.runnables
import limits.strategies
import numpy as np
import polars as pl
import pydantic
import urllib3
import uvicorn


def try_init_enum(enum_: type[enum.Enum], value) -> enum.Enum | None:
    try:
        return enum_(value)
    except ValueError:
        return


def filter_dict_by_keys(dictionary: dict, keys: Iterable) -> dict:
    dictionary = {key: dictionary[key] for key in keys if key in dictionary}
    return dictionary


def wrap_with_xml_tag(tag: str, value: str, with_new_lines: bool = False) -> str:
    value = f"\n{value}\n" if with_new_lines else value
    wrapped_value = f"<{tag}>{value}</{tag}>"
    wrapped_value += "\n" if with_new_lines else ""
    return wrapped_value


def normalize_whitespaces(string: str) -> str:
    string = re.sub(r"\s+", " ", string.strip())
    return string


def get_now() -> datetime.datetime:
    now = datetime.datetime.now().astimezone()
    return now


def get_utc_now() -> datetime.datetime:
    now = datetime.datetime.now(datetime.UTC)
    return now


class PydanticForbidExtra(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")


def display_langchain_graph(
    graph_or_agent,
    endpoint: Literal["svg", "img"] = "svg",  # The img endpoint may hang.
    width: float = 500,
    **ipython_image_kwargs,
):
    """Displays graph as Mermaid diagram inside a Jupyter notebook."""
    import IPython.display

    graph = (
        graph_or_agent
        if isinstance(graph_or_agent, langchain_core.runnables.graph.Graph)
        else graph_or_agent.get_graph()
    )
    # Makes a call to Mermaid website, which may fail due to site rate limits.
    mermaid_syntax_string = graph.draw_mermaid()
    mermaid_syntax_string = base64.b64encode(mermaid_syntax_string.encode("utf8")).decode("ascii")
    url = f"https://mermaid.ink/{endpoint}/{mermaid_syntax_string}"
    image = IPython.display.Image(url=url, width=width, **ipython_image_kwargs)
    IPython.display.display(image)


def disable_urllib_insecure_request_warning():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_number_of_batches(size: int, batch_size: int) -> int:
    n_batches = (size - 1) // batch_size + 1
    return n_batches


def unnest_with_prefix(df: pl.DataFrame, column: str) -> pl.DataFrame:
    df = df.with_columns(pl.col(column).struct.unnest().name.prefix(f"{column}_")).drop(column)
    return df


def refreshing_cache(
    maxsize: int | None = 128,
    ttl: float | datetime.timedelta = datetime.timedelta(seconds=60),
):
    """
    Calling a cached function with many different sets of arguments will lead to a memory leak.
    The cached function may return stale depending on function execution time or it the function
    throws an error after the first call.
    """
    ttl = ttl.total_seconds() if isinstance(ttl, datetime.timedelta) else ttl

    def decorator(function):
        @functools.lru_cache(maxsize=maxsize)
        class Cache:
            def __init__(self, *args, **kwargs):
                self.arguments = args, kwargs
                self.function_with_arguments = functools.partial(function, *args, **kwargs)
                self.value = self.function_with_arguments()
                self.thread = None
                self.lock = threading.Lock()

            def update(self):
                try:
                    self.value = self.function_with_arguments()
                except Exception as e:
                    logging.error(
                        f"Encountered an error when trying to refresh function cache for '{function}' with arguments {self.arguments}:\n{e}",
                        exc_info=True,
                    )

            def is_thread_running(self):
                return self.thread and self.thread.is_alive()

            def start_thread_if_not_running(self):
                with self.lock:
                    if not self.is_thread_running():
                        self.thread = threading.Thread(target=self.update, daemon=True)
                        self.thread.start()

            @cachetools.func.ttl_cache(ttl=ttl)
            def get_value(self):
                self.start_thread_if_not_running()
                return self.value

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            cache = Cache(*args, **kwargs)
            value = cache.get_value()
            return value

        return wrapped

    return decorator


class LazyImporter:
    """
    Useful for heavy packages. Example:

        os = LazyImporter("os")
        os.getcwd()
    """

    def __init__(self, module_name: str):
        # Long name not to collide with module namespace because of getattr method.
        self._module_name_for_lazy_import = module_name

    @functools.cache
    def _get_cached_lazy_import_module(self):
        with Timer("lazy importing"):
            module = importlib.import_module(self._module_name_for_lazy_import)

        return module

    def __getattr__(self, attribute: str):
        module = self._get_cached_lazy_import_module()
        attribute = getattr(module, attribute)
        return attribute


class DecoratorInterface:
    callable: Callable = None

    def on_enter(self) -> None:
        """On enter hook."""

    def on_exit(self) -> None:
        """On exit hook."""

    def on_before_callable(self, *args, **kwargs) -> None:
        """A hook, args and kwargs are the ones that were passed to the function."""

    def on_after_callable(self, result, *args, **kwargs) -> None:
        """A hook, function returned result when it was called with args and kwargs."""

    def decorate(self, callable: Callable) -> Callable:
        @functools.wraps(callable)
        def wrap(*args, **kwargs):
            self.callable = callable
            self.on_enter()
            self.on_before_callable(*args, **kwargs)
            result = callable(*args, **kwargs)
            self.on_after_callable(result, *args, **kwargs)
            self.on_exit()
            self.callable = None
            return result

        return wrap

    __call__ = decorate


class Timer(DecoratorInterface):
    """Context manager and decorator for timing."""

    def __init__(self, name: str | None = None, warning_threshold: float | None = None):
        self.name = name
        self.warning_threshold = float("inf") if warning_threshold is None else warning_threshold
        self.begin: float | None = None
        self.end: float | None = None

    def get_enriched_name(self):
        name_parts = []
        if self.name:
            name_parts.append(self.name)
        if self.callable is not None:
            name_parts.append(f"callable {self.callable.__qualname__}")

        name = ", ".join(name_parts)
        return name

    @property
    def delta(self) -> float | None:
        return None if self.end is None else self.end - self.begin

    def on_enter(self):
        self.begin = time.time()
        self.end = None
        logging.info(self.get_enriched_name())

    def on_exit(self):
        self.end = time.time()
        level = logging.WARNING if self.delta > self.warning_threshold else logging.INFO
        logging.log(level, f"Time spent on {self.get_enriched_name()}:\t{self.delta:.6f} s")

    def __enter__(self):
        self.on_enter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ):
        self.on_exit()


def setup_logging(level=logging.INFO, **kwargs):
    logging.basicConfig(
        level=level, format="{asctime} | {levelname} | {message}", style="{", **kwargs
    )


def try_match_regex(pattern: str, string: str, **kwargs):
    match = re.match(pattern, string, **kwargs)
    if not match:
        raise ValueError(f"String '{string}' does not fit expected pattern '{pattern}'")

    return match


def int_log_2(value: float) -> int:
    value = int(np.log2(value))
    return value


def get_pydantic_model_fields(model: pydantic.BaseModel) -> dict[str]:
    """Preserves field types instead of converting to base Python types, like model_dump does."""
    model_fields = {field: getattr(model, field) for field in sorted(model.model_fields_set)}
    return model_fields


def get_total_disk_size(path: str = ".") -> float:
    """Calculates the total size of a file or directory"""
    if os.path.isfile(path):
        size = os.path.getsize(path)
        return size

    if not os.path.isdir(path):
        raise ValueError(f"Path '{path}' is not a valid file or directory.")

    size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.islink(filepath):
                continue

            try:
                size += os.path.getsize(filepath)
            except OSError as e:
                print(f"Could not get size of {filepath}: {e}")

    return size


def get_installed_packages_sizes() -> pl.DataFrame:
    packages = []
    for site_package in site.getsitepackages():
        names = os.listdir(site_package)
        for name in names:
            path = os.path.join(site_package, name)
            if os.path.isdir(path) and not path.endswith(".dist-info"):
                package_size = get_total_disk_size(path)
                packages = {"package": name, "size_mb": package_size / 10**6, "package_dir": path}
                packages.append(packages)

    packages = pl.DataFrame(packages).sort("size_mb", descending=True)
    return packages


class CallableCounter:
    """Returns an increasing integer every time it is called."""

    def __init__(self):
        self.count = itertools.count()

    def __call__(self) -> int:
        return next(self.count)


class CounterBidict(bidict.bidict):
    """A bidict which maps to an autoincreasing index."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callable_counter = CallableCounter()

    def __getitem__(self, key):
        if key not in self:
            self[key] = self._callable_counter()

        value = super().__getitem__(key)
        return value


def value_to_key(items: list, key: str) -> dict:
    dictionary = {i.pop(key): i for i in items}
    return dictionary


def join_url(base_url: str, *parts: str, add_trailing_slash: bool = False) -> str:
    url = base_url.rstrip("/")
    for part in parts:
        url = urllib.parse.urljoin(url + "/", part.strip("/"))

    url = url + "/" if add_trailing_slash else url
    return url


async def serve_fastapi_app(app: fastapi.FastAPI, port: int = 7860, **kwargs):
    """Intended to be used in Jupyter notebooks."""
    config = uvicorn.Config(app, port=port, **kwargs)
    server = uvicorn.Server(config)
    await server.serve()


def build_url_with_parameters(base_url: str, **params) -> str:
    if not params:
        return base_url

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url


def file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        base64_file = base64.b64encode(f.read()).decode("utf-8")

    return base64_file


def compress(data: str) -> str:
    data_bytes = zlib.compress(data.encode("utf-8"))
    compressed_data = base64.b64encode(data_bytes).decode("utf-8")
    return compressed_data


def decompress(compressed_data: str) -> str:
    data_bytes = base64.b64decode(compressed_data)
    data = zlib.decompress(data_bytes).decode("utf-8")
    return data


def get_module_path(module: ModuleType) -> pathlib.Path:
    path = importlib.resources.files(module)
    return path


def fetch_gradio_named_endpoints_parameter_labels(
    client: gradio_client.Client,
) -> dict[str, dict[str, str]]:
    api_info = client.view_api(print_info=False, return_format="dict")
    endpoints = api_info["named_endpoints"]
    endpoints = {
        k: {p["label"]: p["parameter_name"] for p in v["parameters"]} for k, v in endpoints.items()
    }
    return endpoints


def is_redirect_response(response: fastapi.Response) -> bool:
    return 300 <= response.status_code < 400 and "Location" in response.headers


def generate_test_file(size_mb: int) -> pathlib.Path:
    """Generate a test file of the specified size in MB."""
    temp_dir = tempfile.gettempdir()
    file_path = pathlib.Path(temp_dir) / f"test_{size_mb}mb.bin"
    mega = 1024 * 1024
    chunk = b"0" * mega
    with open(file_path, "wb") as f:
        for _ in range(size_mb):
            f.write(chunk)

    actual_size_mb = os.path.getsize(file_path) / mega
    assert abs(actual_size_mb - size_mb) < 0.1
    return file_path


class HttpMethod(enum.StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


def get_remote_address(request: fastapi.Request) -> str:
    address = request.client.host if request.client and request.client.host else "127.0.0.1"
    return address


def are_rate_limits_hit(
    limiter: limits.strategies.RateLimiter,
    limits_with_keys: Iterable[tuple[limits.RateLimitItem, tuple[str, ...]]],
) -> bool:
    """Need to eagerly iterate over all rate limits and keys combinations to ensure that all are hit."""
    hit = False
    for rate_limit, key in limits_with_keys:
        allow = limiter.hit(rate_limit, *key)
        hit = hit or not allow

    return hit
