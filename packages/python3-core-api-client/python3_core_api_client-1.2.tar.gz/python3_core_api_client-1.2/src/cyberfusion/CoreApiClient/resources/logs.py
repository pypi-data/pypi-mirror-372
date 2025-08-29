from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Logs(Resource):
    def list_access_logs(
        self,
        *,
        virtual_host_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[models.WebServerLogAccessResource]:
        return [
            models.WebServerLogAccessResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/logs/access/{virtual_host_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "sort": sort,
                    "limit": limit,
                },
            ).json
        ]

    def list_error_logs(
        self,
        *,
        virtual_host_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[models.WebServerLogErrorResource]:
        return [
            models.WebServerLogErrorResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/logs/error/{virtual_host_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "sort": sort,
                    "limit": limit,
                },
            ).json
        ]

    def list_object_logs(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.ObjectLogResource]:
        return [
            models.ObjectLogResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/object-logs",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def list_request_logs(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.RequestLogResource]:
        return [
            models.RequestLogResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/request-logs",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]
