from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class FirewallRules(Resource):
    def create_firewall_rule(
        self,
        request: models.FirewallRuleCreateRequest,
    ) -> models.FirewallRuleResource:
        return models.FirewallRuleResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/firewall-rules",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_firewall_rules(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.FirewallRuleResource]:
        return [
            models.FirewallRuleResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/firewall-rules",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_firewall_rule(
        self,
        *,
        id_: int,
    ) -> models.FirewallRuleResource:
        return models.FirewallRuleResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/firewall-rules/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_firewall_rule(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/firewall-rules/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
