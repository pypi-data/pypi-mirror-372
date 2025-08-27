from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.geoteknisk_unders import GeotekniskUnders
from ...types import Response


def _get_kwargs(
    geoteknisk_unders_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/nadag/innmelding/v1/GeotekniskUnders/{geoteknisk_unders_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, GeotekniskUnders]]:
    if response.status_code == 200:
        response_200 = GeotekniskUnders.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, GeotekniskUnders]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    geoteknisk_unders_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, GeotekniskUnders]]:
    """Fetches a GeotekniskUnders by id.

     Fetches a GeotekniskUnders by id.

    Args:
        geoteknisk_unders_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GeotekniskUnders]]
    """

    kwargs = _get_kwargs(
        geoteknisk_unders_id=geoteknisk_unders_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    geoteknisk_unders_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, GeotekniskUnders]]:
    """Fetches a GeotekniskUnders by id.

     Fetches a GeotekniskUnders by id.

    Args:
        geoteknisk_unders_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GeotekniskUnders]
    """

    return sync_detailed(
        geoteknisk_unders_id=geoteknisk_unders_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    geoteknisk_unders_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, GeotekniskUnders]]:
    """Fetches a GeotekniskUnders by id.

     Fetches a GeotekniskUnders by id.

    Args:
        geoteknisk_unders_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GeotekniskUnders]]
    """

    kwargs = _get_kwargs(
        geoteknisk_unders_id=geoteknisk_unders_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    geoteknisk_unders_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, GeotekniskUnders]]:
    """Fetches a GeotekniskUnders by id.

     Fetches a GeotekniskUnders by id.

    Args:
        geoteknisk_unders_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GeotekniskUnders]
    """

    return (
        await asyncio_detailed(
            geoteknisk_unders_id=geoteknisk_unders_id,
            client=client,
        )
    ).parsed
