from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Daemons(Resource):
    def create_daemon(
        self,
        request: models.DaemonCreateRequest,
    ) -> models.DaemonResource:
        return models.DaemonResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/daemons",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_daemons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.DaemonResource]:
        return [
            models.DaemonResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/daemons",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_daemon(
        self,
        *,
        id_: int,
    ) -> models.DaemonResource:
        return models.DaemonResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/daemons/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_daemon(
        self,
        request: models.DaemonUpdateRequest,
        *,
        id_: int,
    ) -> models.DaemonResource:
        return models.DaemonResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/daemons/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_daemon(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/daemons/{id_}", data=None, query_parameters={}
            ).json
        )

    def list_logs(
        self,
        *,
        daemon_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[models.DaemonLogResource]:
        return [
            models.DaemonLogResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/daemons/{daemon_id}/logs",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "sort": sort,
                    "limit": limit,
                },
            ).json
        ]
