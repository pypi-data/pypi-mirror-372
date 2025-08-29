from cyberfusion.CoreApiClient import models

from cyberfusion.CoreApiClient.interfaces import Resource


class Login(Resource):
    def request_access_token(
        self,
        request: models.BodyLoginAccessToken,
    ) -> models.TokenResource:
        return models.TokenResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/login/access-token",
                data=request.dict(exclude_unset=True),
                query_parameters={},
                content_type="application/x-www-form-urlencoded",
            ).json
        )

    def test_access_token(
        self,
    ) -> models.APIUserInfo:
        return models.APIUserInfo.parse_obj(
            self.api_connector.send_or_fail(
                "POST", "/api/v1/login/test-token", data=None, query_parameters={}
            ).json
        )
