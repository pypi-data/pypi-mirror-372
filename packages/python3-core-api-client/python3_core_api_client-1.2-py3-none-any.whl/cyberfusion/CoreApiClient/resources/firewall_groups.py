from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class FirewallGroups(Resource):
    def create_firewall_group(
        self,
        request: models.FirewallGroupCreateRequest,
    ) -> models.FirewallGroupResource:
        return models.FirewallGroupResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/firewall-groups",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_firewall_groups(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.FirewallGroupResource]:
        return [
            models.FirewallGroupResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/firewall-groups",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_firewall_group(
        self,
        *,
        id_: int,
    ) -> models.FirewallGroupResource:
        return models.FirewallGroupResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/firewall-groups/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_firewall_group(
        self,
        request: models.FirewallGroupUpdateRequest,
        *,
        id_: int,
    ) -> models.FirewallGroupResource:
        return models.FirewallGroupResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/firewall-groups/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_firewall_group(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/firewall-groups/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
