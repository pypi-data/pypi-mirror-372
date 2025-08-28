from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.volume import Volume
from ...types import Response


def _get_kwargs(
    volume_name: str,
    *,
    body: Volume,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/volumes/{volume_name}",
    }

    if type(body) is dict:
        _body = body
    else:
        _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[Any, Volume]]:
    if response.status_code == 200:
        response_200 = Volume.from_dict(response.json())

        return response_200
    if response.status_code == 405:
        response_405 = cast(Any, None)
        return response_405
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[Any, Volume]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    volume_name: str,
    *,
    client: Union[Client],
    body: Volume,
) -> Response[Union[Any, Volume]]:
    """Update volume (Not Implemented)

     Update a volume by name.

    Args:
        volume_name (str):
        body (Volume): Volume resource for persistent storage

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Volume]]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    volume_name: str,
    *,
    client: Union[Client],
    body: Volume,
) -> Optional[Union[Any, Volume]]:
    """Update volume (Not Implemented)

     Update a volume by name.

    Args:
        volume_name (str):
        body (Volume): Volume resource for persistent storage

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Volume]
    """

    return sync_detailed(
        volume_name=volume_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    volume_name: str,
    *,
    client: Union[Client],
    body: Volume,
) -> Response[Union[Any, Volume]]:
    """Update volume (Not Implemented)

     Update a volume by name.

    Args:
        volume_name (str):
        body (Volume): Volume resource for persistent storage

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Volume]]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume_name: str,
    *,
    client: Union[Client],
    body: Volume,
) -> Optional[Union[Any, Volume]]:
    """Update volume (Not Implemented)

     Update a volume by name.

    Args:
        volume_name (str):
        body (Volume): Volume resource for persistent storage

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Volume]
    """

    return (
        await asyncio_detailed(
            volume_name=volume_name,
            client=client,
            body=body,
        )
    ).parsed
