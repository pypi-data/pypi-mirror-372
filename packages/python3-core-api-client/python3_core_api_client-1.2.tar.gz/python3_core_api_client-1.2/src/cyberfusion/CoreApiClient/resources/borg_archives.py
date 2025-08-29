from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class BorgArchives(Resource):
    def create_borg_archive_for_database(
        self,
        request: models.BorgArchiveCreateDatabaseRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/borg-archives/database",
                data=request.dict(exclude_unset=True),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def create_borg_archive_for_unix_user(
        self,
        request: models.BorgArchiveCreateUNIXUserRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/borg-archives/unix-user",
                data=request.dict(exclude_unset=True),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def list_borg_archives(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.BorgArchiveResource]:
        return [
            models.BorgArchiveResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/borg-archives",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_borg_archive(
        self,
        *,
        id_: int,
    ) -> models.BorgArchiveResource:
        return models.BorgArchiveResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/borg-archives/{id_}", data=None, query_parameters={}
            ).json
        )

    def get_borg_archive_metadata(
        self,
        *,
        id_: int,
    ) -> models.BorgArchiveMetadata:
        return models.BorgArchiveMetadata.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/borg-archives/{id_}/metadata",
                data=None,
                query_parameters={},
            ).json
        )

    def restore_borg_archive(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        path: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/borg-archives/{id_}/restore",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                    "path": path,
                },
            ).json
        )

    def list_borg_archive_contents(
        self,
        *,
        id_: int,
        path: Optional[str] = None,
    ) -> list[models.BorgArchiveContent]:
        return [
            models.BorgArchiveContent.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/borg-archives/{id_}/contents",
                data=None,
                query_parameters={
                    "path": path,
                },
            ).json
        ]

    def download_borg_archive(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        path: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/borg-archives/{id_}/download",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                    "path": path,
                },
            ).json
        )
