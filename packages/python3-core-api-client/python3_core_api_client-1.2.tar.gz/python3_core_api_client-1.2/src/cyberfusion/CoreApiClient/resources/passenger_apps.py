from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class PassengerApps(Resource):
    def create_nodejs_passenger_app(
        self,
        request: models.PassengerAppCreateNodeJSRequest,
    ) -> models.PassengerAppResource:
        return models.PassengerAppResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/passenger-apps/nodejs",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_passenger_apps(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.PassengerAppResource]:
        return [
            models.PassengerAppResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/passenger-apps",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_passenger_app(
        self,
        *,
        id_: int,
    ) -> models.PassengerAppResource:
        return models.PassengerAppResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/passenger-apps/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_passenger_app(
        self,
        request: models.PassengerAppUpdateRequest,
        *,
        id_: int,
    ) -> models.PassengerAppResource:
        return models.PassengerAppResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/passenger-apps/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_passenger_app(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/passenger-apps/{id_}",
                data=None,
                query_parameters={"delete_on_cluster": delete_on_cluster},
            ).json
        )

    def restart_passenger_app(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/passenger-apps/{id_}/restart",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )
