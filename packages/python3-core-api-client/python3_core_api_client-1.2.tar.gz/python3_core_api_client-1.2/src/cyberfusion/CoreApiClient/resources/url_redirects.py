from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class URLRedirects(Resource):
    def create_url_redirect(
        self,
        request: models.URLRedirectCreateRequest,
    ) -> models.URLRedirectResource:
        return models.URLRedirectResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/url-redirects",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_url_redirects(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.URLRedirectResource]:
        return [
            models.URLRedirectResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/url-redirects",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_url_redirect(
        self,
        *,
        id_: int,
    ) -> models.URLRedirectResource:
        return models.URLRedirectResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/url-redirects/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_url_redirect(
        self,
        request: models.URLRedirectUpdateRequest,
        *,
        id_: int,
    ) -> models.URLRedirectResource:
        return models.URLRedirectResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/url-redirects/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_url_redirect(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/url-redirects/{id_}", data=None, query_parameters={}
            ).json
        )
