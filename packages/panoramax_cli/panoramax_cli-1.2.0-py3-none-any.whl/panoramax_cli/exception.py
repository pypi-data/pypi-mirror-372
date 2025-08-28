from httpx import HTTPStatusError, Response
from typing import Optional


class CliException(Exception):
    def __init__(self, msg, details: Optional[str] = None, response: Optional[Response] = None):
        if details is not None:
            msg += f"\n[bold]Error:[/bold]\n{details}"
        if response is not None:
            msg += format_response(response)
        super().__init__(msg)


def raise_for_status(r: Response, msg: str):
    try:
        r.raise_for_status()
    except HTTPStatusError as e:
        raise CliException(msg, details=str(e), response=e.response) from e


def format_response(r: Response):
    """Format response to display in error message
    Panoramax errors can define a `message` and `details` in the json, if it's the case, display them properly.
    """
    try:
        error = "\n[bold]Details:[/bold]"
        data = r.json()
        msg = data.pop("message", None)
        if msg:
            error += f"\n{msg}"
        details = data.pop("details", None)
        if details:
            error += f"\n{details}"
        data.pop("status_code", None)
        return error

    except Exception:
        return f"\n[bold]Response:[/bold]\n{r.text}"
