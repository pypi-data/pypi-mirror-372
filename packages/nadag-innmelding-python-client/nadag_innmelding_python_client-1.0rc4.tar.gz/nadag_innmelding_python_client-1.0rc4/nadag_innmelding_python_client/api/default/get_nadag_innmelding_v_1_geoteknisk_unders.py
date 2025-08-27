from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.geoteknisk_unders import GeotekniskUnders
from ...types import UNSET, Response


def _get_kwargs(
    *,
    ekstern_id: str,
    ekstern_navnerom: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["eksternId"] = ekstern_id

    params["eksternNavnerom"] = ekstern_navnerom

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/nadag/innmelding/v1/GeotekniskUnders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GeotekniskUnders]:
    if response.status_code == 200:
        response_200 = GeotekniskUnders.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GeotekniskUnders]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    ekstern_id: str,
    ekstern_navnerom: str,
) -> Response[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GeotekniskUnders]
    """

    kwargs = _get_kwargs(
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    ekstern_id: str,
    ekstern_navnerom: str,
) -> Optional[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GeotekniskUnders
    """

    return sync_detailed(
        client=client,
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    ekstern_id: str,
    ekstern_navnerom: str,
) -> Response[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GeotekniskUnders]
    """

    kwargs = _get_kwargs(
        ekstern_id=ekstern_id,
        ekstern_navnerom=ekstern_navnerom,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    ekstern_id: str,
    ekstern_navnerom: str,
) -> Optional[GeotekniskUnders]:
    """Fetches a GeotekniskUnders by external id.

     Fetches a GeotekniskUnders by external id.

    Args:
        ekstern_id (str):
        ekstern_navnerom (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GeotekniskUnders
    """

    return (
        await asyncio_detailed(
            client=client,
            ekstern_id=ekstern_id,
            ekstern_navnerom=ekstern_navnerom,
        )
    ).parsed
