from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.datasets_paginated_list import DatasetsPaginatedList
from ...models.list_datasets_sort import ListDatasetsSort
from ...models.listing_error import ListingError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListDatasetsSort] = ListDatasetsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    origin_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/datasets".format(client.base_url)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason
    if not isinstance(created_at, Unset) and created_at is not None:
        params["createdAt"] = created_at
    if not isinstance(creator_ids, Unset) and creator_ids is not None:
        params["creatorIds"] = creator_ids
    if not isinstance(folder_id, Unset) and folder_id is not None:
        params["folderId"] = folder_id
    if not isinstance(mentioned_in, Unset) and mentioned_in is not None:
        params["mentionedIn"] = mentioned_in
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(name_includes, Unset) and name_includes is not None:
        params["nameIncludes"] = name_includes
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(origin_ids, Unset) and origin_ids is not None:
        params["originIds"] = origin_ids
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(display_ids, Unset) and display_ids is not None:
        params["displayIds"] = display_ids
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    if response.status_code == 200:
        response_200 = DatasetsPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = ListingError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListDatasetsSort] = ListDatasetsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    origin_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListDatasetsSort] = ListDatasetsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    origin_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    """ List datasets """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListDatasetsSort] = ListDatasetsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    origin_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListDatasetsSort] = ListDatasetsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    created_at: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    origin_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    """ List datasets """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            archive_reason=archive_reason,
            created_at=created_at,
            creator_ids=creator_ids,
            folder_id=folder_id,
            mentioned_in=mentioned_in,
            modified_at=modified_at,
            name=name,
            name_includes=name_includes,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            namesany_of=namesany_of,
            origin_ids=origin_ids,
            ids=ids,
            display_ids=display_ids,
            returning=returning,
        )
    ).parsed
