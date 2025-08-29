from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Crons(Resource):
    def create_cron(
        self,
        request: models.CronCreateRequest,
    ) -> models.CronResource:
        return models.CronResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/crons",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_crons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CronResource]:
        return [
            models.CronResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/crons",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_cron(
        self,
        *,
        id_: int,
    ) -> models.CronResource:
        return models.CronResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/crons/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_cron(
        self,
        request: models.CronUpdateRequest,
        *,
        id_: int,
    ) -> models.CronResource:
        return models.CronResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/crons/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_cron(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/crons/{id_}", data=None, query_parameters={}
            ).json
        )
