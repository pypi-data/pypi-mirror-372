from cyberfusion.CoreApiClient import models
from typing import Optional, List
from cyberfusion.CoreApiClient.interfaces import Resource


class Certificates(Resource):
    def create_certificate(
        self,
        request: models.CertificateCreateRequest,
    ) -> models.CertificateResource:
        return models.CertificateResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/certificates",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_certificates(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CertificateResource]:
        return [
            models.CertificateResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/certificates",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_certificate(
        self,
        *,
        id_: int,
    ) -> models.CertificateResource:
        return models.CertificateResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/certificates/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_certificate(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/certificates/{id_}", data=None, query_parameters={}
            ).json
        )
