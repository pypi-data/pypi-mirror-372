from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class MariaDBEncryptionKeys(Resource):
    def create_mariadb_encryption_key(
        self,
        request: models.MariaDBEncryptionKeyCreateRequest,
    ) -> models.MariaDBEncryptionKeyResource:
        return models.MariaDBEncryptionKeyResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/mariadb-encryption-keys",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_mariadb_encryption_keys(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.MariaDBEncryptionKeyResource]:
        return [
            models.MariaDBEncryptionKeyResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/mariadb-encryption-keys",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_mariadb_encryption_key(
        self,
        *,
        id_: int,
    ) -> models.MariaDBEncryptionKeyResource:
        return models.MariaDBEncryptionKeyResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/mariadb-encryption-keys/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
