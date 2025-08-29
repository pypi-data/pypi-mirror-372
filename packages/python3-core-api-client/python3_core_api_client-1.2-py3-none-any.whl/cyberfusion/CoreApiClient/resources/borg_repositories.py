from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class BorgRepositories(Resource):
    def create_borg_repository(
        self,
        request: models.BorgRepositoryCreateRequest,
    ) -> models.BorgRepositoryResource:
        return models.BorgRepositoryResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/borg-repositories",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_borg_repositories(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.BorgRepositoryResource]:
        return [
            models.BorgRepositoryResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/borg-repositories",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_borg_repository(
        self,
        *,
        id_: int,
    ) -> models.BorgRepositoryResource:
        return models.BorgRepositoryResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/borg-repositories/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def update_borg_repository(
        self,
        request: models.BorgRepositoryUpdateRequest,
        *,
        id_: int,
    ) -> models.BorgRepositoryResource:
        return models.BorgRepositoryResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/borg-repositories/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_borg_repository(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/borg-repositories/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def prune_borg_repository(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/borg-repositories/{id_}/prune",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def check_borg_repository(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/borg-repositories/{id_}/check",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def get_borg_archives_metadata(
        self,
        *,
        id_: int,
    ) -> list[models.BorgArchiveMetadata]:
        return [
            models.BorgArchiveMetadata.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/borg-repositories/{id_}/archives-metadata",
                data=None,
                query_parameters={},
            ).json
        ]
