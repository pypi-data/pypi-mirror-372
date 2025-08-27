from typing import Type, TypeVar, Any, Dict, Optional, Generator, Callable

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def req(
    client: httpx.Client,
    method: str,
    url: str,
    response_model: Type[T],
    *,
    expected_status: int = 200,
    handle_404_none: bool = False,
    **kwargs,
) -> Optional[T]:
    """
    Send an HTTP request synchronously, parse the response.
    Return None if 404 and handle_404_none=True, else raise.
    """
    try:
        resp = client.request(method, url, **kwargs)
        if handle_404_none and resp.status_code == 404:
            return None

        if 400 <= resp.status_code < 500:
            resp.read()
            if resp.text == "Please specify a group":
                raise httpx.HTTPStatusError(
                    "Bad Request: Please specify a group. Use `AisbergClient.me.groups()` to know which groups you are in.",
                    request=resp.request,
                    response=resp,
                )
            raise httpx.HTTPStatusError(
                f"Bad Request: {resp.text}", request=resp.request, response=resp
            )

        resp.raise_for_status()
        return response_model.model_validate(resp.json())
    except httpx.HTTPStatusError as e:
        if handle_404_none and e.response.status_code == 404:
            return None
        raise
    except ValidationError as ve:
        raise RuntimeError(f"Invalid response: {ve}") from ve


def req_stream(
    client: httpx.Client,
    method: str,
    url: str,
    parse_line: Callable[[str], Any],
    *,
    handle_status: Optional[Dict[int, Any]] = None,
    **kwargs,
) -> Generator[Any, None, None]:
    """
    Wrapper to handle HTTP streams.
    - parse_line: Function to parse each line of the stream.
    """
    with client.stream(method, url, **kwargs) as resp:
        if handle_status and resp.status_code in handle_status:
            yield handle_status[resp.status_code]
            return

        if 400 <= resp.status_code < 500:
            resp.read()
            if resp.text == "Please specify a group":
                raise httpx.HTTPStatusError(
                    "Bad Request: Please specify a group. Use `await AisbergAsyncClient.me.groups()` to know which groups you are in.",
                    request=resp.request,
                    response=resp,
                )
            raise httpx.HTTPStatusError(
                f"Bad Request: {resp.text}", request=resp.request, response=resp
            )

        resp.raise_for_status()
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode() if isinstance(raw_line, bytes) else raw_line
            for parsed in parse_line(line):
                yield parsed
