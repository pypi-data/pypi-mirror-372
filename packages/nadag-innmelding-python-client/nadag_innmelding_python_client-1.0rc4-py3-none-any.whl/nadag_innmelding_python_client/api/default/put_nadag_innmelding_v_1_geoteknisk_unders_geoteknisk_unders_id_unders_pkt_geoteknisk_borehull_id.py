from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.epsg_code import EpsgCode
from ...models.geoteknisk_borehull import GeotekniskBorehull
from ...models.validated_geoteknisk_unders import ValidatedGeotekniskUnders
from ...types import UNSET, Response


def _get_kwargs(
    geoteknisk_unders_id: str,
    geoteknisk_borehull_id: str,
    *,
    body: GeotekniskBorehull,
    epsg_code: EpsgCode,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_epsg_code = epsg_code.value
    params["epsgCode"] = json_epsg_code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/nadag/innmelding/v1/GeotekniskUnders/{geoteknisk_unders_id}/undersPkt/{geoteknisk_borehull_id}",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ValidatedGeotekniskUnders]:
    if response.status_code == 200:
        response_200 = ValidatedGeotekniskUnders.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ValidatedGeotekniskUnders]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    geoteknisk_unders_id: str,
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient,
    body: GeotekniskBorehull,
    epsg_code: EpsgCode,
) -> Response[ValidatedGeotekniskUnders]:
    """Updates a GeotekniskBorehull.

     Updates a GeotekniskBorehull.

    Args:
        geoteknisk_unders_id (str):
        geoteknisk_borehull_id (str):
        epsg_code (EpsgCode):
        body (GeotekniskBorehull): geografisk område representert ved et punkt som er den logiske
            enhet for tolking av laginndeling og egenskaper til de forskjellige jordlag
            <engelsk>geographical area represented by a location which is the logical unit for
            interpretation of stratification and properties for the different strata </engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ValidatedGeotekniskUnders]
    """

    kwargs = _get_kwargs(
        geoteknisk_unders_id=geoteknisk_unders_id,
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        body=body,
        epsg_code=epsg_code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    geoteknisk_unders_id: str,
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient,
    body: GeotekniskBorehull,
    epsg_code: EpsgCode,
) -> Optional[ValidatedGeotekniskUnders]:
    """Updates a GeotekniskBorehull.

     Updates a GeotekniskBorehull.

    Args:
        geoteknisk_unders_id (str):
        geoteknisk_borehull_id (str):
        epsg_code (EpsgCode):
        body (GeotekniskBorehull): geografisk område representert ved et punkt som er den logiske
            enhet for tolking av laginndeling og egenskaper til de forskjellige jordlag
            <engelsk>geographical area represented by a location which is the logical unit for
            interpretation of stratification and properties for the different strata </engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ValidatedGeotekniskUnders
    """

    return sync_detailed(
        geoteknisk_unders_id=geoteknisk_unders_id,
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        client=client,
        body=body,
        epsg_code=epsg_code,
    ).parsed


async def asyncio_detailed(
    geoteknisk_unders_id: str,
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient,
    body: GeotekniskBorehull,
    epsg_code: EpsgCode,
) -> Response[ValidatedGeotekniskUnders]:
    """Updates a GeotekniskBorehull.

     Updates a GeotekniskBorehull.

    Args:
        geoteknisk_unders_id (str):
        geoteknisk_borehull_id (str):
        epsg_code (EpsgCode):
        body (GeotekniskBorehull): geografisk område representert ved et punkt som er den logiske
            enhet for tolking av laginndeling og egenskaper til de forskjellige jordlag
            <engelsk>geographical area represented by a location which is the logical unit for
            interpretation of stratification and properties for the different strata </engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ValidatedGeotekniskUnders]
    """

    kwargs = _get_kwargs(
        geoteknisk_unders_id=geoteknisk_unders_id,
        geoteknisk_borehull_id=geoteknisk_borehull_id,
        body=body,
        epsg_code=epsg_code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    geoteknisk_unders_id: str,
    geoteknisk_borehull_id: str,
    *,
    client: AuthenticatedClient,
    body: GeotekniskBorehull,
    epsg_code: EpsgCode,
) -> Optional[ValidatedGeotekniskUnders]:
    """Updates a GeotekniskBorehull.

     Updates a GeotekniskBorehull.

    Args:
        geoteknisk_unders_id (str):
        geoteknisk_borehull_id (str):
        epsg_code (EpsgCode):
        body (GeotekniskBorehull): geografisk område representert ved et punkt som er den logiske
            enhet for tolking av laginndeling og egenskaper til de forskjellige jordlag
            <engelsk>geographical area represented by a location which is the logical unit for
            interpretation of stratification and properties for the different strata </engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ValidatedGeotekniskUnders
    """

    return (
        await asyncio_detailed(
            geoteknisk_unders_id=geoteknisk_unders_id,
            geoteknisk_borehull_id=geoteknisk_borehull_id,
            client=client,
            body=body,
            epsg_code=epsg_code,
        )
    ).parsed
