from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class BasicAuthenticationRealms(Resource):
    def create_basic_authentication_realm(
        self,
        request: models.BasicAuthenticationRealmCreateRequest,
    ) -> models.BasicAuthenticationRealmResource:
        return models.BasicAuthenticationRealmResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/basic-authentication-realms",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_basic_authentication_realms(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.BasicAuthenticationRealmResource]:
        return [
            models.BasicAuthenticationRealmResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/basic-authentication-realms",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_basic_authentication_realm(
        self,
        *,
        id_: int,
    ) -> models.BasicAuthenticationRealmResource:
        return models.BasicAuthenticationRealmResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/basic-authentication-realms/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def update_basic_authentication_realm(
        self,
        request: models.BasicAuthenticationRealmUpdateRequest,
        *,
        id_: int,
    ) -> models.BasicAuthenticationRealmResource:
        return models.BasicAuthenticationRealmResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/basic-authentication-realms/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_basic_authentication_realm(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/basic-authentication-realms/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
