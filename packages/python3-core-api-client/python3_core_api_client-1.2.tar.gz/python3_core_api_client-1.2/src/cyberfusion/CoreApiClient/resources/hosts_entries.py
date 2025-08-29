from cyberfusion.CoreApiClient import models
from typing import Optional, List
from cyberfusion.CoreApiClient.interfaces import Resource


class HostsEntries(Resource):
    def create_hosts_entry(
        self,
        request: models.HostsEntryCreateRequest,
    ) -> models.HostsEntryResource:
        return models.HostsEntryResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/hosts-entries",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_hosts_entries(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.HostsEntryResource]:
        return [
            models.HostsEntryResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/hosts-entries",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_hosts_entry(
        self,
        *,
        id_: int,
    ) -> models.HostsEntryResource:
        return models.HostsEntryResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/hosts-entries/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_hosts_entry(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/hosts-entries/{id_}", data=None, query_parameters={}
            ).json
        )
