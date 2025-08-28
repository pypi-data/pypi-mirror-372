from typing import Callable
import tenacity
from panoramax_cli import USER_AGENT
from panoramax_cli.utils import REQUESTS_TIMEOUT
import httpx
from contextlib import contextmanager


@contextmanager
def createClientWithRetry(disable_cert_check: bool = False):
    """Creates a httpx client with automatic retry on failure"""
    transport = httpx.HTTPTransport(
        retries=3
    )  # Note: this retry is only used by httpx to handle connection retries, not when the client fails to read/write
    headers = httpx.Headers(headers={"User-Agent": USER_AGENT})
    with Client(
        transport=transport,
        verify=(not disable_cert_check),
        headers=headers,
        timeout=REQUESTS_TIMEOUT,
    ) as c:
        yield c


RETRY_STATUS_FORCELIST = [502, 503, 504]
MAX_RETRY = 3


def is_retryable_status_code(response):
    """Define the conditions for retrying based on HTTP status codes"""
    return response.status_code in RETRY_STATUS_FORCELIST


def raise_retry_error(retry_state: tenacity.RetryCallState):
    """On failure, raise the exception if there is one, or return the httpx response"""
    outcome = retry_state.outcome
    if not outcome:
        return None
    if outcome.failed:
        e = outcome.exception()
        assert e
        raise e
    return outcome.result()


class retry_if_code_in_retry_status_forcelist(tenacity.retry_base):
    """Handle retries for exception raised by raise_for_status and for invalid status_code"""

    def __call__(self, retry_state: tenacity.RetryCallState) -> bool:
        if not retry_state.outcome:
            return True
        if retry_state.outcome.failed:
            e = retry_state.outcome.exception()
            assert e
            return isinstance(e, httpx.HTTPStatusError) and is_retryable_status_code(e.response)
        page = retry_state.outcome.result()
        return is_retryable_status_code(page)


class Client:
    """
    Simple Wrapper around an httpx Client, retrying GET and POST method

    Note that only the used functions of the httpx Client are implemented, if more method are needed, they'll need to be wraped too

    Note: The streaming part is not handled, as it is tricky to retry a generator.

    This client also cache the instance configuration, so it does not need to be fetched several times
    """

    _httpx_client: httpx.Client

    def __init__(self, **kwargs):
        self._httpx_client = httpx.Client(**kwargs)
        self._instance_configuration = None

    def get_instance_configuration(self, panoramax):
        if self._instance_configuration is None:
            c = self.get(f"{panoramax.url}/api/configuration")
            c.raise_for_status()
            self._instance_configuration = c.json()
        return self._instance_configuration

    def close(self):
        self._httpx_client.close()

    def __enter__(self):
        self._httpx_client.__enter__()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self._httpx_client.__exit__(exc_type=exc_type, exc_value=exc_value, traceback=traceback)

    @property
    def headers(self) -> httpx.Headers:
        return self._httpx_client.headers

    @headers.setter
    def headers(self, headers) -> None:
        self._httpx_client.headers = headers

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self._retry(self._httpx_client.get)(url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self._retry(self._httpx_client.post)(url, **kwargs)

    def _retry(self, func: Callable) -> Callable:
        """Retry given function if the http call fails"""
        retry_strategy = retry_if_code_in_retry_status_forcelist() | tenacity.retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError)
        )
        return tenacity.retry(
            retry=retry_strategy,
            stop=tenacity.stop_after_attempt(MAX_RETRY),
            retry_error_callback=raise_retry_error,
            wait=tenacity.wait_exponential(
                multiplier=0.5,
                max=100,
            ),
            reraise=True,
        )(func)
