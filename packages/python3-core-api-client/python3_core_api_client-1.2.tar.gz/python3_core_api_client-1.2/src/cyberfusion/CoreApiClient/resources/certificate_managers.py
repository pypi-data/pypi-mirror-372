from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class CertificateManagers(Resource):
    def create_certificate_manager(
        self,
        request: models.CertificateManagerCreateRequest,
    ) -> models.CertificateManagerResource:
        return models.CertificateManagerResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/certificate-managers",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_certificate_managers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CertificateManagerResource]:
        return [
            models.CertificateManagerResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/certificate-managers",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_certificate_manager(
        self,
        *,
        id_: int,
    ) -> models.CertificateManagerResource:
        return models.CertificateManagerResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/certificate-managers/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def update_certificate_manager(
        self,
        request: models.CertificateManagerUpdateRequest,
        *,
        id_: int,
    ) -> models.CertificateManagerResource:
        return models.CertificateManagerResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/certificate-managers/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_certificate_manager(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/certificate-managers/{id_}",
                data=None,
                query_parameters={},
            ).json
        )

    def request_certificate(
        self,
        *,
        id_: int,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/certificate-managers/{id_}/request",
                data=None,
                query_parameters={},
            ).json
        )
