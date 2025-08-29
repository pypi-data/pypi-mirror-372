import json
from typing import Optional, Tuple

from cyberfusion.CoreApiClient._encoders import CustomEncoder
from cyberfusion.CoreApiClient.exceptions import CallException, AuthenticationException

from requests.sessions import Session
from typing import Dict, Any, Union
from requests.adapters import HTTPAdapter, Retry
import requests
import certifi
from functools import cached_property
from cyberfusion.CoreApiClient import resources
import datetime
import importlib.metadata
from cyberfusion.CoreApiClient.http import Response


class CoreApiClient:
    def __init__(
        self,
        base_url: str = "https://core-api.cyberfusion.io",
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        requests_session: Optional[Session] = None,
    ) -> None:
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_key = api_key

        self._jwt_metadata: Optional[Tuple[str, Any]] = None

        if (self.username and self.password) and self.api_key:
            raise ValueError(
                "Specify either username and password, or API key, not both"
            )

        if self.username and not self.password:
            raise ValueError("If username is specified, password must be specified")

        if self.password and not self.username:
            raise ValueError("If password is specified, username must be specified")

        if not self.api_key and not (self.username and self.password):
            raise ValueError("Specify either username and password, or API key")

        self.requests_session = requests_session or self.get_default_requests_session()

    @property
    def authentication_headers(self) -> Dict[str, str]:
        headers = {}

        if self.api_key:
            headers["X-API-Key"] = self.api_key
        else:
            login = False

            if not self._jwt_metadata:
                login = True
            else:
                access_token, expires_at = self._jwt_metadata

                if datetime.datetime.utcnow() >= expires_at:
                    login = True

            if login:
                response = self.requests_session.post(
                    "".join([self.base_url, "/api/v1/login/access-token"]),
                    data={"username": self.username, "password": self.password},
                    verify=certifi.where(),
                    timeout=60,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    raise AuthenticationException(
                        response.text, response.status_code
                    ) from e

                json = response.json()

                access_token = json["access_token"]
                expires_in = json["expires_in"]
                expires_at = datetime.datetime.utcnow() + datetime.timedelta(
                    seconds=expires_in
                )

                self._jwt_metadata = (access_token, expires_at)

            headers["Authorization"] = "Bearer " + access_token

        return headers

    def send(
        self,
        method: str,
        path: str,
        data: Optional[Union[str, dict]] = None,
        query_parameters: Optional[dict] = None,
        *,
        content_type: str = "application/json",
    ) -> Response:
        url = "".join([self.base_url, path])

        if data and content_type == "application/json":
            data = json.dumps(data, cls=CustomEncoder)

        if query_parameters:
            for key, value in query_parameters.items():
                if isinstance(value, datetime.datetime):
                    query_parameters[key] = json.loads(
                        json.dumps(value, cls=CustomEncoder)
                    )

        requests_response = self.requests_session.request(
            method,
            url,
            headers=self.authentication_headers | {"Content-Type": content_type},
            data=data,
            params=query_parameters,
            verify=certifi.where(),
            timeout=60,
        )

        local_response = Response(
            status_code=requests_response.status_code,
            body=requests_response.text,
            headers=requests_response.headers,
        )

        return local_response

    def send_or_fail(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        query_parameters: Optional[dict] = None,
        *,
        content_type: str = "application/json",
    ) -> Response:
        local_response = self.send(
            method, path, data, query_parameters, content_type=content_type
        )

        if local_response.failed:
            raise CallException(local_response.body, local_response.status_code)

        return local_response

    def get_default_requests_session(self) -> requests.sessions.Session:
        session = requests.Session()

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=10,
                backoff_factor=2.5,
                allowed_methods=None,
                status_forcelist=[502, 503],
            )
        )

        session.mount(self.base_url + "/", adapter)

        session.headers.update(
            {
                "User-Agent": "python3-core-api-client/"
                + importlib.metadata.version("python3-core-api-client")
            }
        )

        return session


class CoreApiConnector(CoreApiClient):
    @cached_property
    def login(self) -> resources.login.Login:
        return resources.login.Login(self)

    @cached_property
    def sites(self) -> resources.sites.Sites:
        return resources.sites.Sites(self)

    @cached_property
    def customers(self) -> resources.customers.Customers:
        return resources.customers.Customers(self)

    @cached_property
    def haproxy_listens(self) -> resources.haproxy_listens.HAProxyListens:
        return resources.haproxy_listens.HAProxyListens(self)

    @cached_property
    def haproxy_listens_to_nodes(
        self,
    ) -> resources.haproxy_listens_to_nodes.HAProxyListensToNodes:
        return resources.haproxy_listens_to_nodes.HAProxyListensToNodes(self)

    @cached_property
    def borg_repositories(self) -> resources.borg_repositories.BorgRepositories:
        return resources.borg_repositories.BorgRepositories(self)

    @cached_property
    def borg_archives(self) -> resources.borg_archives.BorgArchives:
        return resources.borg_archives.BorgArchives(self)

    @cached_property
    def certificates(self) -> resources.certificates.Certificates:
        return resources.certificates.Certificates(self)

    @cached_property
    def certificate_managers(
        self,
    ) -> resources.certificate_managers.CertificateManagers:
        return resources.certificate_managers.CertificateManagers(self)

    @cached_property
    def tombstones(self) -> resources.tombstones.Tombstones:
        return resources.tombstones.Tombstones(self)

    @cached_property
    def clusters(self) -> resources.clusters.Clusters:
        return resources.clusters.Clusters(self)

    @cached_property
    def virtual_hosts(self) -> resources.virtual_hosts.VirtualHosts:
        return resources.virtual_hosts.VirtualHosts(self)

    @cached_property
    def mail_hostnames(self) -> resources.mail_hostnames.MailHostnames:
        return resources.mail_hostnames.MailHostnames(self)

    @cached_property
    def domain_routers(self) -> resources.domain_routers.DomainRouters:
        return resources.domain_routers.DomainRouters(self)

    @cached_property
    def url_redirects(self) -> resources.url_redirects.URLRedirects:
        return resources.url_redirects.URLRedirects(self)

    @cached_property
    def htpasswd_files(self) -> resources.htpasswd_files.HtpasswdFiles:
        return resources.htpasswd_files.HtpasswdFiles(self)

    @cached_property
    def htpasswd_users(self) -> resources.htpasswd_users.HtpasswdUsers:
        return resources.htpasswd_users.HtpasswdUsers(self)

    @cached_property
    def basic_authentication_realms(
        self,
    ) -> resources.basic_authentication_realms.BasicAuthenticationRealms:
        return resources.basic_authentication_realms.BasicAuthenticationRealms(self)

    @cached_property
    def node_add_ons(self) -> resources.node_add_ons.NodeAddOns:
        return resources.node_add_ons.NodeAddOns(self)

    @cached_property
    def crons(self) -> resources.crons.Crons:
        return resources.crons.Crons(self)

    @cached_property
    def daemons(self) -> resources.daemons.Daemons:
        return resources.daemons.Daemons(self)

    @cached_property
    def mariadb_encryption_keys(
        self,
    ) -> resources.mariadb_encryption_keys.MariaDBEncryptionKeys:
        return resources.mariadb_encryption_keys.MariaDBEncryptionKeys(self)

    @cached_property
    def firewall_rules(self) -> resources.firewall_rules.FirewallRules:
        return resources.firewall_rules.FirewallRules(self)

    @cached_property
    def hosts_entries(self) -> resources.hosts_entries.HostsEntries:
        return resources.hosts_entries.HostsEntries(self)

    @cached_property
    def security_txt_policies(
        self,
    ) -> resources.security_txt_policies.SecurityTXTPolicies:
        return resources.security_txt_policies.SecurityTXTPolicies(self)

    @cached_property
    def firewall_groups(self) -> resources.firewall_groups.FirewallGroups:
        return resources.firewall_groups.FirewallGroups(self)

    @cached_property
    def custom_config_snippets(
        self,
    ) -> resources.custom_config_snippets.CustomConfigSnippets:
        return resources.custom_config_snippets.CustomConfigSnippets(self)

    @cached_property
    def custom_configs(self) -> resources.custom_configs.CustomConfigs:
        return resources.custom_configs.CustomConfigs(self)

    @cached_property
    def ftp_users(self) -> resources.ftp_users.FTPUsers:
        return resources.ftp_users.FTPUsers(self)

    @cached_property
    def cmses(self) -> resources.cmses.CMSes:
        return resources.cmses.CMSes(self)

    @cached_property
    def fpm_pools(self) -> resources.fpm_pools.FPMPools:
        return resources.fpm_pools.FPMPools(self)

    @cached_property
    def passenger_apps(self) -> resources.passenger_apps.PassengerApps:
        return resources.passenger_apps.PassengerApps(self)

    @cached_property
    def redis_instances(self) -> resources.redis_instances.RedisInstances:
        return resources.redis_instances.RedisInstances(self)

    @cached_property
    def task_collections(self) -> resources.task_collections.TaskCollections:
        return resources.task_collections.TaskCollections(self)

    @cached_property
    def nodes(self) -> resources.nodes.Nodes:
        return resources.nodes.Nodes(self)

    @cached_property
    def unix_users(self) -> resources.unix_users.UNIXUsers:
        return resources.unix_users.UNIXUsers(self)

    @cached_property
    def logs(self) -> resources.logs.Logs:
        return resources.logs.Logs(self)

    @cached_property
    def ssh_keys(self) -> resources.ssh_keys.SSHKeys:
        return resources.ssh_keys.SSHKeys(self)

    @cached_property
    def root_ssh_keys(self) -> resources.root_ssh_keys.RootSSHKeys:
        return resources.root_ssh_keys.RootSSHKeys(self)

    @cached_property
    def malwares(self) -> resources.malwares.Malwares:
        return resources.malwares.Malwares(self)

    @cached_property
    def databases(self) -> resources.databases.Databases:
        return resources.databases.Databases(self)

    @cached_property
    def database_users(self) -> resources.database_users.DatabaseUsers:
        return resources.database_users.DatabaseUsers(self)

    @cached_property
    def database_user_grants(self) -> resources.database_user_grants.DatabaseUserGrants:
        return resources.database_user_grants.DatabaseUserGrants(self)

    @cached_property
    def mail_domains(self) -> resources.mail_domains.MailDomains:
        return resources.mail_domains.MailDomains(self)

    @cached_property
    def mail_accounts(self) -> resources.mail_accounts.MailAccounts:
        return resources.mail_accounts.MailAccounts(self)

    @cached_property
    def mail_aliases(self) -> resources.mail_aliases.MailAliases:
        return resources.mail_aliases.MailAliases(self)

    @cached_property
    def health(self) -> resources.health.Health:
        return resources.health.Health(self)
