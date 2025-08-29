from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class SecurityTXTPolicies(Resource):
    def create_security_txt_policy(
        self,
        request: models.SecurityTXTPolicyCreateRequest,
    ) -> models.SecurityTXTPolicyResource:
        return models.SecurityTXTPolicyResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/security-txt-policies",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_security_txt_policies(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.SecurityTXTPolicyResource]:
        return [
            models.SecurityTXTPolicyResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/security-txt-policies",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_security_txt_policy(
        self,
        *,
        id_: int,
    ) -> models.SecurityTXTPolicyResource:
        return models.SecurityTXTPolicyResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/security-txt-policies/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def update_security_txt_policy(
        self,
        request: models.SecurityTXTPolicyUpdateRequest,
        *,
        id_: int,
    ) -> models.SecurityTXTPolicyResource:
        return models.SecurityTXTPolicyResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/security-txt-policies/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_security_txt_policy(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/security-txt-policies/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
