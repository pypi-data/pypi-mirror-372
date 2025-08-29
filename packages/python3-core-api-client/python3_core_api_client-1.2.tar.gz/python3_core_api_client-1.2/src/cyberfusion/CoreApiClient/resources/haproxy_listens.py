from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class HAProxyListens(Resource):
    def create_haproxy_listen(
        self,
        request: models.HAProxyListenCreateRequest,
    ) -> models.HAProxyListenResource:
        return models.HAProxyListenResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/haproxy-listens",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_haproxy_listens(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.HAProxyListenResource]:
        return [
            models.HAProxyListenResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/haproxy-listens",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_haproxy_listen(
        self,
        *,
        id_: int,
    ) -> models.HAProxyListenResource:
        return models.HAProxyListenResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/haproxy-listens/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_haproxy_listen(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/haproxy-listens/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
