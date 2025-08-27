from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.epsg_code import EpsgCode
from ...models.geoteknisk_unders import GeotekniskUnders
from ...models.validated_geoteknisk_unders import ValidatedGeotekniskUnders
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: GeotekniskUnders,
    epsg_code: EpsgCode,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_epsg_code = epsg_code.value
    params["epsgCode"] = json_epsg_code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/nadag/innmelding/v1/GeotekniskUnders",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ValidatedGeotekniskUnders]]:
    if response.status_code == 200:
        response_200 = ValidatedGeotekniskUnders.from_dict(response.json())

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
) -> Response[Union[Any, ValidatedGeotekniskUnders]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: GeotekniskUnders,
    epsg_code: EpsgCode,
) -> Response[Union[Any, ValidatedGeotekniskUnders]]:
    """Creates a new GeotekniskUnders.

     Creates a new GeotekniskUnders. Returns the id of the newly created GeotekniskUnders.

    Args:
        epsg_code (EpsgCode):
        body (GeotekniskUnders): geografisk område hvor det finnes eller er planlagt geotekniske
            borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are
            planned geotechnical boreholes for a given project</engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidatedGeotekniskUnders]]
    """

    kwargs = _get_kwargs(
        body=body,
        epsg_code=epsg_code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: GeotekniskUnders,
    epsg_code: EpsgCode,
) -> Optional[Union[Any, ValidatedGeotekniskUnders]]:
    """Creates a new GeotekniskUnders.

     Creates a new GeotekniskUnders. Returns the id of the newly created GeotekniskUnders.

    Args:
        epsg_code (EpsgCode):
        body (GeotekniskUnders): geografisk område hvor det finnes eller er planlagt geotekniske
            borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are
            planned geotechnical boreholes for a given project</engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidatedGeotekniskUnders]
    """

    return sync_detailed(
        client=client,
        body=body,
        epsg_code=epsg_code,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: GeotekniskUnders,
    epsg_code: EpsgCode,
) -> Response[Union[Any, ValidatedGeotekniskUnders]]:
    """Creates a new GeotekniskUnders.

     Creates a new GeotekniskUnders. Returns the id of the newly created GeotekniskUnders.

    Args:
        epsg_code (EpsgCode):
        body (GeotekniskUnders): geografisk område hvor det finnes eller er planlagt geotekniske
            borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are
            planned geotechnical boreholes for a given project</engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidatedGeotekniskUnders]]
    """

    kwargs = _get_kwargs(
        body=body,
        epsg_code=epsg_code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: GeotekniskUnders,
    epsg_code: EpsgCode,
) -> Optional[Union[Any, ValidatedGeotekniskUnders]]:
    """Creates a new GeotekniskUnders.

     Creates a new GeotekniskUnders. Returns the id of the newly created GeotekniskUnders.

    Args:
        epsg_code (EpsgCode):
        body (GeotekniskUnders): geografisk område hvor det finnes eller er planlagt geotekniske
            borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are
            planned geotechnical boreholes for a given project</engelsk>

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidatedGeotekniskUnders]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            epsg_code=epsg_code,
        )
    ).parsed
