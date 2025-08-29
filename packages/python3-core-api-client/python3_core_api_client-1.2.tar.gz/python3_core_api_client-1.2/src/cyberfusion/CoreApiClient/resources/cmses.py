from cyberfusion.CoreApiClient import models
from typing import Optional, Union, List

from cyberfusion.CoreApiClient.interfaces import Resource


class CMSes(Resource):
    def create_cms(
        self,
        request: models.CMSCreateRequest,
    ) -> models.CMSResource:
        return models.CMSResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/cmses",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_cmses(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CMSResource]:
        return [
            models.CMSResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/cmses",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_cms(
        self,
        *,
        id_: int,
    ) -> models.CMSResource:
        return models.CMSResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/cmses/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_cms(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/cmses/{id_}", data=None, query_parameters={}
            ).json
        )

    def install_wordpress(
        self,
        request: models.CMSInstallWordPressRequest,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/install/wordpress",
                data=request.dict(exclude_unset=True),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def install_nextcloud(
        self,
        request: models.CMSInstallNextCloudRequest,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/install/nextcloud",
                data=request.dict(exclude_unset=True),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def get_cms_one_time_login(
        self,
        *,
        id_: int,
    ) -> models.CMSOneTimeLogin:
        return models.CMSOneTimeLogin.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/cmses/{id_}/one-time-login",
                data=None,
                query_parameters={},
            ).json
        )

    def get_cms_plugins(
        self,
        *,
        id_: int,
    ) -> list[models.CMSPlugin]:
        return [
            models.CMSPlugin.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET", f"/api/v1/cmses/{id_}/plugins", data=None, query_parameters={}
            ).json
        ]

    def update_cms_option(
        self,
        request: models.CMSOptionUpdateRequest,
        *,
        id_: int,
        name: models.CMSOptionNameEnum,
    ) -> models.CMSOption:
        return models.CMSOption.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/cmses/{id_}/options/{name}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def update_cms_configuration_constant(
        self,
        request: models.CMSConfigurationConstantUpdateRequest,
        *,
        id_: int,
        name: str,
    ) -> models.CMSConfigurationConstant:
        return models.CMSConfigurationConstant.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/cmses/{id_}/configuration-constants/{name}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def update_cms_user_credentials(
        self,
        request: models.CMSUserCredentialsUpdateRequest,
        *,
        id_: int,
        user_id: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/cmses/{id_}/users/{user_id}/credentials",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def update_cms_core(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/core/update",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def update_cms_plugin(
        self,
        *,
        id_: int,
        name: str,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/plugins/{name}/update",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def search_replace_in_cms_database(
        self,
        *,
        id_: int,
        search_string: str,
        replace_string: str,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/search-replace",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                    "search_string": search_string,
                    "replace_string": replace_string,
                },
            ).json
        )

    def enable_cms_plugin(
        self,
        *,
        id_: int,
        name: str,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/plugins/{name}/enable",
                data=None,
                query_parameters={},
            ).json
        )

    def disable_cms_plugin(
        self,
        *,
        id_: int,
        name: str,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/plugins/{name}/disable",
                data=None,
                query_parameters={},
            ).json
        )

    def regenerate_cms_salts(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/regenerate-salts",
                data=None,
                query_parameters={},
            ).json
        )

    def install_cms_theme(
        self,
        request: Union[
            models.CMSThemeInstallFromRepositoryRequest,
            models.CMSThemeInstallFromURLRequest,
        ],
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/cmses/{id_}/themes",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )
