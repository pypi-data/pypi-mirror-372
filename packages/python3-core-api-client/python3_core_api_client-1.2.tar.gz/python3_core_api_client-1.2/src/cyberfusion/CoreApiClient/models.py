from datetime import datetime
from enum import StrEnum, IntEnum
from ipaddress import IPv4Address, IPv6Address
from typing import Dict, List, Literal, Optional, Union, Any

from pydantic import UUID4, AnyUrl, EmailStr, Field, confloat, conint, constr, BaseModel
from typing import Iterator


class CoreApiModel(BaseModel):
    pass


class RootModelCollectionMixin:
    """Mixin supporting iterating over and accessing items in a root model, without explicitly accessing __root__.

    Inspired by https://docs.pydantic.dev/2.0/usage/models/#rootmodel-and-custom-root-types
    """

    __root__: dict | list | None

    def __iter__(self) -> Iterator:
        if not isinstance(self.__root__, (list, dict)):
            raise TypeError("Type does not support iter")

        return iter(self.__root__)

    def __getitem__(self, item: Any) -> Any:
        if not isinstance(self.__root__, (list, dict)):
            raise TypeError("Type does not support getitem")

        return self.__root__[item]

    def items(self) -> Any:
        if not isinstance(self.__root__, (dict)):
            raise TypeError("Type does not support items")

        return self.__root__.items()


class ObjectLogTypeEnum(StrEnum):
    Create = "Create"
    Update = "Update"
    Delete = "Delete"


class CauserTypeEnum(StrEnum):
    API_User = "API User"


class HTTPMethod(StrEnum):
    CONNECT = "CONNECT"
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


class APIUserAuthenticationMethod(StrEnum):
    API_KEY = "API Key"
    JWT_TOKEN = "JWT Token"


class APIUserInfo(CoreApiModel):
    id: int = Field(..., title="Id")
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Username"
    )
    is_active: bool = Field(..., title="Is Active")
    is_superuser: bool = Field(..., title="Is Superuser")
    clusters: List[int] = Field(..., title="Clusters", unique_items=True)
    customer_id: Optional[int] = Field(..., title="Customer Id")
    authentication_method: APIUserAuthenticationMethod


class AllowOverrideDirectiveEnum(StrEnum):
    ALL = "All"
    AUTHCONFIG = "AuthConfig"
    FILEINFO = "FileInfo"
    INDEXES = "Indexes"
    LIMIT = "Limit"
    NONE = "None"


class AllowOverrideOptionDirectiveEnum(StrEnum):
    ALL = "All"
    FOLLOWSYMLINKS = "FollowSymLinks"
    INDEXES = "Indexes"
    MULTIVIEWS = "MultiViews"
    SYMLINKSIFOWNERMATCH = "SymLinksIfOwnerMatch"
    NONE = "None"


class BasicAuthenticationRealmCreateRequest(CoreApiModel):
    directory_path: Optional[str] = Field(
        ...,
        description="Specify null for entire virtual host document root. If the specified virtual host uses the server software Apache, must be in its domain root (`domain_root`).",
        title="Directory Path",
    )
    virtual_host_id: int = Field(
        ...,
        description="Must have same UNIX user as specified htpasswd file.",
        title="Virtual Host Id",
    )
    name: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    htpasswd_file_id: int = Field(
        ...,
        description="Must have same UNIX user as specified virtual host.",
        title="Htpasswd File Id",
    )


class BasicAuthenticationRealmUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    directory_path: Optional[str] = Field(
        ...,
        description="Specify null for entire virtual host document root. If the specified virtual host uses the server software Apache, must be in its domain root (`domain_root`).",
        title="Directory Path",
    )
    virtual_host_id: int = Field(
        ...,
        description="Must have same UNIX user as specified htpasswd file.",
        title="Virtual Host Id",
    )
    name: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    htpasswd_file_id: int = Field(
        ...,
        description="Must have same UNIX user as specified virtual host.",
        title="Htpasswd File Id",
    )


class BasicAuthenticationRealmUpdateRequest(CoreApiModel):
    name: Optional[constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64)] = (
        Field(None, title="Name")
    )
    htpasswd_file_id: Optional[int] = Field(
        None,
        description="Must have same UNIX user as specified virtual host.",
        title="Htpasswd File Id",
    )


class BodyLoginAccessToken(CoreApiModel):
    grant_type: Optional[constr(regex=r"^password$")] = Field(None, title="Grant Type")
    username: str = Field(..., title="Username")
    password: str = Field(..., title="Password")
    scope: Optional[str] = Field("", title="Scope")
    client_id: Optional[str] = Field(None, title="Client Id")
    client_secret: Optional[str] = Field(None, title="Client Secret")


class BorgArchiveContentObjectTypeEnum(StrEnum):
    REGULAR_FILE = "regular_file"
    DIRECTORY = "directory"
    SYMBOLIC_LINK = "symbolic_link"


class BorgArchiveCreateDatabaseRequest(CoreApiModel):
    borg_repository_id: int = Field(..., title="Borg Repository Id")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    database_id: int = Field(..., title="Database Id")


class BorgArchiveCreateUNIXUserRequest(CoreApiModel):
    borg_repository_id: int = Field(..., title="Borg Repository Id")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")


class BorgArchiveMetadata(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    borg_archive_id: int = Field(..., title="Borg Archive Id")
    exists_on_server: bool = Field(..., title="Exists On Server")
    contents_path: Optional[str] = Field(..., title="Contents Path")


class BorgRepositoryCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    passphrase: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Passphrase"
    )
    remote_host: str = Field(..., title="Remote Host")
    remote_path: str = Field(..., title="Remote Path")
    remote_username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = (
        Field(..., title="Remote Username")
    )
    unix_user_id: Optional[int] = Field(
        ...,
        description="If you want to use a Borg repository to create Borg archives of a UNIX user, set this to the ID of that UNIX user. If this is set, the Borg repository cannot be used for Borg archives of databases.",
        title="Unix User Id",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    keep_hourly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Hourly",
    )
    keep_daily: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Daily",
    )
    keep_weekly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Weekly",
    )
    keep_monthly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Monthly",
    )
    keep_yearly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Yearly",
    )
    identity_file_path: Optional[str] = Field(
        ...,
        description="Must be set when UNIX user (`unix_user_id`) is set. May not be set otherwise.",
        title="Identity File Path",
    )


class BorgRepositoryUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    passphrase: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Passphrase"
    )
    remote_host: str = Field(..., title="Remote Host")
    remote_path: str = Field(..., title="Remote Path")
    remote_username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = (
        Field(..., title="Remote Username")
    )
    cluster_id: int = Field(..., title="Cluster Id")
    keep_hourly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Hourly",
    )
    keep_daily: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Daily",
    )
    keep_weekly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Weekly",
    )
    keep_monthly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Monthly",
    )
    keep_yearly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Yearly",
    )
    identity_file_path: Optional[str] = Field(
        ...,
        description="Must be set when UNIX user (`unix_user_id`) is set. May not be set otherwise.",
        title="Identity File Path",
    )
    unix_user_id: Optional[int] = Field(..., title="Unix User Id")


class BorgRepositoryUpdateRequest(CoreApiModel):
    keep_hourly: Optional[int] = Field(
        None,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Hourly",
    )
    keep_daily: Optional[int] = Field(
        None,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Daily",
    )
    keep_weekly: Optional[int] = Field(
        None,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Weekly",
    )
    keep_monthly: Optional[int] = Field(
        None,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Monthly",
    )
    keep_yearly: Optional[int] = Field(
        None,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Yearly",
    )
    identity_file_path: Optional[str] = Field(
        None,
        description="Must be set when UNIX user (`unix_user_id`) is set. May not be set otherwise.",
        title="Identity File Path",
    )


class CMSConfigurationConstant(CoreApiModel):
    value: Union[str, int, float, bool] = Field(..., title="Value")
    index: Optional[conint(ge=0)] = Field(None, title="Index")
    name: constr(regex=r"^[a-zA-Z0-9_]+$", min_length=1) = Field(..., title="Name")


class CMSConfigurationConstantUpdateDeprecatedRequest(CoreApiModel):
    value: Union[str, int, float, bool] = Field(..., title="Value")
    index: Optional[conint(ge=0)] = Field(None, title="Index")


class CMSConfigurationConstantUpdateRequest(CoreApiModel):
    value: Union[str, int, float, bool] = Field(..., title="Value")
    index: Optional[conint(ge=0)] = Field(None, title="Index")


class CMSInstallNextCloudRequest(CoreApiModel):
    database_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63) = (
        Field(..., title="Database Name")
    )
    database_user_name: constr(
        regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63
    ) = Field(..., title="Database User Name")
    database_user_password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = (
        Field(..., title="Database User Password")
    )
    database_host: str = Field(..., title="Database Host")
    admin_username: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60) = (
        Field(..., title="Admin Username")
    )
    admin_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Admin Password"
    )


class CMSInstallWordPressRequest(CoreApiModel):
    database_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63) = (
        Field(..., title="Database Name")
    )
    database_user_name: constr(
        regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63
    ) = Field(..., title="Database User Name")
    database_user_password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = (
        Field(..., title="Database User Password")
    )
    database_host: str = Field(..., title="Database Host")
    admin_username: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60) = (
        Field(..., title="Admin Username")
    )
    admin_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Admin Password"
    )
    site_title: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=253) = (
        Field(..., title="Site Title")
    )
    site_url: AnyUrl = Field(..., title="Site Url")
    locale: constr(regex=r"^[a-zA-Z_]+$", min_length=1, max_length=15) = Field(
        ..., title="Locale"
    )
    version: constr(regex=r"^[0-9.]+$", min_length=1, max_length=6) = Field(
        ..., title="Version"
    )
    admin_email_address: EmailStr = Field(..., title="Admin Email Address")


class CMSOneTimeLogin(CoreApiModel):
    url: AnyUrl = Field(..., title="Url")


class CMSOptionNameEnum(StrEnum):
    BLOG_PUBLIC = "blog_public"


class CMSOptionUpdateDeprecatedRequest(CoreApiModel):
    value: conint(ge=0, le=1) = Field(..., title="Value")


class CMSOptionUpdateRequest(CoreApiModel):
    value: conint(ge=0, le=1) = Field(..., title="Value")


class CMSPlugin(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9_]+$", min_length=1) = Field(..., title="Name")
    current_version: constr(regex=r"^[a-z0-9.-]+$", min_length=1) = Field(
        ..., title="Current Version"
    )
    available_version: Optional[constr(regex=r"^[a-z0-9.-]+$", min_length=1)] = Field(
        ..., title="Available Version"
    )
    is_enabled: bool = Field(..., title="Is Enabled")


class CMSSoftwareNameEnum(StrEnum):
    WORDPRESS = "WordPress"
    NEXTCLOUD = "NextCloud"


class CMSThemeInstallFromRepositoryRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60) = Field(
        ..., title="Name"
    )
    version: Optional[constr(regex=r"^[0-9.]+$", min_length=1, max_length=6)] = Field(
        ..., title="Version"
    )


class CMSThemeInstallFromURLRequest(CoreApiModel):
    url: AnyUrl = Field(..., title="Url")


class CMSUserCredentialsUpdateRequest(CoreApiModel):
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )


class CertificateCreateRequest(CoreApiModel):
    certificate: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535
    ) = Field(
        ...,
        description="Certificate must have a common name.\n\nMust end with line feed.",
        title="Certificate",
    )
    ca_chain: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535
    ) = Field(..., description="Must end with line feed.", title="Ca Chain")
    private_key: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535
    ) = Field(..., description="Must end with line feed.", title="Private Key")
    cluster_id: int = Field(..., title="Cluster Id")


class CertificateManagerUpdateRequest(CoreApiModel):
    request_callback_url: Optional[AnyUrl] = Field(None, title="Request Callback Url")


class CertificateProviderNameEnum(StrEnum):
    LETS_ENCRYPT = "lets_encrypt"


class ClusterBorgSSHKey(CoreApiModel):
    public_key: str = Field(..., title="Public Key")


class NodejsVersion(CoreApiModel):
    __hash__ = object.__hash__

    __root__: constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")


class ClusterGroupEnum(StrEnum):
    WEB = "Web"
    MAIL = "Mail"
    DATABASE = "Database"
    BORG_CLIENT = "Borg Client"
    BORG_SERVER = "Borg Server"
    REDIRECT = "Redirect"


class ClusterIPAddress(CoreApiModel):
    ip_address: Union[IPv6Address, IPv4Address] = Field(..., title="Ip Address")
    dns_name: Optional[str] = Field(..., title="Dns Name")
    l3_ddos_protection_enabled: bool = Field(..., title="L3 Ddos Protection Enabled")


class ClusterIPAddresses(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Dict[str, List[ClusterIPAddress]]]] = None


class CronCreateRequest(CoreApiModel):
    node_id: Optional[int] = Field(
        ...,
        description="The node this cron will run on.\n\nDefaults to node with Admin group.",
        title="Node Id",
    )
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Use the variable `$CYBERFUSION_DEFAULT_PHP_VERSION_BINARY` to use the UNIX user default PHP version (`default_php_version`). For more information, see 'Differences between PHP versions'.\n\nThe command may not call `exit`.",
        title="Command",
    )
    email_address: Optional[EmailStr] = Field(
        ...,
        description="Emails about failed cron runs are sent to this email address. If the value is null, emails are sent to Cyberfusion.\n\nThis email contains the return code and output.\n\nA cron run has failed when the command exits with a return code other than 0.\n\nIf the cron fails over 10 times consecutively, no more emails are sent.",
        title="Email Address",
    )
    schedule: str = Field(..., title="Schedule")
    error_count: int = Field(
        ...,
        description="Send email after N failed cron runs.\n\nThe counter is reset after a successful cron run.\n\nIf you don't know what to set, set to `1`, so an email is sent after 1 failed cron run. This ensures an email is sent for _every_ failed cron run.",
        title="Error Count",
    )
    random_delay_max_seconds: int = Field(
        ...,
        description="Randomly delay cron run.\n\nUse to avoid overloading a node when many crons run on the same schedule.\n\nIf you don't know what to set, set to `10`.",
        title="Random Delay Max Seconds",
    )
    timeout_seconds: Optional[int] = Field(
        ...,
        description="Cron will be automatically killed after this time. Such a timeout is usually used as a failsafe, so that when the command unexpectedly takes too long (e.g. due to an external API call by a script), the cron isn't stuck (or locked if `locking_enabled` is `true`) for a long or indefinite time.",
        title="Timeout Seconds",
    )
    locking_enabled: bool = Field(
        ...,
        description="When enabled, multiple instances of the cron may not run simultaneously. This can prevent multiple crons from manipulating the same data, or prevent a node from being overloaded when a long-running cron is using many resources.\n\nDisable for crons that handle locking themselves (such as Laravel's `withoutOverlapping`.)",
        title="Locking Enabled",
    )
    is_active: bool = Field(..., title="Is Active")
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the daemon is restarted.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )
    cpu_limit: Optional[int] = Field(
        None,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )


class CronUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: int = Field(..., title="Node Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Use the variable `$CYBERFUSION_DEFAULT_PHP_VERSION_BINARY` to use the UNIX user default PHP version (`default_php_version`). For more information, see 'Differences between PHP versions'.\n\nThe command may not call `exit`.",
        title="Command",
    )
    email_address: Optional[EmailStr] = Field(
        ...,
        description="Emails about failed cron runs are sent to this email address. If the value is null, emails are sent to Cyberfusion.\n\nThis email contains the return code and output.\n\nA cron run has failed when the command exits with a return code other than 0.\n\nIf the cron fails over 10 times consecutively, no more emails are sent.",
        title="Email Address",
    )
    schedule: str = Field(..., title="Schedule")
    error_count: int = Field(
        ...,
        description="Send email after N failed cron runs.\n\nThe counter is reset after a successful cron run.\n\nIf you don't know what to set, set to `1`, so an email is sent after 1 failed cron run. This ensures an email is sent for _every_ failed cron run.",
        title="Error Count",
    )
    random_delay_max_seconds: int = Field(
        ...,
        description="Randomly delay cron run.\n\nUse to avoid overloading a node when many crons run on the same schedule.\n\nIf you don't know what to set, set to `10`.",
        title="Random Delay Max Seconds",
    )
    timeout_seconds: Optional[int] = Field(
        ...,
        description="Cron will be automatically killed after this time. Such a timeout is usually used as a failsafe, so that when the command unexpectedly takes too long (e.g. due to an external API call by a script), the cron isn't stuck (or locked if `locking_enabled` is `true`) for a long or indefinite time.",
        title="Timeout Seconds",
    )
    locking_enabled: bool = Field(
        ...,
        description="When enabled, multiple instances of the cron may not run simultaneously. This can prevent multiple crons from manipulating the same data, or prevent a node from being overloaded when a long-running cron is using many resources.\n\nDisable for crons that handle locking themselves (such as Laravel's `withoutOverlapping`.)",
        title="Locking Enabled",
    )
    is_active: bool = Field(..., title="Is Active")


class CronUpdateRequest(CoreApiModel):
    command: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)] = (
        Field(
            None,
            description="Use the variable `$CYBERFUSION_DEFAULT_PHP_VERSION_BINARY` to use the UNIX user default PHP version (`default_php_version`). For more information, see 'Differences between PHP versions'.\n\nThe command may not call `exit`.",
            title="Command",
        )
    )
    email_address: Optional[EmailStr] = Field(
        None,
        description="Emails about failed cron runs are sent to this email address. If the value is null, emails are sent to Cyberfusion.\n\nThis email contains the return code and output.\n\nA cron run has failed when the command exits with a return code other than 0.\n\nIf the cron fails over 10 times consecutively, no more emails are sent.",
        title="Email Address",
    )
    schedule: Optional[str] = Field(None, title="Schedule")
    error_count: Optional[int] = Field(
        None,
        description="Send email after N failed cron runs.\n\nThe counter is reset after a successful cron run.\n\nIf you don't know what to set, set to `1`, so an email is sent after 1 failed cron run. This ensures an email is sent for _every_ failed cron run.",
        title="Error Count",
    )
    random_delay_max_seconds: Optional[int] = Field(
        None,
        description="Randomly delay cron run.\n\nUse to avoid overloading a node when many crons run on the same schedule.\n\nIf you don't know what to set, set to `10`.",
        title="Random Delay Max Seconds",
    )
    timeout_seconds: Optional[int] = Field(
        None,
        description="Cron will be automatically killed after this time. Such a timeout is usually used as a failsafe, so that when the command unexpectedly takes too long (e.g. due to an external API call by a script), the cron isn't stuck (or locked if `locking_enabled` is `true`) for a long or indefinite time.",
        title="Timeout Seconds",
    )
    locking_enabled: Optional[bool] = Field(
        None,
        description="When enabled, multiple instances of the cron may not run simultaneously. This can prevent multiple crons from manipulating the same data, or prevent a node from being overloaded when a long-running cron is using many resources.\n\nDisable for crons that handle locking themselves (such as Laravel's `withoutOverlapping`.)",
        title="Locking Enabled",
    )
    is_active: Optional[bool] = Field(None, title="Is Active")
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the daemon is restarted.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )
    cpu_limit: Optional[int] = Field(
        None,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )
    node_id: Optional[int] = Field(
        None,
        description="The node this cron will run on.\n\nDefaults to node with Admin group.",
        title="Node Id",
    )


class CustomConfigServerSoftwareNameEnum(StrEnum):
    NGINX = "nginx"


class CustomConfigSnippetTemplateNameEnum(StrEnum):
    LARAVEL = "Laravel"
    COMPRESSION = "Compression"


class CustomConfigSnippetUpdateRequest(CoreApiModel):
    contents: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)] = (
        Field(None, title="Contents")
    )
    is_default: Optional[bool] = Field(
        None,
        description="Automatically include in all virtual hosts custom configs.",
        title="Is Default",
    )


class CustomConfigUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.",
        title="Contents",
    )
    server_software_name: CustomConfigServerSoftwareNameEnum


class CustomConfigUpdateRequest(CoreApiModel):
    contents: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)] = (
        Field(
            None,
            description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.",
            title="Contents",
        )
    )


class CustomerIPAddressDatabase(CoreApiModel):
    ip_address: Union[IPv6Address, IPv4Address] = Field(..., title="Ip Address")
    dns_name: Optional[str] = Field(..., title="Dns Name")


class CustomerIPAddresses(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Dict[str, List[CustomerIPAddressDatabase]]]] = None


class CustomerIncludes(CoreApiModel):
    pass


class CustomerResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    identifier: constr(regex=r"^[a-z0-9]+$", min_length=2, max_length=4) = Field(
        ..., title="Identifier"
    )
    dns_subdomain: str = Field(..., title="Dns Subdomain")
    is_internal: bool = Field(..., title="Is Internal")
    team_code: constr(regex=r"^[A-Z0-9]+$", min_length=4, max_length=6) = Field(
        ..., title="Team Code"
    )
    includes: CustomerIncludes


class DaemonCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Command"
    )
    nodes_ids: List[int] = Field(..., min_items=1, title="Nodes Ids", unique_items=True)
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the daemon is restarted.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )
    cpu_limit: Optional[int] = Field(
        None,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )


class DaemonUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Command"
    )
    nodes_ids: List[int] = Field(..., min_items=1, title="Nodes Ids", unique_items=True)


class DaemonUpdateRequest(CoreApiModel):
    command: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)] = (
        Field(None, title="Command")
    )
    nodes_ids: Optional[List[int]] = Field(None, title="Nodes Ids")
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the daemon is restarted.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )
    cpu_limit: Optional[int] = Field(
        None,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent a daemon from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )


class IdenticalTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class NotIdenticalTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class OnlyLeftTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class OnlyRightTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class DatabaseComparison(CoreApiModel):
    identical_tables_names: List[IdenticalTablesName] = Field(
        ..., title="Identical Tables Names", unique_items=True
    )
    not_identical_tables_names: List[NotIdenticalTablesName] = Field(
        ..., title="Not Identical Tables Names", unique_items=True
    )
    only_left_tables_names: List[OnlyLeftTablesName] = Field(
        ..., title="Only Left Tables Names", unique_items=True
    )
    only_right_tables_names: List[OnlyRightTablesName] = Field(
        ..., title="Only Right Tables Names", unique_items=True
    )


class DatabaseServerSoftwareNameEnum(StrEnum):
    MARIADB = "MariaDB"
    POSTGRESQL = "PostgreSQL"


class DatabaseUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    optimizing_enabled: bool = Field(
        ...,
        description="Periodically automatically run `OPTIMIZE` on database.\n\nEnabling is only supported for MariaDB server software.",
        title="Optimizing Enabled",
    )
    backups_enabled: bool = Field(
        ...,
        description="Periodically automatically create backup of database.\n\nDisabling is only supported for MariaDB server software.",
        title="Backups Enabled",
    )


class DatabaseUpdateRequest(CoreApiModel):
    optimizing_enabled: Optional[bool] = Field(
        None,
        description="Periodically automatically run `OPTIMIZE` on database.\n\nEnabling is only supported for MariaDB server software.",
        title="Optimizing Enabled",
    )
    backups_enabled: Optional[bool] = Field(
        None,
        description="Periodically automatically create backup of database.\n\nDisabling is only supported for MariaDB server software.",
        title="Backups Enabled",
    )


class DatabaseUsageIncludes(CoreApiModel):
    pass


class DatabaseUsageResource(CoreApiModel):
    database_id: int = Field(..., title="Database Id")
    usage: confloat(ge=0.0) = Field(..., title="Usage")
    timestamp: datetime = Field(..., title="Timestamp")
    includes: DatabaseUsageIncludes


class DatabaseUserUpdateRequest(CoreApiModel):
    phpmyadmin_firewall_groups_ids: Optional[List[int]] = Field(
        None,
        description="Only IP networks in the specified firewall groups may access phpMyAdmin.\n\nIf this is null, all IP networks may.",
        title="Phpmyadmin Firewall Groups Ids",
    )
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = (
        Field(None, description="Passwords are deleted after 7 days.", title="Password")
    )


class DetailMessage(CoreApiModel):
    detail: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Detail"
    )


class DocumentRootFileSuffixEnum(StrEnum):
    PHP = "php"


class DomainRouterCategoryEnum(StrEnum):
    GRAFANA = "Grafana"
    SINGLESTORE_STUDIO = "SingleStore Studio"
    SINGLESTORE_API = "SingleStore API"
    METABASE = "Metabase"
    KIBANA = "Kibana"
    RABBITMQ_MANAGEMENT = "RabbitMQ Management"
    VIRTUAL_HOST = "Virtual Host"
    URL_REDIRECT = "URL Redirect"


class DomainRouterUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    domain: str = Field(..., title="Domain")
    virtual_host_id: Optional[int] = Field(
        ...,
        description="May only be set when `category` is `Virtual Host`.",
        title="Virtual Host Id",
    )
    url_redirect_id: Optional[int] = Field(
        ...,
        description="May only be set when `category` is `URL Redirect`.",
        title="Url Redirect Id",
    )
    category: DomainRouterCategoryEnum
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: Optional[int] = Field(
        ...,
        description="\nWhen set, traffic is routed to the specified node rather than load-balanced over all available nodes (default). This prevents resources (such as FPM pools) from being active on multiple nodes, which can decrease costs.\n\nIf the node is unavailable, traffic is failed over to another node.\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id`.\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n",
        title="Node Id",
    )
    certificate_id: Optional[int] = Field(..., title="Certificate Id")
    security_txt_policy_id: Optional[int] = Field(..., title="Security Txt Policy Id")
    firewall_groups_ids: Optional[List[int]] = Field(
        ...,
        description="Only IP networks in the specified firewall groups may access this domain router.\n\nIf this is null, all IP networks may.\n\nIf this domain router has a wildcard domain (e.g. `*.example.com`), and more specific domain routers exist (e.g. `test.example.com`), the more specific domain router uses the same firewall groups. If the more specific domain router has its own firewall groups, those on the wildcard domain router are ignored.`",
        title="Firewall Groups Ids",
    )
    force_ssl: bool = Field(..., title="Force Ssl")


class DomainRouterUpdateRequest(CoreApiModel):
    node_id: Optional[int] = Field(
        None,
        description="\nWhen set, traffic is routed to the specified node rather than load-balanced over all available nodes (default). This prevents resources (such as FPM pools) from being active on multiple nodes, which can decrease costs.\n\nIf the node is unavailable, traffic is failed over to another node.\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id`.\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n",
        title="Node Id",
    )
    certificate_id: Optional[int] = Field(None, title="Certificate Id")
    security_txt_policy_id: Optional[int] = Field(None, title="Security Txt Policy Id")
    firewall_groups_ids: Optional[List[int]] = Field(
        None,
        description="Only IP networks in the specified firewall groups may access this domain router.\n\nIf this is null, all IP networks may.\n\nIf this domain router has a wildcard domain (e.g. `*.example.com`), and more specific domain routers exist (e.g. `test.example.com`), the more specific domain router uses the same firewall groups. If the more specific domain router has its own firewall groups, those on the wildcard domain router are ignored.`",
        title="Firewall Groups Ids",
    )
    force_ssl: Optional[bool] = Field(None, title="Force Ssl")


class EncryptionTypeEnum(StrEnum):
    TLS = "TLS"
    SSL = "SSL"
    STARTTLS = "STARTTLS"


class FPMPoolCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ...,
        description="We recommend adding the version to the name (e.g. `dropflix83`). As `version` cannot be changed, when wanting to change the version, a new FPM pool must be created. By adding the version to the name, the old and new FPM pools can exist simultaneously without name conflicts (as `name` is unique).",
        title="Name",
    )
    version: str = Field(
        ...,
        description="Must be installed on cluster (`php_versions`).\n\nThis value cannot be changed as it is FPM pool specific. When wanting to change the version, create a new FPM pool, and update it on the virtual host(s) that use the current FPM pool. Or use the CLI command `corectl fpm-pools update-version` which does this for you.",
        title="Version",
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    max_children: int = Field(
        ...,
        description="The maximum amount of concurrent PHP-FPM processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `5`.",
        title="Max Children",
    )
    max_requests: int = Field(
        ...,
        description="Each PHP-FPM process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `20`.",
        title="Max Requests",
    )
    process_idle_timeout: int = Field(
        ...,
        description="Each PHP-FPM process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy PHP-FPM pool (that started many PHP-FPM processes) is no longer busy. However, if all PHP-FPM processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Process Idle Timeout",
    )
    cpu_limit: Optional[int] = Field(
        ...,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent an FPM pool from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )
    log_slow_requests_threshold: Optional[int] = Field(
        ...,
        description="Minimum amount of seconds a request must take to be logged to the PHP-FPM slow log.\n\nTo retrieve the results, contact Cyberfusion.",
        title="Log Slow Requests Threshold",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the FPM pool is restarted.\n\nUse this to prevent an FPM pool from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )


class FPMPoolUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ...,
        description="We recommend adding the version to the name (e.g. `dropflix83`). As `version` cannot be changed, when wanting to change the version, a new FPM pool must be created. By adding the version to the name, the old and new FPM pools can exist simultaneously without name conflicts (as `name` is unique).",
        title="Name",
    )
    version: str = Field(
        ...,
        description="Must be installed on cluster (`php_versions`).\n\nThis value cannot be changed as it is FPM pool specific. When wanting to change the version, create a new FPM pool, and update it on the virtual host(s) that use the current FPM pool. Or use the CLI command `corectl fpm-pools update-version` which does this for you.",
        title="Version",
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    max_children: int = Field(
        ...,
        description="The maximum amount of concurrent PHP-FPM processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `5`.",
        title="Max Children",
    )
    max_requests: int = Field(
        ...,
        description="Each PHP-FPM process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `20`.",
        title="Max Requests",
    )
    process_idle_timeout: int = Field(
        ...,
        description="Each PHP-FPM process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy PHP-FPM pool (that started many PHP-FPM processes) is no longer busy. However, if all PHP-FPM processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Process Idle Timeout",
    )
    cpu_limit: Optional[int] = Field(
        ...,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent an FPM pool from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )
    log_slow_requests_threshold: Optional[int] = Field(
        ...,
        description="Minimum amount of seconds a request must take to be logged to the PHP-FPM slow log.\n\nTo retrieve the results, contact Cyberfusion.",
        title="Log Slow Requests Threshold",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )


class FPMPoolUpdateRequest(CoreApiModel):
    max_children: Optional[int] = Field(
        None,
        description="The maximum amount of concurrent PHP-FPM processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `5`.",
        title="Max Children",
    )
    max_requests: Optional[int] = Field(
        None,
        description="Each PHP-FPM process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `20`.",
        title="Max Requests",
    )
    process_idle_timeout: Optional[int] = Field(
        None,
        description="Each PHP-FPM process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy PHP-FPM pool (that started many PHP-FPM processes) is no longer busy. However, if all PHP-FPM processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Process Idle Timeout",
    )
    cpu_limit: Optional[int] = Field(
        None,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.\n\nUse this to prevent an FPM pool from overloading an entire cluster ('noisy neighbour effect'). Also see `memory_limit`.",
        title="Cpu Limit",
    )
    log_slow_requests_threshold: Optional[int] = Field(
        None,
        description="Minimum amount of seconds a request must take to be logged to the PHP-FPM slow log.\n\nTo retrieve the results, contact Cyberfusion.",
        title="Log Slow Requests Threshold",
    )
    is_namespaced: Optional[bool] = Field(
        None,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    memory_limit: Optional[conint(ge=256)] = Field(
        None,
        description="In MB.\n\nWhen the memory limit is reached, the FPM pool is restarted.\n\nUse this to prevent an FPM pool from overloading an entire cluster ('noisy neighbour effect'). Also see `cpu_limit`.",
        title="Memory Limit",
    )


class FTPUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_.@]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )
    directory_path: str = Field(
        ...,
        description="The directory path must start with the UNIX user home directory. The path may end there, or it can end with custom path elements under it.",
        title="Directory Path",
    )


class FTPUserUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    username: constr(regex=r"^[a-z0-9-_.@]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    directory_path: str = Field(
        ...,
        description="The directory path must start with the UNIX user home directory. The path may end there, or it can end with custom path elements under it.",
        title="Directory Path",
    )
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )


class FTPUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = (
        Field(None, title="Password")
    )
    directory_path: Optional[str] = Field(
        None,
        description="The directory path must start with the UNIX user home directory. The path may end there, or it can end with custom path elements under it.",
        title="Directory Path",
    )


class FirewallGroupCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9_]+$", min_length=1, max_length=32) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    ip_networks: List[str] = Field(
        ...,
        description="To specify a single IP address, use the /128 (IPv6) or /32 (IPv4) CIDR.\n\nFor example: `2001:0db8:8aa:bc:111:abcd:aa11:8991/128` or `192.0.2.6/32`.",
        min_items=1,
        title="Ip Networks",
        unique_items=True,
    )


class FirewallGroupUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9_]+$", min_length=1, max_length=32) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    ip_networks: List[str] = Field(
        ...,
        description="To specify a single IP address, use the /128 (IPv6) or /32 (IPv4) CIDR.\n\nFor example: `2001:0db8:8aa:bc:111:abcd:aa11:8991/128` or `192.0.2.6/32`.",
        min_items=1,
        title="Ip Networks",
        unique_items=True,
    )


class FirewallGroupUpdateRequest(CoreApiModel):
    ip_networks: Optional[List[str]] = Field(
        None,
        description="To specify a single IP address, use the /128 (IPv6) or /32 (IPv4) CIDR.\n\nFor example: `2001:0db8:8aa:bc:111:abcd:aa11:8991/128` or `192.0.2.6/32`.",
        title="Ip Networks",
    )


class FirewallRuleExternalProviderNameEnum(StrEnum):
    ATLASSIAN = "Atlassian"
    AWS = "AWS"
    BUDDY = "Buddy"
    GOOGLE_CLOUD = "Google Cloud"


class FirewallRuleServiceNameEnum(StrEnum):
    SSH = "SSH"
    PROFTPD = "ProFTPD"
    NGINX = "nginx"
    APACHE = "Apache"


class HAProxyListenToNodeCreateRequest(CoreApiModel):
    haproxy_listen_id: int = Field(..., title="Haproxy Listen Id")
    node_id: int = Field(
        ..., description="Node must have HAProxy group.", title="Node Id"
    )


class HTTPRetryConditionEnum(StrEnum):
    CONNECTION_FAILURE = "Connection failure"
    EMPTY_RESPONSE = "Empty response"
    JUNK_RESPONSE = "Junk response"
    RESPONSE_TIMEOUT = "Response timeout"
    ZERO_RTT_REJECTED = "0-RTT rejected"
    HTTP_STATUS_401 = "HTTP status 401"
    HTTP_STATUS_403 = "HTTP status 403"
    HTTP_STATUS_404 = "HTTP status 404"
    HTTP_STATUS_408 = "HTTP status 408"
    HTTP_STATUS_425 = "HTTP status 425"
    HTTP_STATUS_500 = "HTTP status 500"
    HTTP_STATUS_501 = "HTTP status 501"
    HTTP_STATUS_502 = "HTTP status 502"
    HTTP_STATUS_503 = "HTTP status 503"
    HTTP_STATUS_504 = "HTTP status 504"


class HTTPRetryProperties(CoreApiModel):
    tries_amount: Optional[conint(ge=1, le=3)] = Field(..., title="Tries Amount")
    tries_failover_amount: Optional[conint(ge=1, le=3)] = Field(
        ..., title="Tries Failover Amount"
    )
    conditions: List[HTTPRetryConditionEnum] = Field(
        ..., title="Conditions", unique_items=True
    )


class HealthStatusEnum(StrEnum):
    UP = "up"
    MAINTENANCE = "maintenance"


class HostEnum(StrEnum):
    ALL = "%"
    LOCALHOST_IPV6 = "::1"


class HostsEntryCreateRequest(CoreApiModel):
    node_id: int = Field(
        ...,
        description="Route lookups for hostname to specified node.",
        title="Node Id",
    )
    host_name: str = Field(..., title="Host Name")
    cluster_id: int = Field(..., title="Cluster Id")


class HtpasswdFileCreateRequest(CoreApiModel):
    unix_user_id: int = Field(..., title="Unix User Id")


class HtpasswdUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=255) = Field(
        ..., title="Username"
    )
    htpasswd_file_id: int = Field(..., title="Htpasswd File Id")
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )


class HtpasswdUserUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=255) = Field(
        ..., title="Username"
    )
    htpasswd_file_id: int = Field(..., title="Htpasswd File Id")
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )


class HtpasswdUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = (
        Field(None, title="Password")
    )


class IPAddressFamilyEnum(StrEnum):
    IPV6 = "IPv6"
    IPV4 = "IPv4"


class IPAddressProductTypeEnum(StrEnum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"


class LanguageCodeEnum(StrEnum):
    NL = "nl"
    EN = "en"


class LoadBalancingMethodEnum(StrEnum):
    ROUND_ROBIN = "Round Robin"
    SOURCE_IP_ADDRESS = "Source IP Address"


class LogMethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"
    HEAD = "HEAD"


class LogSortOrderEnum(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class MailAccountCreateRequest(CoreApiModel):
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail alias in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    password: constr(regex=r"^[ -~]+$", min_length=6, max_length=255) = Field(
        ..., title="Password"
    )
    quota: Optional[int] = Field(
        ...,
        description="When the quota has been reached, emails will be bounced.\n\nIn MB.",
        title="Quota",
    )


class MailAccountUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail alias in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    cluster_id: int = Field(..., title="Cluster Id")
    quota: Optional[int] = Field(
        ...,
        description="When the quota has been reached, emails will be bounced.\n\nIn MB.",
        title="Quota",
    )
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )


class MailAccountUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=6, max_length=255)] = Field(
        None, title="Password"
    )
    quota: Optional[int] = Field(
        None,
        description="When the quota has been reached, emails will be bounced.\n\nIn MB.",
        title="Quota",
    )


class MailAccountUsageIncludes(CoreApiModel):
    pass


class MailAccountUsageResource(CoreApiModel):
    mail_account_id: int = Field(..., title="Mail Account Id")
    usage: confloat(ge=0.0) = Field(..., title="Usage")
    timestamp: datetime = Field(..., title="Timestamp")
    includes: MailAccountUsageIncludes


class MailAliasCreateRequest(CoreApiModel):
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail account in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    forward_email_addresses: List[EmailStr] = Field(
        ..., min_items=1, title="Forward Email Addresses", unique_items=True
    )


class MailAliasUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail account in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    forward_email_addresses: List[EmailStr] = Field(
        ..., min_items=1, title="Forward Email Addresses", unique_items=True
    )


class MailAliasUpdateRequest(CoreApiModel):
    forward_email_addresses: Optional[List[EmailStr]] = Field(
        None, title="Forward Email Addresses"
    )


class MailDomainCreateRequest(CoreApiModel):
    domain: str = Field(..., title="Domain")
    unix_user_id: int = Field(..., title="Unix User Id")
    catch_all_forward_email_addresses: List[EmailStr] = Field(
        ..., title="Catch All Forward Email Addresses", unique_items=True
    )
    is_local: bool = Field(
        ...,
        description="Set to `true` when MX records point to cluster. Set to `false` when mail domain exists on cluster, but MX records point elsewhere.\n\nWhen this value is `false`, emails sent from other mail accounts on the same cluster will not be delivered locally, but sent to the MX records.",
        title="Is Local",
    )


class MailDomainUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    domain: str = Field(..., title="Domain")
    unix_user_id: int = Field(..., title="Unix User Id")
    catch_all_forward_email_addresses: List[EmailStr] = Field(
        ..., title="Catch All Forward Email Addresses", unique_items=True
    )
    is_local: bool = Field(
        ...,
        description="Set to `true` when MX records point to cluster. Set to `false` when mail domain exists on cluster, but MX records point elsewhere.\n\nWhen this value is `false`, emails sent from other mail accounts on the same cluster will not be delivered locally, but sent to the MX records.",
        title="Is Local",
    )


class MailDomainUpdateRequest(CoreApiModel):
    catch_all_forward_email_addresses: Optional[List[EmailStr]] = Field(
        None, title="Catch All Forward Email Addresses"
    )
    is_local: Optional[bool] = Field(
        None,
        description="Set to `true` when MX records point to cluster. Set to `false` when mail domain exists on cluster, but MX records point elsewhere.\n\nWhen this value is `false`, emails sent from other mail accounts on the same cluster will not be delivered locally, but sent to the MX records.",
        title="Is Local",
    )


class MailHostnameCreateRequest(CoreApiModel):
    domain: str = Field(..., title="Domain")
    cluster_id: int = Field(..., title="Cluster Id")
    certificate_id: Optional[int] = Field(..., title="Certificate Id")


class MailHostnameUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    domain: str = Field(..., title="Domain")
    cluster_id: int = Field(..., title="Cluster Id")
    certificate_id: Optional[int] = Field(..., title="Certificate Id")


class MailHostnameUpdateRequest(CoreApiModel):
    certificate_id: Optional[int] = Field(None, title="Certificate Id")


class MariaDBEncryptionKeyCreateRequest(CoreApiModel):
    cluster_id: int = Field(..., title="Cluster Id")


class MariaDBPrivilegeEnum(StrEnum):
    ALL = "ALL"
    SELECT = "SELECT"


class MeilisearchEnvironmentEnum(StrEnum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class NestedPathsDict(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Optional["NestedPathsDict"]]] = None


class NodeAddOnCreateRequest(CoreApiModel):
    node_id: int = Field(..., title="Node Id")
    product: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64) = Field(
        ...,
        description="Get available products with `GET /node-add-ons/products`.",
        title="Product",
    )
    quantity: int = Field(..., title="Quantity")


class NodeAddOnProduct(CoreApiModel):
    uuid: UUID4 = Field(..., title="Uuid")
    name: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    memory_gib: Optional[int] = Field(..., title="Memory Gib")
    cpu_cores: Optional[int] = Field(..., title="Cpu Cores")
    disk_gib: Optional[int] = Field(..., title="Disk Gib")
    price: confloat(ge=0.0) = Field(..., title="Price")
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2) = Field(
        ..., title="Period"
    )
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3) = Field(
        ..., title="Currency"
    )


class NodeGroupEnum(StrEnum):
    ADMIN = "Admin"
    APACHE = "Apache"
    PROFTPD = "ProFTPD"
    NGINX = "nginx"
    DOVECOT = "Dovecot"
    MARIADB = "MariaDB"
    POSTGRESQL = "PostgreSQL"
    PHP = "PHP"
    PASSENGER = "Passenger"
    BORG = "Borg"
    FAST_REDIRECT = "Fast Redirect"
    HAPROXY = "HAProxy"
    REDIS = "Redis"
    COMPOSER = "Composer"
    WP_CLI = "WP-CLI"
    KERNELCARE = "KernelCare"
    IMAGEMAGICK = "ImageMagick"
    WKHTMLTOPDF = "wkhtmltopdf"
    GNU_MAILUTILS = "GNU Mailutils"
    CLAMAV = "ClamAV"
    PUPPETEER = "Puppeteer"
    LIBREOFFICE = "LibreOffice"
    GHOSTSCRIPT = "Ghostscript"
    FFMPEG = "FFmpeg"
    DOCKER = "Docker"
    MEILISEARCH = "Meilisearch"
    NEW_RELIC = "New Relic"
    MALDET = "maldet"
    NODEJS = "NodeJS"
    GRAFANA = "Grafana"
    SINGLESTORE = "SingleStore"
    METABASE = "Metabase"
    ELASTICSEARCH = "Elasticsearch"
    RABBITMQ = "RabbitMQ"


class NodeMariaDBGroupProperties(CoreApiModel):
    is_master: bool = Field(..., title="Is Master")


class NodeProduct(CoreApiModel):
    uuid: UUID4 = Field(..., title="Uuid")
    name: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2) = Field(
        ..., title="Name"
    )
    memory_gib: int = Field(..., title="Memory Gib")
    cpu_cores: int = Field(..., title="Cpu Cores")
    disk_gib: int = Field(..., title="Disk Gib")
    allow_upgrade_to: List[constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)] = (
        Field(..., title="Allow Upgrade To")
    )
    allow_downgrade_to: List[constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)] = (
        Field(..., title="Allow Downgrade To")
    )
    price: confloat(ge=0.0) = Field(..., title="Price")
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2) = Field(
        ..., title="Period"
    )
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3) = Field(
        ..., title="Currency"
    )


class NodeRabbitMQGroupProperties(CoreApiModel):
    is_master: bool = Field(..., title="Is Master")


class NodeRedisGroupProperties(CoreApiModel):
    is_master: bool = Field(..., title="Is Master")


class ObjectModelNameEnum(StrEnum):
    BORG_ARCHIVE = "BorgArchive"
    BORG_REPOSITORY = "BorgRepository"
    SERVICE_ACCOUNT_TO_CLUSTER = "ServiceAccountToCluster"
    SITE = "Site"
    SERVICE_ACCOUNT_TO_CUSTOMER = "ServiceAccountToCustomer"
    CLUSTER = "Cluster"
    CUSTOMER = "Customer"
    CMS = "CMS"
    FPM_POOL = "FPMPool"
    VIRTUAL_HOST = "VirtualHost"
    PASSENGER_APP = "PassengerApp"
    DATABASE = "Database"
    CERTIFICATE_MANAGER = "CertificateManager"
    BASIC_AUTHENTICATION_REALM = "BasicAuthenticationRealm"
    CRON = "Cron"
    DAEMON = "Daemon"
    MARIADB_ENCRYPTION_KEY = "MariaDBEncryptionKey"
    FIREWALL_RULE = "FirewallRule"
    HOSTS_ENTRY = "HostsEntry"
    NODE_ADD_ON = "NodeAddOn"
    IP_ADDRESS = "IPAddress"
    SECURITY_TXT_POLICY = "SecurityTXTPolicy"
    DATABASE_USER = "DatabaseUser"
    DATABASE_USER_GRANT = "DatabaseUserGrant"
    HTPASSWD_FILE = "HtpasswdFile"
    HTPASSWD_USER = "HtpasswdUser"
    MAIL_ACCOUNT = "MailAccount"
    MAIL_ALIAS = "MailAlias"
    MAIL_DOMAIN = "MailDomain"
    NODE = "Node"
    REDIS_INSTANCE = "RedisInstance"
    DOMAIN_ROUTER = "DomainRouter"
    MAIL_HOSTNAME = "MailHostname"
    CERTIFICATE = "Certificate"
    ROOT_SSH_KEY = "RootSSHKey"
    SSH_KEY = "SSHKey"
    UNIX_USER = "UNIXUser"
    UNIX_USER_RABBITMQ_CREDENTIALS = "UNIXUserRabbitMQCredentials"
    HAPROXY_LISTEN = "HAProxyListen"
    HAPROXY_LISTEN_TO_NODE = "HAProxyListenToNode"
    URL_REDIRECT = "URLRedirect"
    SITE_TO_CUSTOMER = "SiteToCustomer"
    SERVICE_ACCOUNT = "ServiceAccount"
    SERVICE_ACCOUNT_SERVER = "ServiceAccountServer"
    CUSTOM_CONFIG = "CustomConfig"


class PHPExtensionEnum(StrEnum):
    REDIS = "redis"
    IMAGICK = "imagick"
    SQLITE3 = "sqlite3"
    INTL = "intl"
    BCMATH = "bcmath"
    XDEBUG = "xdebug"
    PGSQL = "pgsql"
    SSH2 = "ssh2"
    LDAP = "ldap"
    MCRYPT = "mcrypt"
    XMLRPC = "xmlrpc"
    APCU = "apcu"
    TIDEWAYS = "tideways"
    SQLSRV = "sqlsrv"
    GMP = "gmp"
    VIPS = "vips"
    EXCIMER = "excimer"
    MAILPARSE = "mailparse"
    UV = "uv"
    AMQP = "amqp"
    MONGODB = "mongodb"


class PHPSettings(CoreApiModel):
    apc_enable_cli: bool = Field(False, title="Apc Enable Cli")
    opcache_file_cache: bool = Field(False, title="Opcache File Cache")
    opcache_validate_timestamps: bool = Field(True, title="Opcache Validate Timestamps")
    short_open_tag: bool = Field(False, title="Short Open Tag")
    error_reporting: constr(regex=r"^[A-Z&~_ ]+$", min_length=1, max_length=255) = (
        Field("E_ALL & ~E_DEPRECATED & ~E_STRICT", title="Error Reporting")
    )
    opcache_memory_consumption: conint(ge=192, le=1024) = Field(
        192, title="Opcache Memory Consumption"
    )
    max_execution_time: conint(ge=30, le=120) = Field(120, title="Max Execution Time")
    max_file_uploads: conint(ge=100, le=1000) = Field(100, title="Max File Uploads")
    memory_limit: conint(ge=256, le=4096) = Field(256, title="Memory Limit")
    post_max_size: conint(ge=32, le=256) = Field(32, title="Post Max Size")
    upload_max_filesize: conint(ge=32, le=256) = Field(32, title="Upload Max Filesize")
    tideways_api_key: Optional[
        constr(regex=r"^[a-zA-Z0-9_]+$", min_length=16, max_length=32)
    ] = Field(None, title="Tideways Api Key")
    tideways_sample_rate: Optional[conint(ge=1, le=100)] = Field(
        None, title="Tideways Sample Rate"
    )
    newrelic_browser_monitoring_auto_instrument: bool = Field(
        True, title="Newrelic Browser Monitoring Auto Instrument"
    )


class PassengerAppTypeEnum(StrEnum):
    NODEJS = "NodeJS"


class PassengerEnvironmentEnum(StrEnum):
    PRODUCTION = "Production"
    DEVELOPMENT = "Development"


class RedisEvictionPolicyEnum(StrEnum):
    VOLATILE_TTL = "volatile-ttl"
    VOLATILE_RANDOM = "volatile-random"
    ALLKEYS_RANDOM = "allkeys-random"
    VOLATILE_LFU = "volatile-lfu"
    VOLATILE_LRU = "volatile-lru"
    ALLKEYS_LFU = "allkeys-lfu"
    ALLKEYS_LRU = "allkeys-lru"
    NOEVICTION = "noeviction"


class RedisInstanceCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )
    memory_limit: conint(ge=8) = Field(..., description="In MB.", title="Memory Limit")
    max_databases: int = Field(..., title="Max Databases")
    eviction_policy: RedisEvictionPolicyEnum = Field(
        ...,
        description="See [Redis documentation](https://redis.io/docs/reference/eviction/#eviction-policies).\n\nIf you don't know what to set, set to `volatile-lru`.",
    )


class RedisInstanceUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    port: int = Field(..., title="Port")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )
    memory_limit: conint(ge=8) = Field(..., description="In MB.", title="Memory Limit")
    max_databases: int = Field(..., title="Max Databases")
    eviction_policy: RedisEvictionPolicyEnum = Field(
        ...,
        description="See [Redis documentation](https://redis.io/docs/reference/eviction/#eviction-policies).\n\nIf you don't know what to set, set to `volatile-lru`.",
    )


class RedisInstanceUpdateRequest(CoreApiModel):
    password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(None, title="Password")
    memory_limit: Optional[conint(ge=8)] = Field(
        None, description="In MB.", title="Memory Limit"
    )
    max_databases: Optional[int] = Field(None, title="Max Databases")
    eviction_policy: Optional[RedisEvictionPolicyEnum] = Field(
        None,
        description="See [Redis documentation](https://redis.io/docs/reference/eviction/#eviction-policies).\n\nIf you don't know what to set, set to `volatile-lru`.",
    )


class RootSSHKeyCreatePrivateRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    private_key: str = Field(
        ..., description="Must end with line feed.", title="Private Key"
    )


class RootSSHKeyCreatePublicRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    public_key: str = Field(
        ..., description="Must end with line feed.", title="Public Key"
    )


class SSHKeyCreatePrivateRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    private_key: str = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nMust end with line feed.",
        title="Private Key",
    )


class SSHKeyCreatePublicRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    public_key: str = Field(
        ..., description="Must end with line feed.", title="Public Key"
    )


class SecurityTXTPolicyCreateRequest(CoreApiModel):
    cluster_id: int = Field(..., title="Cluster Id")
    expires_timestamp: datetime = Field(..., title="Expires Timestamp")
    email_contacts: List[EmailStr] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Email Contacts",
        unique_items=True,
    )
    url_contacts: List[AnyUrl] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Url Contacts",
        unique_items=True,
    )
    encryption_key_urls: List[AnyUrl] = Field(
        ..., title="Encryption Key Urls", unique_items=True
    )
    acknowledgment_urls: List[AnyUrl] = Field(
        ..., title="Acknowledgment Urls", unique_items=True
    )
    policy_urls: List[AnyUrl] = Field(..., title="Policy Urls", unique_items=True)
    opening_urls: List[AnyUrl] = Field(..., title="Opening Urls", unique_items=True)
    preferred_languages: List[LanguageCodeEnum] = Field(
        ..., title="Preferred Languages", unique_items=True
    )


class SecurityTXTPolicyUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    expires_timestamp: datetime = Field(..., title="Expires Timestamp")
    email_contacts: List[EmailStr] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Email Contacts",
        unique_items=True,
    )
    url_contacts: List[AnyUrl] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Url Contacts",
        unique_items=True,
    )
    encryption_key_urls: List[AnyUrl] = Field(
        ..., title="Encryption Key Urls", unique_items=True
    )
    acknowledgment_urls: List[AnyUrl] = Field(
        ..., title="Acknowledgment Urls", unique_items=True
    )
    policy_urls: List[AnyUrl] = Field(..., title="Policy Urls", unique_items=True)
    opening_urls: List[AnyUrl] = Field(..., title="Opening Urls", unique_items=True)
    preferred_languages: List[LanguageCodeEnum] = Field(
        ..., title="Preferred Languages", unique_items=True
    )


class SecurityTXTPolicyUpdateRequest(CoreApiModel):
    expires_timestamp: Optional[datetime] = Field(None, title="Expires Timestamp")
    email_contacts: Optional[List[EmailStr]] = Field(
        None,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Email Contacts",
    )
    url_contacts: Optional[List[AnyUrl]] = Field(
        None,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Url Contacts",
    )
    encryption_key_urls: Optional[List[AnyUrl]] = Field(
        None, title="Encryption Key Urls"
    )
    acknowledgment_urls: Optional[List[AnyUrl]] = Field(
        None, title="Acknowledgment Urls"
    )
    policy_urls: Optional[List[AnyUrl]] = Field(None, title="Policy Urls")
    opening_urls: Optional[List[AnyUrl]] = Field(None, title="Opening Urls")
    preferred_languages: Optional[List[LanguageCodeEnum]] = Field(
        None, title="Preferred Languages"
    )


class ServiceAccountGroupEnum(StrEnum):
    SECURITY_TXT_POLICY_SERVER = "Security TXT Policy Server"
    LOAD_BALANCER = "Load Balancer"
    MAIL_PROXY = "Mail Proxy"
    MAIL_GATEWAY = "Mail Gateway"
    INTERNET_ROUTER = "Internet Router"
    STORAGE_ROUTER = "Storage Router"
    PHPMYADMIN = "phpMyAdmin"


class ShellPathEnum(StrEnum):
    BASH = "/bin/bash"
    JAILSHELL = "/usr/local/bin/jailshell"
    NOLOGIN = "/usr/sbin/nologin"


class SiteIncludes(CoreApiModel):
    pass


class SiteResource(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[A-Z0-9-]+$", min_length=1, max_length=32) = Field(
        ..., title="Name"
    )
    includes: SiteIncludes


class StatusCodeEnum(IntEnum):
    INTEGER_301 = 301
    INTEGER_302 = 302
    INTEGER_303 = 303
    INTEGER_307 = 307
    INTEGER_308 = 308


class TaskCollectionCallback(CoreApiModel):
    task_collection_uuid: UUID4 = Field(..., title="Task Collection Uuid")
    success: bool = Field(..., title="Success")


class TaskCollectionTypeEnum(StrEnum):
    ASYNCHRONOUS = "asynchronous"


class TaskStateEnum(StrEnum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class TemporaryFTPUserCreateRequest(CoreApiModel):
    unix_user_id: int = Field(..., title="Unix User Id")
    node_id: int = Field(..., description="Must have ProFTPD group.", title="Node Id")


class TemporaryFTPUserResource(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )
    file_manager_url: AnyUrl = Field(..., title="File Manager Url")


class TimeUnitEnum(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TokenTypeEnum(StrEnum):
    BEARER = "bearer"


class UNIXUserComparison(CoreApiModel):
    not_identical_paths: NestedPathsDict
    only_left_files_paths: NestedPathsDict
    only_right_files_paths: NestedPathsDict
    only_left_directories_paths: NestedPathsDict
    only_right_directories_paths: NestedPathsDict


class UNIXUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    virtual_hosts_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Web group. May not be set otherwise.\n\nThe virtual hosts directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `virtual-hosts`.",
        title="Virtual Hosts Directory",
    )
    mail_domains_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Mail group. May not be set otherwise.\n\nThe mail domains directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `mail-domains`.",
        title="Mail Domains Directory",
    )
    borg_repositories_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Borg Server group. May not be set otherwise.\n\nThe Borg repositories directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `borg-repositories`.",
        title="Borg Repositories Directory",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = (
        Field(
            ...,
            description="If set to null, only SSH key authentication is allowed.",
            title="Password",
        )
    )
    shell_path: ShellPathEnum = Field(
        ...,
        description="When set to `/usr/local/bin/jailshell`, Bubblewrap Toolkit must be enabled on the cluster (`bubblewrap_toolkit_enabled`).\n\nWhen set to `/usr/local/bin/jailshell`, multiple security measures are applied, most notably the inability to see other UNIX user's processes. Recommended for shared environments in which users are not trusted.",
    )
    record_usage_files: bool = Field(
        ...,
        description="May only be set to `true` when cluster has Web group.\n\nWhen enabled, UNIX user usages objects contain a list of largest files (`files`).",
        title="Record Usage Files",
    )
    default_php_version: Optional[str] = Field(
        ...,
        description="When set, the `php` command is aliased to the specified PHP version. Otherwise, the system default is used.\n\nMust be installed on cluster (`php_versions`).",
        title="Default Php Version",
    )
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        ...,
        description="When set, the following commands are activated to the specified NodeJS version: `corepack`, `npm`, `npx`, `node`. Otherwise, these commands are not available.\n\nMust be installed on cluster (`nodejs_versions`).\n\nRequires shell path (`shell_path`) to be set to `/usr/local/bin/jailshell`.",
        title="Default Nodejs Version",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")


class UNIXUserHomeDirectoryEnum(StrEnum):
    VAR_WWW_VHOSTS = "/var/www/vhosts"
    VAR_WWW = "/var/www"
    HOME = "/home"
    MNT_MAIL = "/mnt/mail"
    MNT_BACKUPS = "/mnt/backups"


class UNIXUserUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    unix_id: int = Field(..., title="Unix Id")
    home_directory: str = Field(
        ...,
        description="Cluster UNIX users home directory (`unix_users_home_directory`) + UNIX user username (`username`).",
        title="Home Directory",
    )
    ssh_directory: str = Field(..., title="Ssh Directory")
    virtual_hosts_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Web group. May not be set otherwise.\n\nThe virtual hosts directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `virtual-hosts`.",
        title="Virtual Hosts Directory",
    )
    mail_domains_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Mail group. May not be set otherwise.\n\nThe mail domains directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `mail-domains`.",
        title="Mail Domains Directory",
    )
    borg_repositories_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Borg Server group. May not be set otherwise.\n\nThe Borg repositories directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `borg-repositories`.",
        title="Borg Repositories Directory",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    shell_path: ShellPathEnum = Field(
        ...,
        description="When set to `/usr/local/bin/jailshell`, Bubblewrap Toolkit must be enabled on the cluster (`bubblewrap_toolkit_enabled`).\n\nWhen set to `/usr/local/bin/jailshell`, multiple security measures are applied, most notably the inability to see other UNIX user's processes. Recommended for shared environments in which users are not trusted.",
    )
    record_usage_files: bool = Field(
        ...,
        description="May only be set to `true` when cluster has Web group.\n\nWhen enabled, UNIX user usages objects contain a list of largest files (`files`).",
        title="Record Usage Files",
    )
    default_php_version: Optional[str] = Field(
        ...,
        description="When set, the `php` command is aliased to the specified PHP version. Otherwise, the system default is used.\n\nMust be installed on cluster (`php_versions`).",
        title="Default Php Version",
    )
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        ...,
        description="When set, the following commands are activated to the specified NodeJS version: `corepack`, `npm`, `npx`, `node`. Otherwise, these commands are not available.\n\nMust be installed on cluster (`nodejs_versions`).\n\nRequires shell path (`shell_path`) to be set to `/usr/local/bin/jailshell`.",
        title="Default Nodejs Version",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)] = Field(
        ...,
        description="If set to null, only SSH key authentication is allowed.",
        title="Password",
    )


class UNIXUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = (
        Field(
            None,
            description="If set to null, only SSH key authentication is allowed.",
            title="Password",
        )
    )
    shell_path: Optional[ShellPathEnum] = Field(
        None,
        description="When set to `/usr/local/bin/jailshell`, Bubblewrap Toolkit must be enabled on the cluster (`bubblewrap_toolkit_enabled`).\n\nWhen set to `/usr/local/bin/jailshell`, multiple security measures are applied, most notably the inability to see other UNIX user's processes. Recommended for shared environments in which users are not trusted.",
    )
    record_usage_files: Optional[bool] = Field(
        None,
        description="May only be set to `true` when cluster has Web group.\n\nWhen enabled, UNIX user usages objects contain a list of largest files (`files`).",
        title="Record Usage Files",
    )
    default_php_version: Optional[str] = Field(
        None,
        description="When set, the `php` command is aliased to the specified PHP version. Otherwise, the system default is used.\n\nMust be installed on cluster (`php_versions`).",
        title="Default Php Version",
    )
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        None,
        description="When set, the following commands are activated to the specified NodeJS version: `corepack`, `npm`, `npx`, `node`. Otherwise, these commands are not available.\n\nMust be installed on cluster (`nodejs_versions`).\n\nRequires shell path (`shell_path`) to be set to `/usr/local/bin/jailshell`.",
        title="Default Nodejs Version",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(None, title="Description")


class UNIXUserUsageFile(CoreApiModel):
    path: str = Field(..., title="Path")
    size: confloat(ge=0.0) = Field(..., title="Size")


class UNIXUserUsageIncludes(CoreApiModel):
    pass


class UNIXUserUsageResource(CoreApiModel):
    unix_user_id: int = Field(..., title="Unix User Id")
    usage: confloat(ge=0.0) = Field(..., title="Usage")
    files: Optional[List[UNIXUserUsageFile]] = Field(
        ...,
        description="List of largest files.\n\nRequires `record_usage_files` to be set to `true` on UNIX user.",
        title="Files",
    )
    timestamp: datetime = Field(..., title="Timestamp")
    includes: UNIXUserUsageIncludes


class UNIXUsersHomeDirectoryUsageIncludes(CoreApiModel):
    pass


class UNIXUsersHomeDirectoryUsageResource(CoreApiModel):
    cluster_id: int = Field(..., title="Cluster Id")
    usage: confloat(ge=0.0) = Field(..., title="Usage")
    timestamp: datetime = Field(..., title="Timestamp")
    includes: UNIXUsersHomeDirectoryUsageIncludes


class URLRedirectCreateRequest(CoreApiModel):
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    destination_url: AnyUrl = Field(..., title="Destination Url")
    status_code: StatusCodeEnum
    keep_query_parameters: bool = Field(
        ...,
        description="Append query parameters from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io?a=b` to `https://www.dropflix.io?a=b`.",
        title="Keep Query Parameters",
    )
    keep_path: bool = Field(
        ...,
        description="Append path from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io/a` to `https://www.dropflix.io/a`.",
        title="Keep Path",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")


class URLRedirectUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    destination_url: AnyUrl = Field(..., title="Destination Url")
    status_code: StatusCodeEnum
    keep_query_parameters: bool = Field(
        ...,
        description="Append query parameters from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io?a=b` to `https://www.dropflix.io?a=b`.",
        title="Keep Query Parameters",
    )
    keep_path: bool = Field(
        ...,
        description="Append path from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io/a` to `https://www.dropflix.io/a`.",
        title="Keep Path",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")


class URLRedirectUpdateRequest(CoreApiModel):
    server_aliases: Optional[List[str]] = Field(
        None,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
    )
    destination_url: Optional[AnyUrl] = Field(None, title="Destination Url")
    status_code: Optional[StatusCodeEnum] = None
    keep_query_parameters: Optional[bool] = Field(
        None,
        description="Append query parameters from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io?a=b` to `https://www.dropflix.io?a=b`.",
        title="Keep Query Parameters",
    )
    keep_path: Optional[bool] = Field(
        None,
        description="Append path from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io/a` to `https://www.dropflix.io/a`.",
        title="Keep Path",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(None, title="Description")


class ValidationError(CoreApiModel):
    loc: List[Union[str, int]] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class VirtualHostDocumentRoot(CoreApiModel):
    contains_files: Dict[str, bool] = Field(..., title="Contains Files")


class VirtualHostServerSoftwareNameEnum(StrEnum):
    APACHE = "Apache"
    NGINX = "nginx"


class VirtualHostUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    unix_user_id: int = Field(..., title="Unix User Id")
    server_software_name: VirtualHostServerSoftwareNameEnum
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]] = Field(
        ..., title="Allow Override Directives"
    )
    allow_override_option_directives: Optional[
        List[AllowOverrideOptionDirectiveEnum]
    ] = Field(..., title="Allow Override Option Directives")
    domain_root: str = Field(..., title="Domain Root")
    cluster_id: int = Field(..., title="Cluster Id")
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    public_root: str = Field(
        ...,
        description="This directory is created automatically. It is also periodically scanned for CMSes which will be added to the API.\n\nThis is what you should set to a custom value for systems such as Laravel. Often to a subdirectory such as `public`.\n\nDo not confuse with document root (`document_root`), which is the directory that files will be loaded from when receiving an HTTP request.\n\nMust be inside UNIX user virtual hosts directory + specified domain (e.g. `/home/dropflix/dropflix.io/htdocs`).",
        title="Public Root",
    )
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    document_root: str = Field(
        ...,
        description="When receiving an HTTP request, files will be loaded from this directory.",
        title="Document Root",
    )
    fpm_pool_id: Optional[int] = Field(
        ...,
        description="Let the specified FPM pool handle requests to PHP files.\n\nMay not be set when Passenger app (`passenger_app_id`) is set.",
        title="Fpm Pool Id",
    )
    passenger_app_id: Optional[int] = Field(
        ...,
        description="Let the specified Passenger app handle requests.\n\nMay only be set when server software is set to nginx (`server_software_name`).\n\nMay not be set when FPM pool (`fpm_pool_id`) is set.",
        title="Passenger App Id",
    )
    custom_config: Optional[
        constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    ] = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.\n\nDefault custom config snippets (`is_default`) are inserted after the virtual host specific custom config. To place a default custom config snippet earlier, include it manually in the virtual host specific custom config.\n\nWhen the server software nginx is used, custom configs are added to the `server` context.\n\nIf the virtual host has basic authentication realms, the `auth_basic` and `auth_basic_user_file` directives may not be set in the default context.\n",
        title="Custom Config",
    )


class VirtualHostUpdateRequest(CoreApiModel):
    server_aliases: Optional[List[str]] = Field(
        None,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
    )
    document_root: Optional[str] = Field(
        None,
        description="When receiving an HTTP request, files will be loaded from this directory.",
        title="Document Root",
    )
    fpm_pool_id: Optional[int] = Field(
        None,
        description="Let the specified FPM pool handle requests to PHP files.\n\nMay not be set when Passenger app (`passenger_app_id`) is set.",
        title="Fpm Pool Id",
    )
    passenger_app_id: Optional[int] = Field(
        None,
        description="Let the specified Passenger app handle requests.\n\nMay only be set when server software is set to nginx (`server_software_name`).\n\nMay not be set when FPM pool (`fpm_pool_id`) is set.",
        title="Passenger App Id",
    )
    custom_config: Optional[
        constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    ] = Field(
        None,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.\n\nDefault custom config snippets (`is_default`) are inserted after the virtual host specific custom config. To place a default custom config snippet earlier, include it manually in the virtual host specific custom config.\n\nWhen the server software nginx is used, custom configs are added to the `server` context.\n\nIf the virtual host has basic authentication realms, the `auth_basic` and `auth_basic_user_file` directives may not be set in the default context.\n",
        title="Custom Config",
    )
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]] = Field(
        None, title="Allow Override Directives"
    )
    allow_override_option_directives: Optional[
        List[AllowOverrideOptionDirectiveEnum]
    ] = Field(None, title="Allow Override Option Directives")
    server_software_name: Optional[VirtualHostServerSoftwareNameEnum] = None


class BorgArchiveContent(CoreApiModel):
    object_type: BorgArchiveContentObjectTypeEnum
    symbolic_mode: constr(regex=r"^[rwx\+\-dlsStT]+$", min_length=10, max_length=10) = (
        Field(..., title="Symbolic Mode")
    )
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    group_name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Group Name"
    )
    path: str = Field(..., title="Path")
    link_target: Optional[str] = Field(..., title="Link Target")
    modification_time: datetime = Field(..., title="Modification Time")
    size: Optional[conint(ge=0)] = Field(..., title="Size")


class CMSCreateRequest(CoreApiModel):
    software_name: CMSSoftwareNameEnum
    is_manually_created: bool = Field(
        ...,
        description="Value is `false` when CMS was detected automatically. Must be set to `true` in other cases.",
        title="Is Manually Created",
    )
    virtual_host_id: int = Field(..., title="Virtual Host Id")


class CMSOption(CoreApiModel):
    value: conint(ge=0, le=1) = Field(..., title="Value")
    name: CMSOptionNameEnum


class CertificateManagerCreateRequest(CoreApiModel):
    common_names: List[str] = Field(
        ...,
        description="May not contain wildcard domains.\n\nEach common name is unique across all certificate managers.",
        min_items=1,
        title="Common Names",
        unique_items=True,
    )
    provider_name: CertificateProviderNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    request_callback_url: Optional[AnyUrl] = Field(..., title="Request Callback Url")


class CertificateManagerUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    main_common_name: str = Field(..., title="Main Common Name")
    certificate_id: Optional[int] = Field(..., title="Certificate Id")
    last_request_task_collection_uuid: Optional[UUID4] = Field(
        ..., title="Last Request Task Collection Uuid"
    )
    common_names: List[str] = Field(
        ...,
        description="May not contain wildcard domains.\n\nEach common name is unique across all certificate managers.",
        min_items=1,
        title="Common Names",
        unique_items=True,
    )
    provider_name: CertificateProviderNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    request_callback_url: Optional[AnyUrl] = Field(..., title="Request Callback Url")


class ClusterCreateRequest(CoreApiModel):
    customer_id: int = Field(
        ...,
        description="Specify your customer ID.\n\nIt can be found on your API user. Retrieve it with `POST /api/v1/login/test-token`.",
        title="Customer Id",
    )
    site_id: int = Field(
        ...,
        description="Locations to create cluster in.\n\nGet available sites with `GET /sites`.",
        title="Site Id",
    )
    groups: List[ClusterGroupEnum] = Field(
        ...,
        description="The following cluster groups are not compatible with each other: Web, Mail, Borg Server and Borg Server, Borg Client. Groups may not be removed once present.",
        title="Groups",
        unique_items=True,
    )
    unix_users_home_directory: Optional[UNIXUserHomeDirectoryEnum] = Field(
        ...,
        description="Must be set when cluster has Web, Mail or Borg Server groups. May not be set otherwise.\n\nThe directory in which UNIX users' home directories will be stored. For example, if this is set to `/home`, a UNIX user with username `dropflix`'s home directory will be `/home/dropflix`.",
    )
    php_versions: List[str] = Field(
        ...,
        description="May only be non-empty when cluster has Web group.\n\nWhen removing a PHP version, it may no longer be in use as version for FPM pools, and default PHP version for UNIX users.",
        title="Php Versions",
        unique_items=True,
    )
    load_balancing_method: Optional[LoadBalancingMethodEnum] = Field(
        None,
        description="Must be set when cluster has Web group. May not be set otherwise.\n\nWhen set to 'Round Robin', requests are routed to the least busy node. This is the most efficient load balancing method, but can cause issues with deadlocks on databases.\n\nWhen set to 'Source IP Address', the initial request by a specific IP address is routed to the least busy node. All follow-up requests are sent to that node. This causes load to be distributed less efficiently than with the 'Round Robin' method, but cannot cause issues with deadlocks on databases.\n\nIf a cluster has only one node with a group for which load is balanced (such as Apache or nginx), this option has no effect.",
    )
    mariadb_version: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Mariadb Version",
    )
    nodejs_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nSpecify only the major version.",
        title="Nodejs Version",
    )
    postgresql_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Postgresql Version",
    )
    mariadb_cluster_name: Optional[
        constr(regex=r"^[a-z.]+$", min_length=1, max_length=64)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly used internally.",
        title="Mariadb Cluster Name",
    )
    custom_php_modules_names: List[PHPExtensionEnum] = Field(
        ...,
        description="\nCustom PHP modules may not be removed once present.\n\nWhen adding `vips`, note that FFI will be enabled globally. This has security implications, generally not deemed as dangerous. For more information, see the following comments by the PHP module's author: https://github.com/libvips/php-vips/commit/3c178b30521736136e0368d2858848bf4e6e5f01\n",
        title="Custom Php Modules Names",
        unique_items=True,
    )
    php_settings: PHPSettings
    php_ioncube_enabled: bool = Field(
        ...,
        description="Requires at least one PHP version (`php_versions`).\n\nCannot be disabled once enabled.",
        title="Php Ioncube Enabled",
    )
    kernelcare_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16)
    ] = Field(
        ...,
        description="When unsetting, no nodes may have the group KernelCare.",
        title="Kernelcare License Key",
    )
    redis_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group has one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This password applies to the main Redis instance. The password of additional instances is determined by the appropriate Redis Instance model in the Core API.",
        title="Redis Password",
    )
    redis_memory_limit: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group have one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This memory limit applies to the main Redis instance. The memory limit of additional instances is determined by the appropriate Redis Instance model in the Core API.\n\nIn MB.",
        title="Redis Memory Limit",
    )
    php_sessions_spread_enabled: bool = Field(
        ...,
        description="Cannot be disabled once enabled.",
        title="Php Sessions Spread Enabled",
    )
    nodejs_versions: List[str] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nWhen removing a NodeJS version, it may no longer be in use as version for Passenger apps, and default NodeJS version for UNIX users.\n\nFind all available NodeJS versions on https://nodejs.org/dist/index.tab (first column).",
        title="Nodejs Versions",
        unique_items=True,
    )
    description: constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255) = (
        Field(..., title="Description")
    )
    wordpress_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Wordpress Toolkit Enabled",
    )
    automatic_borg_repositories_prune_enabled: bool = Field(
        ...,
        description="Requires cluster to have Borg Client group.",
        title="Automatic Borg Repositories Prune Enabled",
    )
    sync_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web or Database group.\n\nCannot be disabled once enabled.",
        title="Sync Toolkit Enabled",
    )
    bubblewrap_toolkit_enabled: bool = Field(
        ...,
        description="Bubblewrap allows you to 'jail' UNIX users' SSH sessions. This is recommended for shared environments in which users are not trusted.\n\nRequires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Bubblewrap Toolkit Enabled",
    )
    automatic_upgrades_enabled: bool = Field(
        ...,
        description="Automatically apply certain higher-severity updates.\n\nWe recommend enabling this for shared hosting to reduce the chance of privilege escalation.",
        title="Automatic Upgrades Enabled",
    )
    firewall_rules_external_providers_enabled: bool = Field(
        ...,
        description="Allows for using 'external_provider_name' with firewall rules.\n\nCannot be disabled once enabled.",
        title="Firewall Rules External Providers Enabled",
    )
    database_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Database group.\n\nCannot be disabled once enabled.",
        title="Database Toolkit Enabled",
    )
    mariadb_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Mariadb Backup Interval",
    )
    mariadb_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Mariadb Backup Local Retention",
    )
    postgresql_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Postgresql Backup Local Retention",
    )
    meilisearch_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Meilisearch Backup Local Retention",
    )
    new_relic_mariadb_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by New Relic.\n\nThe MySQL user is created automatically.",
        title="New Relic Mariadb Password",
    )
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nGet license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Apm License Key",
    )
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="Get license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Infrastructure License Key",
    )
    meilisearch_master_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly the master key has access to endpoints for creating and deleting API keys.",
        title="Meilisearch Master Key",
    )
    meilisearch_environment: Optional[MeilisearchEnvironmentEnum] = Field(
        ..., description="May only be set when cluster has Database group."
    )
    meilisearch_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Meilisearch Backup Interval",
    )
    postgresql_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Postgresql Backup Interval",
    )
    http_retry_properties: Optional[HTTPRetryProperties] = Field(
        ...,
        description="Must be set when cluster has Web or Redirect groups. May not be set otherwise.",
    )
    grafana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Grafana Domain",
    )
    singlestore_studio_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Studio Domain",
    )
    singlestore_api_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Api Domain",
    )
    singlestore_license_key: Optional[
        constr(regex=r"^[ -~]+$", min_length=144, max_length=144)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nGet license key from https://portal.singlestore.com.",
        title="Singlestore License Key",
    )
    singlestore_root_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Singlestore Root Password",
    )
    elasticsearch_default_users_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Elasticsearch Default Users Password",
    )
    rabbitmq_erlang_cookie: Optional[
        constr(regex=r"^[A-Z0-9]+$", min_length=20, max_length=20)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Erlang Cookie",
    )
    rabbitmq_admin_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Admin Password",
    )
    metabase_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Metabase Domain",
    )
    metabase_database_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by Metabase.\n\nThe MySQL user is created automatically.",
        title="Metabase Database Password",
    )
    kibana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Kibana Domain",
    )
    rabbitmq_management_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Rabbitmq Management Domain",
    )


class ClusterDeploymentTaskResult(CoreApiModel):
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Description"
    )
    message: Optional[str] = Field(..., title="Message")
    state: TaskStateEnum


class ClusterIPAddressCreateRequest(CoreApiModel):
    service_account_name: str = Field(
        ...,
        description="Must be service account with group 'Load Balancer'.\n\nRetrieve service accounts with `GET /api/v1/clusters/{id}/ip-addresses`.",
        title="Service Account Name",
    )
    dns_name: str = Field(..., description="Reverse DNS.", title="Dns Name")
    address_family: IPAddressFamilyEnum


class ClusterIncludes(CoreApiModel):
    site: SiteResource
    customer: CustomerResource


class ClusterResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    customer_id: int = Field(
        ...,
        description="Specify your customer ID.\n\nIt can be found on your API user. Retrieve it with `POST /api/v1/login/test-token`.",
        title="Customer Id",
    )
    site_id: int = Field(
        ...,
        description="Locations to create cluster in.\n\nGet available sites with `GET /sites`.",
        title="Site Id",
    )
    groups: List[ClusterGroupEnum] = Field(
        ...,
        description="The following cluster groups are not compatible with each other: Web, Mail, Borg Server and Borg Server, Borg Client. Groups may not be removed once present.",
        title="Groups",
        unique_items=True,
    )
    unix_users_home_directory: Optional[UNIXUserHomeDirectoryEnum] = Field(
        ...,
        description="Must be set when cluster has Web, Mail or Borg Server groups. May not be set otherwise.\n\nThe directory in which UNIX users' home directories will be stored. For example, if this is set to `/home`, a UNIX user with username `dropflix`'s home directory will be `/home/dropflix`.",
    )
    php_versions: List[str] = Field(
        ...,
        description="May only be non-empty when cluster has Web group.\n\nWhen removing a PHP version, it may no longer be in use as version for FPM pools, and default PHP version for UNIX users.",
        title="Php Versions",
        unique_items=True,
    )
    load_balancing_method: Optional[LoadBalancingMethodEnum] = Field(
        ...,
        description="Must be set when cluster has Web group. May not be set otherwise.",
    )
    mariadb_version: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Mariadb Version",
    )
    nodejs_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nSpecify only the major version.",
        title="Nodejs Version",
    )
    postgresql_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Postgresql Version",
    )
    mariadb_cluster_name: Optional[
        constr(regex=r"^[a-z.]+$", min_length=1, max_length=64)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly used internally.",
        title="Mariadb Cluster Name",
    )
    custom_php_modules_names: List[PHPExtensionEnum] = Field(
        ...,
        description="\nCustom PHP modules may not be removed once present.\n\nWhen adding `vips`, note that FFI will be enabled globally. This has security implications, generally not deemed as dangerous. For more information, see the following comments by the PHP module's author: https://github.com/libvips/php-vips/commit/3c178b30521736136e0368d2858848bf4e6e5f01\n",
        title="Custom Php Modules Names",
        unique_items=True,
    )
    php_settings: PHPSettings
    php_ioncube_enabled: bool = Field(
        ...,
        description="Requires at least one PHP version (`php_versions`).\n\nCannot be disabled once enabled.",
        title="Php Ioncube Enabled",
    )
    kernelcare_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16)
    ] = Field(
        ...,
        description="When unsetting, no nodes may have the group KernelCare.",
        title="Kernelcare License Key",
    )
    redis_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group has one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This password applies to the main Redis instance. The password of additional instances is determined by the appropriate Redis Instance model in the Core API.",
        title="Redis Password",
    )
    redis_memory_limit: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group have one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This memory limit applies to the main Redis instance. The memory limit of additional instances is determined by the appropriate Redis Instance model in the Core API.\n\nIn MB.",
        title="Redis Memory Limit",
    )
    php_sessions_spread_enabled: bool = Field(
        ...,
        description="Cannot be disabled once enabled.",
        title="Php Sessions Spread Enabled",
    )
    nodejs_versions: List[NodejsVersion] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nWhen removing a NodeJS version, it may no longer be in use as version for Passenger apps, and default NodeJS version for UNIX users.\n\nFind all available NodeJS versions on https://nodejs.org/dist/index.tab (first column).",
        title="Nodejs Versions",
        unique_items=True,
    )
    description: constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255) = (
        Field(..., title="Description")
    )
    wordpress_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Wordpress Toolkit Enabled",
    )
    automatic_borg_repositories_prune_enabled: bool = Field(
        ...,
        description="Requires cluster to have Borg Client group.",
        title="Automatic Borg Repositories Prune Enabled",
    )
    sync_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web or Database group.\n\nCannot be disabled once enabled.",
        title="Sync Toolkit Enabled",
    )
    bubblewrap_toolkit_enabled: bool = Field(
        ...,
        description="Bubblewrap allows you to 'jail' UNIX users' SSH sessions. This is recommended for shared environments in which users are not trusted.\n\nRequires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Bubblewrap Toolkit Enabled",
    )
    automatic_upgrades_enabled: bool = Field(
        ...,
        description="Automatically apply certain higher-severity updates.\n\nWe recommend enabling this for shared hosting to reduce the chance of privilege escalation.",
        title="Automatic Upgrades Enabled",
    )
    firewall_rules_external_providers_enabled: bool = Field(
        ...,
        description="Allows for using 'external_provider_name' with firewall rules.\n\nCannot be disabled once enabled.",
        title="Firewall Rules External Providers Enabled",
    )
    database_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Database group.\n\nCannot be disabled once enabled.",
        title="Database Toolkit Enabled",
    )
    mariadb_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Mariadb Backup Interval",
    )
    mariadb_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available..",
        title="Mariadb Backup Local Retention",
    )
    postgresql_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Postgresql Backup Local Retention",
    )
    meilisearch_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Meilisearch Backup Local Retention",
    )
    new_relic_mariadb_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by New Relic.\n\nThe MySQL user is created automatically.",
        title="New Relic Mariadb Password",
    )
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nGet license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Apm License Key",
    )
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="Get license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Infrastructure License Key",
    )
    meilisearch_master_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly the master key has access to endpoints for creating and deleting API keys.",
        title="Meilisearch Master Key",
    )
    meilisearch_environment: Optional[MeilisearchEnvironmentEnum] = Field(
        ..., description="May only be set when cluster has Database group."
    )
    meilisearch_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Meilisearch Backup Interval",
    )
    postgresql_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Postgresql Backup Interval",
    )
    http_retry_properties: Optional[HTTPRetryProperties] = Field(
        ...,
        description="Must be set when cluster has Web or Redirect groups. May not be set otherwise.",
    )
    grafana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Grafana Domain",
    )
    singlestore_studio_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Studio Domain",
    )
    singlestore_api_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Api Domain",
    )
    singlestore_license_key: Optional[
        constr(regex=r"^[ -~]+$", min_length=144, max_length=6144)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nGet license key from https://portal.singlestore.com.",
        title="Singlestore License Key",
    )
    singlestore_root_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Singlestore Root Password",
    )
    elasticsearch_default_users_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Elasticsearch Default Users Password",
    )
    rabbitmq_erlang_cookie: Optional[
        constr(regex=r"^[A-Z0-9]+$", min_length=20, max_length=20)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Erlang Cookie",
    )
    rabbitmq_admin_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Admin Password",
    )
    metabase_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Metabase Domain",
    )
    metabase_database_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by Metabase.\n\nThe MySQL user is created automatically.",
        title="Metabase Database Password",
    )
    kibana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Kibana Domain",
    )
    rabbitmq_management_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Rabbitmq Management Domain",
    )
    includes: ClusterIncludes


class ClusterUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    customer_id: int = Field(
        ...,
        description="Specify your customer ID.\n\nIt can be found on your API user. Retrieve it with `POST /api/v1/login/test-token`.",
        title="Customer Id",
    )
    site_id: int = Field(
        ...,
        description="Locations to create cluster in.\n\nGet available sites with `GET /sites`.",
        title="Site Id",
    )
    groups: List[ClusterGroupEnum] = Field(
        ...,
        description="The following cluster groups are not compatible with each other: Web, Mail, Borg Server and Borg Server, Borg Client. Groups may not be removed once present.",
        title="Groups",
        unique_items=True,
    )
    unix_users_home_directory: Optional[UNIXUserHomeDirectoryEnum] = Field(
        ...,
        description="Must be set when cluster has Web, Mail or Borg Server groups. May not be set otherwise.\n\nThe directory in which UNIX users' home directories will be stored. For example, if this is set to `/home`, a UNIX user with username `dropflix`'s home directory will be `/home/dropflix`.",
    )
    php_versions: List[str] = Field(
        ...,
        description="May only be non-empty when cluster has Web group.\n\nWhen removing a PHP version, it may no longer be in use as version for FPM pools, and default PHP version for UNIX users.",
        title="Php Versions",
        unique_items=True,
    )
    mariadb_version: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Mariadb Version",
    )
    nodejs_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nSpecify only the major version.",
        title="Nodejs Version",
    )
    postgresql_version: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Postgresql Version",
    )
    mariadb_cluster_name: Optional[
        constr(regex=r"^[a-z.]+$", min_length=1, max_length=64)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly used internally.",
        title="Mariadb Cluster Name",
    )
    custom_php_modules_names: List[PHPExtensionEnum] = Field(
        ...,
        description="\nCustom PHP modules may not be removed once present.\n\nWhen adding `vips`, note that FFI will be enabled globally. This has security implications, generally not deemed as dangerous. For more information, see the following comments by the PHP module's author: https://github.com/libvips/php-vips/commit/3c178b30521736136e0368d2858848bf4e6e5f01\n",
        title="Custom Php Modules Names",
        unique_items=True,
    )
    php_settings: PHPSettings
    php_ioncube_enabled: bool = Field(
        ...,
        description="Requires at least one PHP version (`php_versions`).\n\nCannot be disabled once enabled.",
        title="Php Ioncube Enabled",
    )
    kernelcare_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16)
    ] = Field(
        ...,
        description="When unsetting, no nodes may have the group KernelCare.",
        title="Kernelcare License Key",
    )
    redis_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group has one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This password applies to the main Redis instance. The password of additional instances is determined by the appropriate Redis Instance model in the Core API.",
        title="Redis Password",
    )
    redis_memory_limit: Optional[int] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group have one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This memory limit applies to the main Redis instance. The memory limit of additional instances is determined by the appropriate Redis Instance model in the Core API.\n\nIn MB.",
        title="Redis Memory Limit",
    )
    php_sessions_spread_enabled: bool = Field(
        ...,
        description="Cannot be disabled once enabled.",
        title="Php Sessions Spread Enabled",
    )
    nodejs_versions: List[str] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nWhen removing a NodeJS version, it may no longer be in use as version for Passenger apps, and default NodeJS version for UNIX users.\n\nFind all available NodeJS versions on https://nodejs.org/dist/index.tab (first column).",
        title="Nodejs Versions",
        unique_items=True,
    )
    description: constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255) = (
        Field(..., title="Description")
    )
    wordpress_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Wordpress Toolkit Enabled",
    )
    automatic_borg_repositories_prune_enabled: bool = Field(
        ...,
        description="Requires cluster to have Borg Client group.",
        title="Automatic Borg Repositories Prune Enabled",
    )
    sync_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Web or Database group.\n\nCannot be disabled once enabled.",
        title="Sync Toolkit Enabled",
    )
    bubblewrap_toolkit_enabled: bool = Field(
        ...,
        description="Bubblewrap allows you to 'jail' UNIX users' SSH sessions. This is recommended for shared environments in which users are not trusted.\n\nRequires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Bubblewrap Toolkit Enabled",
    )
    automatic_upgrades_enabled: bool = Field(
        ...,
        description="Automatically apply certain higher-severity updates.\n\nWe recommend enabling this for shared hosting to reduce the chance of privilege escalation.",
        title="Automatic Upgrades Enabled",
    )
    firewall_rules_external_providers_enabled: bool = Field(
        ...,
        description="Allows for using 'external_provider_name' with firewall rules.\n\nCannot be disabled once enabled.",
        title="Firewall Rules External Providers Enabled",
    )
    database_toolkit_enabled: bool = Field(
        ...,
        description="Requires cluster to have Database group.\n\nCannot be disabled once enabled.",
        title="Database Toolkit Enabled",
    )
    mariadb_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Mariadb Backup Interval",
    )
    mariadb_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Mariadb Backup Local Retention",
    )
    postgresql_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Postgresql Backup Local Retention",
    )
    meilisearch_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available..",
        title="Meilisearch Backup Local Retention",
    )
    new_relic_mariadb_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by New Relic.\n\nThe MySQL user is created automatically.",
        title="New Relic Mariadb Password",
    )
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="May only be set when cluster has Web group.\n\nGet license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Apm License Key",
    )
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        ...,
        description="Get license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Infrastructure License Key",
    )
    meilisearch_master_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nOnly the master key has access to endpoints for creating and deleting API keys.",
        title="Meilisearch Master Key",
    )
    meilisearch_environment: Optional[MeilisearchEnvironmentEnum] = Field(
        ..., description="May only be set when cluster has Database group."
    )
    meilisearch_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Meilisearch Backup Interval",
    )
    postgresql_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Postgresql Backup Interval",
    )
    http_retry_properties: Optional[HTTPRetryProperties] = Field(
        ...,
        description="Must be set when cluster has Web or Redirect groups. May not be set otherwise.",
    )
    grafana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Grafana Domain",
    )
    singlestore_studio_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Studio Domain",
    )
    singlestore_api_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Api Domain",
    )
    singlestore_license_key: Optional[
        constr(regex=r"^[ -~]+$", min_length=144, max_length=6144)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nGet license key from https://portal.singlestore.com.",
        title="Singlestore License Key",
    )
    singlestore_root_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Singlestore Root Password",
    )
    elasticsearch_default_users_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Elasticsearch Default Users Password",
    )
    rabbitmq_erlang_cookie: Optional[
        constr(regex=r"^[A-Z0-9]+$", min_length=20, max_length=20)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Erlang Cookie",
    )
    rabbitmq_admin_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Admin Password",
    )
    metabase_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Metabase Domain",
    )
    metabase_database_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by Metabase.\n\nThe MySQL user is created automatically.",
        title="Metabase Database Password",
    )
    kibana_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Kibana Domain",
    )
    rabbitmq_management_domain: Optional[str] = Field(
        ...,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Rabbitmq Management Domain",
    )


class ClusterUpdateRequest(CoreApiModel):
    groups: Optional[List[ClusterGroupEnum]] = Field(
        None,
        description="The following cluster groups are not compatible with each other: Web, Mail, Borg Server and Borg Server, Borg Client. Groups may not be removed once present.",
        title="Groups",
    )
    unix_users_home_directory: Optional[UNIXUserHomeDirectoryEnum] = Field(
        None,
        description="Must be set when cluster has Web, Mail or Borg Server groups. May not be set otherwise.\n\nThe directory in which UNIX users' home directories will be stored. For example, if this is set to `/home`, a UNIX user with username `dropflix`'s home directory will be `/home/dropflix`.",
    )
    load_balancing_method: Optional[LoadBalancingMethodEnum] = Field(
        None,
        description="Must be set when cluster has Web group. May not be set otherwise.\n\nWhen set to 'Round Robin', requests are routed to the least busy node. This is the most efficient load balancing method, but can cause issues with deadlocks on databases.\n\nWhen set to 'Source IP Address', the initial request by a specific IP address is routed to the least busy node. All follow-up requests are sent to that node. This causes load to be distributed less efficiently than with the 'Round Robin' method, but cannot cause issues with deadlocks on databases.\n\nIf a cluster has only one node with a group for which load is balanced (such as Apache or nginx), this option has no effect.",
    )
    php_versions: Optional[List[str]] = Field(
        None,
        description="May only be non-empty when cluster has Web group.\n\nWhen removing a PHP version, it may no longer be in use as version for FPM pools, and default PHP version for UNIX users.",
        title="Php Versions",
    )
    mariadb_version: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Mariadb Version",
    )
    nodejs_version: Optional[int] = Field(
        None,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nSpecify only the major version.",
        title="Nodejs Version",
    )
    postgresql_version: Optional[int] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Postgresql Version",
    )
    mariadb_cluster_name: Optional[
        constr(regex=r"^[a-z.]+$", min_length=1, max_length=64)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nOnly used internally.",
        title="Mariadb Cluster Name",
    )
    custom_php_modules_names: Optional[List[PHPExtensionEnum]] = Field(
        None,
        description="\nCustom PHP modules may not be removed once present.\n\nWhen adding `vips`, note that FFI will be enabled globally. This has security implications, generally not deemed as dangerous. For more information, see the following comments by the PHP module's author: https://github.com/libvips/php-vips/commit/3c178b30521736136e0368d2858848bf4e6e5f01\n",
        title="Custom Php Modules Names",
    )
    php_settings: Optional[PHPSettings] = None
    php_ioncube_enabled: Optional[bool] = Field(
        None,
        description="Requires at least one PHP version (`php_versions`).\n\nCannot be disabled once enabled.",
        title="Php Ioncube Enabled",
    )
    kernelcare_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16)
    ] = Field(
        None,
        description="When unsetting, no nodes may have the group KernelCare.",
        title="Kernelcare License Key",
    )
    redis_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group has one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This password applies to the main Redis instance. The password of additional instances is determined by the appropriate Redis Instance model in the Core API.",
        title="Redis Password",
    )
    redis_memory_limit: Optional[int] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nEach cluster with node(s) with the Redis group have one main Redis instance, and optional additional instances created with the Core API (Redis Instances model). This memory limit applies to the main Redis instance. The memory limit of additional instances is determined by the appropriate Redis Instance model in the Core API.\n\nIn MB.",
        title="Redis Memory Limit",
    )
    php_sessions_spread_enabled: Optional[bool] = Field(
        None,
        description="Cannot be disabled once enabled.",
        title="Php Sessions Spread Enabled",
    )
    nodejs_versions: Optional[List[str]] = Field(
        None,
        description="May only be set when cluster has Web group.\n\nCluster has `nodejs_version` and `nodejs_versions` attributes. For information on the difference, see 'Differences between NodeJS versions'.\n\nWhen removing a NodeJS version, it may no longer be in use as version for Passenger apps, and default NodeJS version for UNIX users.\n\nFind all available NodeJS versions on https://nodejs.org/dist/index.tab (first column).",
        title="Nodejs Versions",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255)
    ] = Field(None, title="Description")
    wordpress_toolkit_enabled: Optional[bool] = Field(
        None,
        description="Requires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Wordpress Toolkit Enabled",
    )
    automatic_borg_repositories_prune_enabled: Optional[bool] = Field(
        None,
        description="Requires cluster to have Borg Client group.",
        title="Automatic Borg Repositories Prune Enabled",
    )
    sync_toolkit_enabled: Optional[bool] = Field(
        None,
        description="Requires cluster to have Web or Database group.\n\nCannot be disabled once enabled.",
        title="Sync Toolkit Enabled",
    )
    bubblewrap_toolkit_enabled: Optional[bool] = Field(
        None,
        description="Bubblewrap allows you to 'jail' UNIX users' SSH sessions. This is recommended for shared environments in which users are not trusted.\n\nRequires cluster to have Web group.\n\nCannot be disabled once enabled.",
        title="Bubblewrap Toolkit Enabled",
    )
    automatic_upgrades_enabled: Optional[bool] = Field(
        None,
        description="Automatically apply certain higher-severity updates.\n\nWe recommend enabling this for shared hosting to reduce the chance of privilege escalation.",
        title="Automatic Upgrades Enabled",
    )
    firewall_rules_external_providers_enabled: Optional[bool] = Field(
        None,
        description="Allows for using 'external_provider_name' with firewall rules.\n\nCannot be disabled once enabled.",
        title="Firewall Rules External Providers Enabled",
    )
    database_toolkit_enabled: Optional[bool] = Field(
        None,
        description="Requires cluster to have Database group.\n\nCannot be disabled once enabled.",
        title="Database Toolkit Enabled",
    )
    mariadb_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Mariadb Backup Interval",
    )
    mariadb_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available..",
        title="Mariadb Backup Local Retention",
    )
    postgresql_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Postgresql Backup Local Retention",
    )
    meilisearch_backup_local_retention: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe amount of default (non-Borg) backups stored on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nThese backups are backed up every 24 hours; set this value accordingly. For example, when this is set to `3` and backups are created every 4 hours (`mariadb_backup_interval`), the most recent 3 * 4 = 12 hours of backups are stored locally. When the 24-hour backup runs, the least recent 12 hours of backups would have been rotated, and will therefore no longer be available.",
        title="Meilisearch Backup Local Retention",
    )
    new_relic_mariadb_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by New Relic.\n\nThe MySQL user is created automatically.",
        title="New Relic Mariadb Password",
    )
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        None,
        description="May only be set when cluster has Web group.\n\nGet license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Apm License Key",
    )
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = Field(
        None,
        description="Get license key from https://one.eu.newrelic.com/api-keys.",
        title="New Relic Infrastructure License Key",
    )
    meilisearch_master_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nOnly the master key has access to endpoints for creating and deleting API keys.",
        title="Meilisearch Master Key",
    )
    meilisearch_environment: Optional[MeilisearchEnvironmentEnum] = Field(
        None, description="May only be set when cluster has Database group."
    )
    meilisearch_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Meilisearch Backup Interval",
    )
    postgresql_backup_interval: Optional[conint(ge=1, le=24)] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe frequency of default (non-Borg) backups created on the master node. Cyberfusion can quickly restore these if needed.\n\nDoes not pertain to Borg repositories; those have their own retention settings (`keep_hourly`, etc.).\n\nIn hours.\n\nIf the interval causes backups to run once a day (i.e. exceeds 12), backups run at the hour of the interval. For example, if this is set to `24`, backups run at 00:00. If set to `13`, backups run at 13:00, etc.",
        title="Postgresql Backup Interval",
    )
    http_retry_properties: Optional[HTTPRetryProperties] = Field(
        None,
        description="Must be set when cluster has Web or Redirect groups. May not be set otherwise.",
    )
    grafana_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Grafana Domain",
    )
    singlestore_studio_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Studio Domain",
    )
    singlestore_api_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Singlestore Api Domain",
    )
    singlestore_license_key: Optional[
        constr(regex=r"^[ -~]+$", min_length=144, max_length=144)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nGet license key from https://portal.singlestore.com.",
        title="Singlestore License Key",
    )
    singlestore_root_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Singlestore Root Password",
    )
    elasticsearch_default_users_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Elasticsearch Default Users Password",
    )
    rabbitmq_erlang_cookie: Optional[
        constr(regex=r"^[A-Z0-9]+$", min_length=20, max_length=20)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Erlang Cookie",
    )
    rabbitmq_admin_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.",
        title="Rabbitmq Admin Password",
    )
    metabase_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Metabase Domain",
    )
    metabase_database_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nPassword for MySQL user used by Metabase.\n\nThe MySQL user is created automatically.",
        title="Metabase Database Password",
    )
    kibana_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Kibana Domain",
    )
    rabbitmq_management_domain: Optional[str] = Field(
        None,
        description="May only be set when cluster has Database group.\n\nThe values of one or more of the attributes `grafana_domain`, `singlestore_studio_domain`, `singlestore_api_domain`, `metabase_domain`, `kibana_domain`, `rabbitmq_management_domain` must be unique.\n\nA domain router is created for this domain.",
        title="Rabbitmq Management Domain",
    )


class ClustersCommonProperties(CoreApiModel):
    imap_hostname: str = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Imap Hostname",
    )
    imap_port: int = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Imap Port",
    )
    imap_encryption: EncryptionTypeEnum = Field(
        ..., description="Use these details if you do not have mail hostnames."
    )
    smtp_hostname: str = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Smtp Hostname",
    )
    smtp_port: int = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Smtp Port",
    )
    smtp_encryption: EncryptionTypeEnum = Field(
        ..., description="Use these details if you do not have mail hostnames."
    )
    pop3_hostname: str = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Pop3 Hostname",
    )
    pop3_port: int = Field(
        ...,
        description="Use these details if you do not have mail hostnames.",
        title="Pop3 Port",
    )
    pop3_encryption: EncryptionTypeEnum = Field(
        ..., description="Use these details if you do not have mail hostnames."
    )
    phpmyadmin_url: AnyUrl = Field(..., title="Phpmyadmin Url")


class CustomConfigCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    server_software_name: CustomConfigServerSoftwareNameEnum = Field(
        ...,
        description="When the server software nginx is used, custom configs are added to the `global` context.",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.",
        title="Contents",
    )


class CustomConfigIncludes(CoreApiModel):
    cluster: ClusterResource


class CustomConfigResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.",
        title="Contents",
    )
    server_software_name: CustomConfigServerSoftwareNameEnum
    includes: CustomConfigIncludes


class CustomConfigSnippetCreateFromContentsRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    server_software_name: VirtualHostServerSoftwareNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    is_default: bool = Field(
        ...,
        description="Automatically include in all virtual hosts custom configs.",
        title="Is Default",
    )
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ..., title="Contents"
    )


class CustomConfigSnippetCreateFromTemplateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    server_software_name: VirtualHostServerSoftwareNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    is_default: bool = Field(
        ...,
        description="Automatically include in all virtual hosts custom configs.",
        title="Is Default",
    )
    template_name: CustomConfigSnippetTemplateNameEnum = Field(
        ...,
        description="The following templates are compatible with the following server software:\n\n* Laravel: nginx (for Apache, simply use the `.htaccess` included with Laravel)\n* Compression: nginx (for Apache, enabled by default)",
    )


class CustomConfigSnippetIncludes(CoreApiModel):
    cluster: ClusterResource


class CustomConfigSnippetResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    server_software_name: VirtualHostServerSoftwareNameEnum
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ..., title="Contents"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    is_default: bool = Field(
        ...,
        description="Automatically include in all virtual hosts custom configs.",
        title="Is Default",
    )
    includes: CustomConfigSnippetIncludes


class CustomConfigSnippetUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    server_software_name: VirtualHostServerSoftwareNameEnum
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535) = Field(
        ..., title="Contents"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    is_default: bool = Field(
        ...,
        description="Automatically include in all virtual hosts custom configs.",
        title="Is Default",
    )


class CustomerIPAddressCreateRequest(CoreApiModel):
    service_account_name: str = Field(
        ...,
        description="Must be service account with group 'Internet Router'.\n\nRetrieve service accounts with `GET /api/v1/customers/{id}/ip-addresses`.",
        title="Service Account Name",
    )
    dns_name: str = Field(..., description="Reverse DNS.", title="Dns Name")
    address_family: IPAddressFamilyEnum


class DatabaseCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    optimizing_enabled: bool = Field(
        ...,
        description="Periodically automatically run `OPTIMIZE` on database.\n\nEnabling is only supported for MariaDB server software.",
        title="Optimizing Enabled",
    )
    backups_enabled: bool = Field(
        ...,
        description="Periodically automatically create backup of database.\n\nDisabling is only supported for MariaDB server software.",
        title="Backups Enabled",
    )


class DatabaseIncludes(CoreApiModel):
    cluster: ClusterResource


class DatabaseResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    optimizing_enabled: bool = Field(
        ...,
        description="Periodically automatically run `OPTIMIZE` on database.\n\nEnabling is only supported for MariaDB server software.",
        title="Optimizing Enabled",
    )
    backups_enabled: bool = Field(
        ...,
        description="Periodically automatically create backup of database.\n\nDisabling is only supported for MariaDB server software.",
        title="Backups Enabled",
    )
    includes: DatabaseIncludes


class DatabaseUserCreateRequest(CoreApiModel):
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ...,
        description="Specify unhashed password. Hashed password is returned. Hashed password is purged after several days.",
        title="Password",
    )
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    host: Optional[HostEnum] = Field(
        ...,
        description="Must be set when server software is MariaDB (`server_software_name`). May not be set otherwise.",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    phpmyadmin_firewall_groups_ids: Optional[List[int]] = Field(
        ...,
        description="Only IP networks in the specified firewall groups may access phpMyAdmin.\n\nIf this is null, all IP networks may.",
        title="Phpmyadmin Firewall Groups Ids",
    )


class DatabaseUserGrantCreateRequest(CoreApiModel):
    database_id: int = Field(
        ...,
        description="Must belong to same cluster as database user.\n\nMust have MariaDB server software (`server_software_name`).",
        title="Database Id",
    )
    database_user_id: int = Field(
        ...,
        description="Must belong to same cluster as database.\n\nMust have MariaDB server software (`server_software_name`).",
        title="Database User Id",
    )
    table_name: Optional[
        constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    ] = Field(..., description="Specify null for all tables.", title="Table Name")
    privilege_name: MariaDBPrivilegeEnum


class DatabaseUserIncludes(CoreApiModel):
    cluster: ClusterResource


class DatabaseUserResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)] = Field(
        ..., description="Passwords are deleted after 7 days.", title="Password"
    )
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    host: Optional[HostEnum] = Field(
        ...,
        description="Must be set when server software is MariaDB (`server_software_name`). May not be set otherwise.",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    phpmyadmin_firewall_groups_ids: Optional[List[int]] = Field(
        ...,
        description="Only IP networks in the specified firewall groups may access phpMyAdmin.\n\nIf this is null, all IP networks may.",
        title="Phpmyadmin Firewall Groups Ids",
    )
    includes: DatabaseUserIncludes


class DatabaseUserUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)] = Field(
        ..., description="Passwords are deleted after 7 days.", title="Password"
    )
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    host: Optional[HostEnum] = Field(
        ...,
        description="Must be set when server software is MariaDB (`server_software_name`). May not be set otherwise.",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    phpmyadmin_firewall_groups_ids: Optional[List[int]] = Field(
        ...,
        description="Only IP networks in the specified firewall groups may access phpMyAdmin.\n\nIf this is null, all IP networks may.",
        title="Phpmyadmin Firewall Groups Ids",
    )


class FirewallGroupIncludes(CoreApiModel):
    cluster: ClusterResource


class FirewallGroupResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9_]+$", min_length=1, max_length=32) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    ip_networks: List[str] = Field(
        ...,
        description="To specify a single IP address, use the /128 (IPv6) or /32 (IPv4) CIDR.\n\nFor example: `2001:0db8:8aa:bc:111:abcd:aa11:8991/128` or `192.0.2.6/32`.",
        min_items=1,
        title="Ip Networks",
        unique_items=True,
    )
    includes: FirewallGroupIncludes


class FirewallRuleCreateRequest(CoreApiModel):
    node_id: int = Field(..., description="Must have Admin group.", title="Node Id")
    firewall_group_id: Optional[int] = Field(
        ...,
        description="Allow access from firewall group.\n\nEither 'firewall_group_id' or 'external_provider_name' may not both be set (allow all), or only one.",
        title="Firewall Group Id",
    )
    external_provider_name: Optional[FirewallRuleExternalProviderNameEnum] = Field(
        ...,
        description="Allow access from external provider.\n\nEither 'firewall_group_id' or 'external_provider_name' may not both be set (allow all), or only one.\n\nRequires `firewall_rules_external_providers_enabled` to be set to `true` on the cluster.\n\nWhen using Atlassian, for 'Bitbucket Pipelines build environments' with a smaller size than '4x', AWS must be whitelisted as well. See https://support.atlassian.com/bitbucket-cloud/docs/what-are-the-bitbucket-cloud-ip-addresses-i-should-use-to-configure-my-corporate-firewall/#Valid-IP-addresses-for-Bitbucket-Pipelines-build-environments",
    )
    service_name: Optional[FirewallRuleServiceNameEnum] = Field(
        ...,
        description="Protect service.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
    )
    haproxy_listen_id: Optional[int] = Field(
        ...,
        description="Protect port of HAProxy listen.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
        title="Haproxy Listen Id",
    )
    port: Optional[conint(ge=1, le=65535)] = Field(
        ...,
        description="Protect port.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
        title="Port",
    )


class HAProxyListenCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    nodes_group: NodeGroupEnum = Field(
        ...,
        description="Proxy to nodes with the specified group.\n\nThe following nodes groups are supported: MariaDB, PostgreSQL, Meilisearch, SingleStore, RabbitMQ.",
    )
    nodes_ids: Optional[List[int]] = Field(
        None,
        description="Proxy only to nodes with the specified IDs. these nodes must have the group specified in `nodes_group`.",
        title="Nodes Ids",
    )
    port: Optional[conint(ge=3306, le=7700)] = Field(
        ...,
        description="Listen on port.\n\nEither `port` or `socket_path` must be set.",
        title="Port",
    )
    socket_path: Optional[str] = Field(
        ...,
        description="Listen on socket.\n\nEither `port` or `socket_path` must be set.\n\nMust be under subdirectory of /run/.",
        title="Socket Path",
    )
    load_balancing_method: LoadBalancingMethodEnum = Field(
        LoadBalancingMethodEnum.SOURCE_IP_ADDRESS,
        description="When set to 'Round Robin', requests are routed to the least busy node. This is the most efficient load balancing method, but can cause issues with deadlocks on databases.\n\nWhen set to 'Source IP Address', the initial request by a specific IP address is routed to the least busy node. All follow-up requests are sent to that node. This causes load to be distributed less efficiently than with the 'Round Robin' method, but cannot cause issues with deadlocks on databases.\n\nIf the specified nodes group has only one node, this option has no effect.",
    )
    destination_cluster_id: int = Field(
        ...,
        description="Proxy to nodes in the specified cluster.",
        title="Destination Cluster Id",
    )


class HAProxyListenIncludes(CoreApiModel):
    destination_cluster: ClusterResource
    cluster: ClusterResource


class HAProxyListenResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    nodes_group: NodeGroupEnum = Field(
        ...,
        description="Proxy to nodes with the specified group.\n\nThe following nodes groups are supported: MariaDB, PostgreSQL, Meilisearch, SingleStore, RabbitMQ.",
    )
    nodes_ids: Optional[List[int]] = Field(
        ...,
        description="Proxy only to nodes with the specified IDs. these nodes must have the group specified in `nodes_group`.",
        title="Nodes Ids",
    )
    port: Optional[conint(ge=3306, le=7700)] = Field(
        ...,
        description="Listen on port.\n\nEither `port` or `socket_path` must be set.",
        title="Port",
    )
    socket_path: Optional[str] = Field(
        ...,
        description="Listen on socket.\n\nEither `port` or `socket_path` must be set.\n\nMust be under subdirectory of /run/.",
        title="Socket Path",
    )
    load_balancing_method: Optional[LoadBalancingMethodEnum] = (
        LoadBalancingMethodEnum.SOURCE_IP_ADDRESS
    )
    destination_cluster_id: int = Field(
        ...,
        description="Proxy to nodes in the specified cluster.",
        title="Destination Cluster Id",
    )
    includes: HAProxyListenIncludes


class HTTPValidationError(CoreApiModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")


class HealthResource(CoreApiModel):
    status: HealthStatusEnum


class IPAddressProduct(CoreApiModel):
    uuid: UUID4 = Field(..., title="Uuid")
    name: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    type: IPAddressProductTypeEnum
    price: confloat(ge=0.0) = Field(..., title="Price")
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2) = Field(
        ..., title="Period"
    )
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3) = Field(
        ..., title="Currency"
    )


class WebServerLogAccessResource(CoreApiModel):
    remote_address: str = Field(..., title="Remote Address")
    raw_message: constr(min_length=1, max_length=65535) = Field(
        ..., title="Raw Message"
    )
    method: Optional[LogMethodEnum] = None
    uri: Optional[constr(min_length=1, max_length=65535)] = Field(None, title="Uri")
    timestamp: datetime = Field(..., title="Timestamp")
    status_code: int = Field(..., title="Status Code")
    bytes_sent: conint(ge=0) = Field(..., title="Bytes Sent")


class WebServerLogErrorResource(CoreApiModel):
    remote_address: str = Field(..., title="Remote Address")
    raw_message: constr(min_length=1, max_length=65535) = Field(
        ..., title="Raw Message"
    )
    method: Optional[LogMethodEnum] = None
    uri: Optional[constr(min_length=1, max_length=65535)] = Field(None, title="Uri")
    timestamp: datetime = Field(..., title="Timestamp")
    error_message: constr(min_length=1, max_length=65535) = Field(
        ..., title="Error Message"
    )


class MariaDBEncryptionKeyIncludes(CoreApiModel):
    cluster: ClusterResource


class MariaDBEncryptionKeyResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    identifier: int = Field(
        ...,
        description="Identifier specified as `ENCRYPTION_KEY_ID` table option.\n\nFor more information, see: https://mariadb.com/kb/en/innodb-encryption-overview/#creating-encrypted-tables",
        title="Identifier",
    )
    key: constr(regex=r"^[a-z0-9]+$", min_length=64, max_length=64) = Field(
        ..., title="Key"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    includes: MariaDBEncryptionKeyIncludes


class NodeGroupDependency(CoreApiModel):
    is_dependency: bool = Field(
        ...,
        description="Will the service become unavailable when this node is unreachable?",
        title="Is Dependency",
    )
    impact: Optional[str] = Field(
        ...,
        description="What impact will this node becoming unreachable have?",
        title="Impact",
    )
    reason: str = Field(
        ...,
        description="Why will the node being unreachable have impact?",
        title="Reason",
    )
    group: NodeGroupEnum


class NodeGroupsProperties(CoreApiModel):
    Redis: Optional[NodeRedisGroupProperties]
    MariaDB: Optional[NodeMariaDBGroupProperties]
    RabbitMQ: Optional[NodeRabbitMQGroupProperties]


class NodeIncludes(CoreApiModel):
    cluster: ClusterResource


class NodeResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    hostname: str = Field(..., title="Hostname")
    product: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2) = Field(
        ...,
        description="Get available products with `GET /nodes/products`.",
        title="Product",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    groups: List[NodeGroupEnum] = Field(
        ...,
        description="Only one node in any cluster may have these groups:\n\n* Borg\n* Elasticsearch\n* SingleStore\n* Meilisearch\n* maldet\n* Admin\n* PostgreSQL\n* Meilisearch\n\nThe following groups do not require any cluster group:\n\n* HAProxy\n* KernelCare\n* New Relic\n* Docker\n* Admin\n\nThe following groups may only be used on clusters with the Borg Client group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Borg Server group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Database group:\n\n* MariaDB\n* Meilisearch\n* PostgreSQL\n* Redis\n* Grafana\n* SingleStore\n* Metabase\n* Elasticsearch\n* RabbitMQ\n\nThe following groups may only be used on clusters with the Mail group:\n\n* Dovecot\n* Admin\n\nThe following groups may only be used on clusters with the Redirect group:\n\n* Fast Redirect\n\nThe following groups may only be used on clusters with the Web group:\n\n* Apache\n* nginx\n* PHP\n* Passenger\n* ProFTPD\n* Composer\n* WP-CLI\n* ImageMagick\n* wkhtmltopdf\n* GNU Mailutils\n* Puppeteer\n* LibreOffice\n* Ghostscript\n* FFmpeg\n* maldet\n* NodeJS\n* ClamAV\n\nThe groups Composer and WP-CLI require the PHP group.\n\nThe group Puppeteer requires the NodeJS group. This group only installs the dependencies for Puppeteer; you must install the NodeJS module within your application(s).\n\nThe group KernelCare requires a KernelCare license key to be set on the cluster (`kernelcare_license_key`).\n\nFor the group ClamAV, clamd listens on port 3310. clamd can be accessed from any node in the cluster; it does not have any form of authentication.\nFind the implications on https://github.com/Cisco-Talos/clamav/issues/1169\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id` (see [Domain Routers](#tag/Domain-Routers)).\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n\nFor the group Docker, to manage Docker, log in to SSH as the `docker` user using a [Root SSH Key](#tag/Root-SSH-Keys).\n",
        title="Groups",
        unique_items=True,
    )
    comment: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Comment")
    load_balancer_health_checks_groups_pairs: Dict[
        NodeGroupEnum, List[NodeGroupEnum]
    ] = Field(
        ...,
        description="When health-checking the primary group (key), check health of additional groups (value). Node must have specified primary group and additional groups. The following primary groups are supported: Apache, nginx, Fast Redirect. The following additional groups are supported: MariaDB, PostgreSQL.\n\nCommon use case: when web server uses local database server, when checking web server health, check database server health.",
        title="Load Balancer Health Checks Groups Pairs",
    )
    groups_properties: NodeGroupsProperties = Field(
        ...,
        description="Group-specific properties. Must be set to null for groups that the node does not have. Must be set to the correct value if the node has groups Redis, MariaDB, RabbitMQ.",
    )
    is_ready: bool = Field(..., title="Is Ready")
    includes: NodeIncludes


class NodeUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    hostname: str = Field(..., title="Hostname")
    product: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2) = Field(
        ...,
        description="Get available products with `GET /nodes/products`.",
        title="Product",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    groups: List[NodeGroupEnum] = Field(
        ...,
        description="Software on this node. If multiple nodes in the same cluster have the same software (groups), that software is redundant / highly-available.\n\nOnly one node in any cluster may have these groups:\n\n* Borg\n* Elasticsearch\n* SingleStore\n* Meilisearch\n* maldet\n* Admin\n* PostgreSQL\n* Meilisearch\n\nThe following groups do not require any cluster group:\n\n* HAProxy\n* KernelCare\n* New Relic\n* Docker\n* Admin\n\nThe following groups may only be used on clusters with the Borg Client group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Borg Server group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Database group:\n\n* MariaDB\n* Meilisearch\n* PostgreSQL\n* Redis\n* Grafana\n* SingleStore\n* Metabase\n* Elasticsearch\n* RabbitMQ\n\nThe following groups may only be used on clusters with the Mail group:\n\n* Dovecot\n* Admin\n\nThe following groups may only be used on clusters with the Redirect group:\n\n* Fast Redirect\n\nThe following groups may only be used on clusters with the Web group:\n\n* Apache\n* nginx\n* PHP\n* Passenger\n* ProFTPD\n* Composer\n* WP-CLI\n* ImageMagick\n* wkhtmltopdf\n* GNU Mailutils\n* Puppeteer\n* LibreOffice\n* Ghostscript\n* FFmpeg\n* maldet\n* NodeJS\n* ClamAV\n\nThe groups Composer and WP-CLI require the PHP group.\n\nThe group Puppeteer requires the NodeJS group. This group only installs the dependencies for Puppeteer; you must install the NodeJS module within your application(s).\n\nThe group KernelCare requires a KernelCare license key to be set on the cluster (`kernelcare_license_key`).\n\nFor the group ClamAV, clamd listens on port 3310. clamd can be accessed from any node in the cluster; it does not have any form of authentication.\nFind the implications on https://github.com/Cisco-Talos/clamav/issues/1169\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id` (see [Domain Routers](#tag/Domain-Routers)).\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n\nFor the group Docker, to manage Docker, log in to SSH as the `docker` user using a [Root SSH Key](#tag/Root-SSH-Keys).\n",
        title="Groups",
        unique_items=True,
    )
    comment: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Comment")
    load_balancer_health_checks_groups_pairs: Dict[
        NodeGroupEnum, List[NodeGroupEnum]
    ] = Field(
        ...,
        description="When health-checking the primary group (key), check health of additional groups (value). Node must have specified primary group and additional groups. The following primary groups are supported: Apache, nginx, Fast Redirect. The following additional groups are supported: MariaDB, PostgreSQL.\n\nCommon use case: when web server uses local database server, when checking web server health, check database server health.",
        title="Load Balancer Health Checks Groups Pairs",
    )


class NodeUpdateRequest(CoreApiModel):
    groups: Optional[List[NodeGroupEnum]] = Field(
        None,
        description="Software on this node. If multiple nodes in the same cluster have the same software (groups), that software is redundant / highly-available.\n\nOnly one node in any cluster may have these groups:\n\n* Borg\n* Elasticsearch\n* SingleStore\n* Meilisearch\n* maldet\n* Admin\n* PostgreSQL\n* Meilisearch\n\nThe following groups do not require any cluster group:\n\n* HAProxy\n* KernelCare\n* New Relic\n\nThe following groups may only be used on clusters with the Borg Client group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Borg Server group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Database group:\n\n* MariaDB\n* Meilisearch\n* PostgreSQL\n* Redis\n* Grafana\n* SingleStore\n* Metabase\n* Elasticsearch\n* RabbitMQ\n\nThe following groups may only be used on clusters with the Mail group:\n\n* Dovecot\n* Admin\n\nThe following groups may only be used on clusters with the Redirect group:\n\n* Fast Redirect\n\nThe following groups may only be used on clusters with the Web group:\n\n* Apache\n* Admin\n* nginx\n* PHP\n* Passenger\n* ProFTPD\n* Composer\n* WP-CLI\n* ImageMagick\n* wkhtmltopdf\n* GNU Mailutils\n* Puppeteer\n* LibreOffice\n* Ghostscript\n* FFmpeg\n* Docker\n* maldet\n* NodeJS\n* ClamAV\n\nThe groups Composer and WP-CLI require the PHP group.\n\nThe group Puppeteer requires the NodeJS group. This group only installs the dependencies for Puppeteer; you must install the NodeJS module within your application(s).\n\nThe group KernelCare requires a KernelCare license key to be set on the cluster (`kernelcare_license_key`).\n\nFor the group ClamAV, clamd listens on port 3310. clamd can be accessed from any node in the cluster; it does not have any form of authentication.\nFind the implications on https://github.com/Cisco-Talos/clamav/issues/1169\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id` (see [Domain Routers](#tag/Domain-Routers)).\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n",
        title="Groups",
    )
    comment: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(None, title="Comment")
    load_balancer_health_checks_groups_pairs: Optional[
        Dict[NodeGroupEnum, List[NodeGroupEnum]]
    ] = Field(
        None,
        description="When health-checking the primary group (key), check health of additional groups (value). Node must have specified primary group and additional groups. The following primary groups are supported: Apache, nginx, Fast Redirect. The following additional groups are supported: MariaDB, PostgreSQL.\n\nCommon use case: when web server uses local database server, when checking web server health, check database server health.",
        title="Load Balancer Health Checks Groups Pairs",
    )


class PassengerAppCreateNodeJSRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    app_root: str = Field(
        ..., description="Must be in UNIX user home directory.", title="App Root"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    environment: PassengerEnvironmentEnum
    environment_variables: Dict[
        constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")
    ] = Field(
        ...,
        description="Do not store secrets in them in environment variables; they are stored in plain text.",
        title="Environment Variables",
    )
    max_pool_size: int = Field(
        ...,
        description="The maximum amount of concurrent processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `10`.",
        title="Max Pool Size",
    )
    max_requests: int = Field(
        ...,
        description="Each process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `2000`.",
        title="Max Requests",
    )
    pool_idle_time: int = Field(
        ...,
        description="Each process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy pool (that started many processes) is no longer busy. However, if all processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Pool Idle Time",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    cpu_limit: Optional[int] = Field(..., title="Cpu Limit")
    nodejs_version: constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$") = Field(
        ...,
        description="Must be installed on cluster (`nodejs_versions`).",
        title="Nodejs Version",
    )
    startup_file: str = Field(..., title="Startup File")


class PassengerAppUpdateDeprecatedRequest(CoreApiModel):
    id: int = Field(..., title="Id")
    cluster_id: int = Field(..., title="Cluster Id")
    port: int = Field(..., title="Port")
    app_type: PassengerAppTypeEnum
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    app_root: str = Field(
        ..., description="Must be in UNIX user home directory.", title="App Root"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    environment: PassengerEnvironmentEnum
    environment_variables: Dict[
        constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")
    ] = Field(
        ...,
        description="Do not store secrets in them in environment variables; they are stored in plain text.",
        title="Environment Variables",
    )
    max_pool_size: int = Field(
        ...,
        description="The maximum amount of concurrent processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `10`.",
        title="Max Pool Size",
    )
    max_requests: int = Field(
        ...,
        description="Each process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `2000`.",
        title="Max Requests",
    )
    pool_idle_time: int = Field(
        ...,
        description="Each process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy pool (that started many processes) is no longer busy. However, if all processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Pool Idle Time",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    cpu_limit: Optional[int] = Field(..., title="Cpu Limit")
    nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        ..., title="Nodejs Version"
    )
    startup_file: Optional[str] = Field(..., title="Startup File")


class PassengerAppUpdateRequest(CoreApiModel):
    environment: Optional[PassengerEnvironmentEnum] = None
    environment_variables: Optional[
        Dict[constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")]
    ] = Field(
        None,
        description="Do not store secrets in them in environment variables; they are stored in plain text.",
        title="Environment Variables",
    )
    max_pool_size: Optional[int] = Field(
        None,
        description="The maximum amount of concurrent processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `10`.",
        title="Max Pool Size",
    )
    max_requests: Optional[int] = Field(
        None,
        description="Each process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `2000`.",
        title="Max Requests",
    )
    pool_idle_time: Optional[int] = Field(
        None,
        description="Each process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy pool (that started many processes) is no longer busy. However, if all processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Pool Idle Time",
    )
    is_namespaced: Optional[bool] = Field(
        None,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    cpu_limit: Optional[int] = Field(None, title="Cpu Limit")
    nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        None,
        description="Must be installed on cluster (`nodejs_versions`).",
        title="Nodejs Version",
    )
    startup_file: Optional[str] = Field(None, title="Startup File")


class RedisInstanceIncludes(CoreApiModel):
    cluster: ClusterResource


class RedisInstanceResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    port: int = Field(..., title="Port")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255) = Field(
        ..., title="Password"
    )
    memory_limit: conint(ge=8) = Field(..., description="In MB.", title="Memory Limit")
    max_databases: int = Field(..., title="Max Databases")
    eviction_policy: RedisEvictionPolicyEnum = Field(
        ...,
        description="See [Redis documentation](https://redis.io/docs/reference/eviction/#eviction-policies).\n\nIf you don't know what to set, set to `volatile-lru`.",
    )
    includes: RedisInstanceIncludes


class RootSSHKeyIncludes(CoreApiModel):
    cluster: ClusterResource


class RootSSHKeyResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    public_key: Optional[str] = Field(..., title="Public Key")
    private_key: Optional[str] = Field(..., title="Private Key")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    includes: RootSSHKeyIncludes


class SecurityTXTPolicyIncludes(CoreApiModel):
    cluster: ClusterResource


class SecurityTXTPolicyResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    expires_timestamp: datetime = Field(..., title="Expires Timestamp")
    email_contacts: List[EmailStr] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Email Contacts",
        unique_items=True,
    )
    url_contacts: List[AnyUrl] = Field(
        ...,
        description="At least `url_contacts` or `email_contacts` must be set.",
        title="Url Contacts",
        unique_items=True,
    )
    encryption_key_urls: List[AnyUrl] = Field(
        ..., title="Encryption Key Urls", unique_items=True
    )
    acknowledgment_urls: List[AnyUrl] = Field(
        ..., title="Acknowledgment Urls", unique_items=True
    )
    policy_urls: List[AnyUrl] = Field(..., title="Policy Urls", unique_items=True)
    opening_urls: List[AnyUrl] = Field(..., title="Opening Urls", unique_items=True)
    preferred_languages: List[LanguageCodeEnum] = Field(
        ..., title="Preferred Languages", unique_items=True
    )
    includes: SecurityTXTPolicyIncludes


class TaskCollectionIncludes(CoreApiModel):
    cluster: Optional[ClusterResource]


class TaskCollectionResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    object_id: Optional[int] = Field(..., title="Object Id")
    object_model_name: ObjectModelNameEnum
    uuid: UUID4 = Field(..., title="Uuid")
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Description"
    )
    collection_type: TaskCollectionTypeEnum
    cluster_id: Optional[int] = Field(..., title="Cluster Id")
    reference: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255) = Field(
        ..., description="Free-form reference.", title="Reference"
    )
    includes: TaskCollectionIncludes


class TaskResult(CoreApiModel):
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Description"
    )
    uuid: UUID4 = Field(..., title="Uuid")
    message: Optional[str] = Field(..., title="Message")
    state: TaskStateEnum
    retries: conint(ge=0) = Field(..., title="Retries")


class TokenResource(CoreApiModel):
    access_token: constr(regex=r"^[ -~]+$", min_length=1) = Field(
        ..., title="Access Token"
    )
    token_type: TokenTypeEnum
    expires_in: int = Field(..., title="Expires In")


class UNIXUserIncludes(CoreApiModel):
    cluster: ClusterResource


class UNIXUserResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)] = Field(
        ...,
        description="If set to null, only SSH key authentication is allowed.",
        title="Password",
    )
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    unix_id: int = Field(..., title="Unix Id")
    home_directory: str = Field(
        ...,
        description="Cluster UNIX users home directory (`unix_users_home_directory`) + UNIX user username (`username`).",
        title="Home Directory",
    )
    ssh_directory: str = Field(..., title="Ssh Directory")
    virtual_hosts_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Web group. May not be set otherwise.\n\nThe virtual hosts directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `virtual-hosts`.",
        title="Virtual Hosts Directory",
    )
    mail_domains_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Mail group. May not be set otherwise.\n\nThe mail domains directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `mail-domains`.",
        title="Mail Domains Directory",
    )
    borg_repositories_directory: Optional[str] = Field(
        ...,
        description="Must be set when cluster has Borg Server group. May not be set otherwise.\n\nThe Borg repositories directory must start with the cluster UNIX user home directory + the UNIX user username. The path may end there, or it can end with **one** custom path element such as `borg-repositories`.",
        title="Borg Repositories Directory",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    shell_path: ShellPathEnum = Field(
        ...,
        description="When set to `/usr/local/bin/jailshell`, Bubblewrap Toolkit must be enabled on the cluster (`bubblewrap_toolkit_enabled`).\n\nWhen set to `/usr/local/bin/jailshell`, multiple security measures are applied, most notably the inability to see other UNIX user's processes. Recommended for shared environments in which users are not trusted.",
    )
    record_usage_files: bool = Field(
        ...,
        description="May only be set to `true` when cluster has Web group.\n\nWhen enabled, UNIX user usages objects contain a list of largest files (`files`).",
        title="Record Usage Files",
    )
    default_php_version: Optional[str] = Field(
        ...,
        description="When set, the `php` command is aliased to the specified PHP version. Otherwise, the system default is used.\n\nMust be installed on cluster (`php_versions`).",
        title="Default Php Version",
    )
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        ...,
        description="When set, the following commands are activated to the specified NodeJS version: `corepack`, `npm`, `npx`, `node`. Otherwise, these commands are not available.\n\nMust be installed on cluster (`nodejs_versions`).\n\nRequires shell path (`shell_path`) to be set to `/usr/local/bin/jailshell`.",
        title="Default Nodejs Version",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")
    includes: UNIXUserIncludes


class URLRedirectIncludes(CoreApiModel):
    cluster: ClusterResource


class URLRedirectResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    destination_url: AnyUrl = Field(..., title="Destination Url")
    status_code: StatusCodeEnum
    keep_query_parameters: bool = Field(
        ...,
        description="Append query parameters from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io?a=b` to `https://www.dropflix.io?a=b`.",
        title="Keep Query Parameters",
    )
    keep_path: bool = Field(
        ...,
        description="Append path from original URL to destination URL. For example, when `true`, a URL redirect from `dropflix.io` to `https://www.dropflix.io` will redirect from `dropflix.io/a` to `https://www.dropflix.io/a`.",
        title="Keep Path",
    )
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Description")
    includes: URLRedirectIncludes


class VirtualHostCreateRequest(CoreApiModel):
    server_software_name: Optional[VirtualHostServerSoftwareNameEnum] = Field(
        ..., description="Set to first found server software by default."
    )
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]] = Field(
        ...,
        description="Must be set when Apache server software is used (`server_software_name`). May not be set otherwise.\n\nOptions that may be set in `.htaccess` files. This is usually limited as some options pose security risks. For more information, see: https://httpd.apache.org/docs/2.4/mod/core.html#allowoverride\n\nIf you don't know what to set, set to `['AuthConfig', 'FileInfo', 'Indexes', 'Limit']`. This suffices for almost all CMSes/systems, including WordPress, Joomla! and Laravel.",
        title="Allow Override Directives",
    )
    allow_override_option_directives: Optional[
        List[AllowOverrideOptionDirectiveEnum]
    ] = Field(
        ...,
        description="Must be set when Apache server software is used (`server_software_name`). May not be set otherwise.\n\nOption directives that may be set in `.htaccess` files. This is usually limited as some option directives pose security risks. For more information, see: https://httpd.apache.org/docs/2.4/mod/core.html#options\n\nIf you don't know what to set, set to `['Indexes', 'MultiViews', 'None', 'SymLinksIfOwnerMatch']`. This suffices for almost all CMSes/systems, including WordPress, Joomla! and Laravel.",
        title="Allow Override Option Directives",
    )
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    public_root: str = Field(
        ...,
        description="This directory is created automatically. It is also periodically scanned for CMSes which will be added to the API.\n\nThis is what you should set to a custom value for systems such as Laravel. Often to a subdirectory such as `public`.\n\nDo not confuse with document root (`document_root`), which is the directory that files will be loaded from when receiving an HTTP request.\n\nMust be inside UNIX user virtual hosts directory + specified domain (e.g. `/home/dropflix/dropflix.io/htdocs`).",
        title="Public Root",
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    document_root: str = Field(
        ...,
        description="When receiving an HTTP request, files will be loaded from this directory.",
        title="Document Root",
    )
    fpm_pool_id: Optional[int] = Field(
        ...,
        description="Let the specified FPM pool handle requests to PHP files.\n\nMay not be set when Passenger app (`passenger_app_id`) is set.",
        title="Fpm Pool Id",
    )
    passenger_app_id: Optional[int] = Field(
        ...,
        description="Let the specified Passenger app handle requests.\n\nMay only be set when server software is set to nginx (`server_software_name`).\n\nMay not be set when FPM pool (`fpm_pool_id`) is set.",
        title="Passenger App Id",
    )
    custom_config: Optional[
        constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    ] = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.\n\nDefault custom config snippets (`is_default`) are inserted after the virtual host specific custom config. To place a default custom config snippet earlier, include it manually in the virtual host specific custom config.\n\nWhen the server software nginx is used, custom configs are added to the `server` context.\n\nIf the virtual host has basic authentication realms, the `auth_basic` and `auth_basic_user_file` directives may not be set in the default context.\n",
        title="Custom Config",
    )


class BorgRepositoryIncludes(CoreApiModel):
    unix_user: Optional[UNIXUserResource]
    cluster: ClusterResource


class BorgRepositoryResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    passphrase: constr(regex=r"^[ -~]+$", min_length=24, max_length=255) = Field(
        ..., title="Passphrase"
    )
    remote_host: str = Field(..., title="Remote Host")
    remote_path: str = Field(..., title="Remote Path")
    remote_username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32) = (
        Field(..., title="Remote Username")
    )
    cluster_id: int = Field(..., title="Cluster Id")
    keep_hourly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Hourly",
    )
    keep_daily: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Daily",
    )
    keep_weekly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Weekly",
    )
    keep_monthly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Monthly",
    )
    keep_yearly: Optional[int] = Field(
        ...,
        description="At least one keep attribute must be set.\n\nFor more information, see: https://github.com/borgbackup/borg/blob/master/docs/misc/prune-example.txt",
        title="Keep Yearly",
    )
    identity_file_path: Optional[str] = Field(
        ...,
        description="Must be set when UNIX user (`unix_user_id`) is set. May not be set otherwise.",
        title="Identity File Path",
    )
    unix_user_id: Optional[int] = Field(..., title="Unix User Id")
    includes: BorgRepositoryIncludes


class CertificateIncludes(CoreApiModel):
    cluster: ClusterResource


class CertificateResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    main_common_name: str = Field(..., title="Main Common Name")
    common_names: List[str] = Field(
        ..., min_items=1, title="Common Names", unique_items=True
    )
    expires_at: datetime = Field(
        ..., description="Timestamp is in UTC.", title="Expires At"
    )
    certificate: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    ) = Field(
        ...,
        description="Certificate must have a common name.\n\nMust end with line feed.",
        title="Certificate",
    )
    ca_chain: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    ) = Field(..., description="Must end with line feed.", title="Ca Chain")
    private_key: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    ) = Field(..., description="Must end with line feed.", title="Private Key")
    cluster_id: int = Field(..., title="Cluster Id")
    includes: CertificateIncludes


class ClusterDeploymentResults(CoreApiModel):
    created_at: datetime = Field(..., title="Created At")
    tasks_results: List[ClusterDeploymentTaskResult] = Field(..., title="Tasks Results")


class CronIncludes(CoreApiModel):
    cluster: ClusterResource
    unix_user: UNIXUserResource
    node: NodeResource


class CronResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: int = Field(..., title="Node Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ...,
        description="Use the variable `$CYBERFUSION_DEFAULT_PHP_VERSION_BINARY` to use the UNIX user default PHP version (`default_php_version`). For more information, see 'Differences between PHP versions'.\n\nThe command may not call `exit`.",
        title="Command",
    )
    email_address: Optional[EmailStr] = Field(
        ...,
        description="Emails about failed cron runs are sent to this email address. If the value is null, emails are sent to Cyberfusion.\n\nThis email contains the return code and output.\n\nA cron run has failed when the command exits with a return code other than 0.\n\nIf the cron fails over 10 times consecutively, no more emails are sent.",
        title="Email Address",
    )
    schedule: str = Field(..., title="Schedule")
    error_count: int = Field(
        ...,
        description="Send email after N failed cron runs.\n\nThe counter is reset after a successful cron run.\n\nIf you don't know what to set, set to `1`, so an email is sent after 1 failed cron run. This ensures an email is sent for _every_ failed cron run.",
        title="Error Count",
    )
    random_delay_max_seconds: int = Field(
        ...,
        description="Randomly delay cron run.\n\nUse to avoid overloading a node when many crons run on the same schedule.\n\nIf you don't know what to set, set to `10`.",
        title="Random Delay Max Seconds",
    )
    timeout_seconds: Optional[int] = Field(
        ...,
        description="Cron will be automatically killed after this time. Such a timeout is usually used as a failsafe, so that when the command unexpectedly takes too long (e.g. due to an external API call by a script), the cron isn't stuck (or locked if `locking_enabled` is `true`) for a long or indefinite time.",
        title="Timeout Seconds",
    )
    locking_enabled: bool = Field(
        ...,
        description="When enabled, multiple instances of the cron may not run simultaneously. This can prevent multiple crons from manipulating the same data, or prevent a node from being overloaded when a long-running cron is using many resources.\n\nDisable for crons that handle locking themselves (such as Laravel's `withoutOverlapping`.)",
        title="Locking Enabled",
    )
    is_active: bool = Field(..., title="Is Active")
    memory_limit: Optional[conint(ge=256)] = Field(
        ..., description="In MB.", title="Memory Limit"
    )
    cpu_limit: Optional[int] = Field(
        ...,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.",
        title="Cpu Limit",
    )
    includes: CronIncludes


class DaemonIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class DaemonResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535) = Field(
        ..., title="Command"
    )
    nodes_ids: List[int] = Field(..., min_items=1, title="Nodes Ids", unique_items=True)
    memory_limit: Optional[conint(ge=256)] = Field(
        ..., description="In MB.", title="Memory Limit"
    )
    cpu_limit: Optional[int] = Field(
        ...,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.",
        title="Cpu Limit",
    )
    includes: DaemonIncludes


class DatabaseUserGrantIncludes(CoreApiModel):
    cluster: ClusterResource
    database: DatabaseResource
    database_user: DatabaseUserResource


class DatabaseUserGrantResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    database_id: int = Field(
        ...,
        description="Must belong to same cluster as database user.\n\nMust have MariaDB server software (`server_software_name`).",
        title="Database Id",
    )
    database_user_id: int = Field(
        ...,
        description="Must belong to same cluster as database.\n\nMust have MariaDB server software (`server_software_name`).",
        title="Database User Id",
    )
    table_name: Optional[
        constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    ] = Field(..., description="Specify null for all tables.", title="Table Name")
    privilege_name: MariaDBPrivilegeEnum
    includes: DatabaseUserGrantIncludes


class FPMPoolIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class FPMPoolResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ...,
        description="We recommend adding the version to the name (e.g. `dropflix83`). As `version` cannot be changed, when wanting to change the version, a new FPM pool must be created. By adding the version to the name, the old and new FPM pools can exist simultaneously without name conflicts (as `name` is unique).",
        title="Name",
    )
    version: str = Field(
        ...,
        description="Must be installed on cluster (`php_versions`).\n\nThis value cannot be changed as it is FPM pool specific. When wanting to change the version, create a new FPM pool, and update it on the virtual host(s) that use the current FPM pool. Or use the CLI command `corectl fpm-pools update-version` which does this for you.",
        title="Version",
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    max_children: int = Field(
        ...,
        description="The maximum amount of concurrent PHP-FPM processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `5`.",
        title="Max Children",
    )
    max_requests: int = Field(
        ...,
        description="Each PHP-FPM process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `20`.",
        title="Max Requests",
    )
    process_idle_timeout: int = Field(
        ...,
        description="Each PHP-FPM process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy PHP-FPM pool (that started many PHP-FPM processes) is no longer busy. However, if all PHP-FPM processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Process Idle Timeout",
    )
    cpu_limit: Optional[int] = Field(
        ...,
        description="Each step of `100` means 1 CPU core. For example, a value of `200` means 2 CPU cores.",
        title="Cpu Limit",
    )
    log_slow_requests_threshold: Optional[int] = Field(
        ...,
        description="Minimum amount of seconds a request must take to be logged to the PHP-FPM slow log.\n\nTo retrieve the results, contact Cyberfusion.",
        title="Log Slow Requests Threshold",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    memory_limit: Optional[conint(ge=256)] = Field(
        ..., description="In MB.", title="Memory Limit"
    )
    includes: FPMPoolIncludes


class FTPUserIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class FTPUserResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    username: constr(regex=r"^[a-z0-9-_.@]+$", min_length=1, max_length=32) = Field(
        ..., title="Username"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    directory_path: str = Field(
        ...,
        description="The directory path must start with the UNIX user home directory. The path may end there, or it can end with custom path elements under it.",
        title="Directory Path",
    )
    includes: FTPUserIncludes


class FirewallRuleIncludes(CoreApiModel):
    node: NodeResource
    firewall_group: Optional[FirewallGroupResource]
    haproxy_listen: Optional[HAProxyListenResource]
    cluster: ClusterResource


class FirewallRuleResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: int = Field(..., description="Must have Admin group.", title="Node Id")
    firewall_group_id: Optional[int] = Field(
        ...,
        description="Allow access from firewall group.\n\nEither 'firewall_group_id' or 'external_provider_name' may not both be set (allow all), or only one.",
        title="Firewall Group Id",
    )
    external_provider_name: Optional[FirewallRuleExternalProviderNameEnum] = Field(
        ...,
        description="Allow access from external provider.\n\nEither 'firewall_group_id' or 'external_provider_name' may not both be set (allow all), or only one.\n\nRequires `firewall_rules_external_providers_enabled` to be set to `true` on the cluster.",
    )
    service_name: Optional[FirewallRuleServiceNameEnum] = Field(
        ...,
        description="Protect service.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
    )
    haproxy_listen_id: Optional[int] = Field(
        ...,
        description="Protect port of HAProxy listen.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
        title="Haproxy Listen Id",
    )
    port: Optional[conint(ge=1, le=65535)] = Field(
        ...,
        description="Protect port.\n\nEither 'service_name', 'haproxy_listen_id' or 'port' must be set.",
        title="Port",
    )
    includes: FirewallRuleIncludes


class HAProxyListenToNodeIncludes(CoreApiModel):
    haproxy_listen: HAProxyListenResource
    node: NodeResource
    cluster: ClusterResource


class HAProxyListenToNodeResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    haproxy_listen_id: int = Field(..., title="Haproxy Listen Id")
    node_id: int = Field(
        ..., description="Node must have HAProxy group.", title="Node Id"
    )
    includes: HAProxyListenToNodeIncludes


class HostsEntryIncludes(CoreApiModel):
    node: NodeResource
    cluster: ClusterResource


class HostsEntryResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    node_id: int = Field(
        ...,
        description="Route lookups for hostname to specified node.",
        title="Node Id",
    )
    host_name: str = Field(..., title="Host Name")
    cluster_id: int = Field(..., title="Cluster Id")
    includes: HostsEntryIncludes


class HtpasswdFileIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class HtpasswdFileResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    unix_user_id: int = Field(..., title="Unix User Id")
    includes: HtpasswdFileIncludes


class HtpasswdUserIncludes(CoreApiModel):
    htpasswd_file: HtpasswdFileResource
    cluster: ClusterResource


class HtpasswdUserResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )
    cluster_id: int = Field(..., title="Cluster Id")
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=255) = Field(
        ..., title="Username"
    )
    htpasswd_file_id: int = Field(..., title="Htpasswd File Id")
    includes: HtpasswdUserIncludes


class MailDomainIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class MailDomainResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    domain: str = Field(..., title="Domain")
    unix_user_id: int = Field(..., title="Unix User Id")
    catch_all_forward_email_addresses: List[EmailStr] = Field(
        ..., title="Catch All Forward Email Addresses", unique_items=True
    )
    is_local: bool = Field(
        ...,
        description="Set to `true` when MX records point to cluster. Set to `false` when mail domain exists on cluster, but MX records point elsewhere.\n\nWhen this value is `false`, emails sent from other mail accounts on the same cluster will not be delivered locally, but sent to the MX records.",
        title="Is Local",
    )
    includes: MailDomainIncludes


class MailHostnameIncludes(CoreApiModel):
    certificate: Optional[CertificateResource]
    cluster: ClusterResource


class MailHostnameResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    domain: str = Field(..., title="Domain")
    cluster_id: int = Field(..., title="Cluster Id")
    certificate_id: Optional[int] = Field(..., title="Certificate Id")
    includes: MailHostnameIncludes


class MalwareIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class MalwareResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    unix_user_id: int = Field(..., title="Unix User Id")
    name: constr(
        regex=r"^\{([A-Z]+)\}[a-zA-Z0-9-_.]+$", min_length=1, max_length=255
    ) = Field(..., title="Name")
    path: str = Field(..., title="Path")
    last_seen_at: datetime = Field(
        ..., description="Timestamp is in UTC.", title="Last Seen At"
    )
    includes: MalwareIncludes


class NodeAddOnIncludes(CoreApiModel):
    node: NodeResource
    cluster: ClusterResource


class NodeAddOnResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: int = Field(..., title="Node Id")
    product: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64) = Field(
        ...,
        description="Get available products with `GET /node-add-ons/products`.",
        title="Product",
    )
    quantity: int = Field(..., title="Quantity")
    includes: NodeAddOnIncludes


class NodeCreateRequest(CoreApiModel):
    product: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2) = Field(
        ...,
        description="Get available products with `GET /nodes/products`.",
        title="Product",
    )
    cluster_id: int = Field(..., title="Cluster Id")
    groups: List[NodeGroupEnum] = Field(
        ...,
        description="Software on this node. If multiple nodes in the same cluster have the same software (groups), that software is redundant / highly-available.\n\nOnly one node in any cluster may have these groups:\n\n* Borg\n* Elasticsearch\n* SingleStore\n* Meilisearch\n* maldet\n* Admin\n* PostgreSQL\n* Meilisearch\n\nThe following groups do not require any cluster group:\n\n* HAProxy\n* KernelCare\n* New Relic\n\nThe following groups may only be used on clusters with the Borg Client group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Borg Server group:\n\n* Borg\n\nThe following groups may only be used on clusters with the Database group:\n\n* MariaDB\n* Meilisearch\n* PostgreSQL\n* Redis\n* Grafana\n* SingleStore\n* Metabase\n* Elasticsearch\n* RabbitMQ\n\nThe following groups may only be used on clusters with the Mail group:\n\n* Dovecot\n* Admin\n\nThe following groups may only be used on clusters with the Redirect group:\n\n* Fast Redirect\n\nThe following groups may only be used on clusters with the Web group:\n\n* Apache\n* Admin\n* nginx\n* PHP\n* Passenger\n* ProFTPD\n* Composer\n* WP-CLI\n* ImageMagick\n* wkhtmltopdf\n* GNU Mailutils\n* Puppeteer\n* LibreOffice\n* Ghostscript\n* FFmpeg\n* Docker\n* maldet\n* NodeJS\n* ClamAV\n\nThe groups Composer and WP-CLI require the PHP group.\n\nThe group Puppeteer requires the NodeJS group. This group only installs the dependencies for Puppeteer; you must install the NodeJS module within your application(s).\n\nThe group KernelCare requires a KernelCare license key to be set on the cluster (`kernelcare_license_key`).\n\nFor the group ClamAV, clamd listens on port 3310. clamd can be accessed from any node in the cluster; it does not have any form of authentication.\nFind the implications on https://github.com/Cisco-Talos/clamav/issues/1169\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id` (see [Domain Routers](#tag/Domain-Routers)).\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n",
        title="Groups",
        unique_items=True,
    )
    comment: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = Field(..., title="Comment")
    load_balancer_health_checks_groups_pairs: Dict[
        NodeGroupEnum, List[NodeGroupEnum]
    ] = Field(
        ...,
        description="When health-checking the primary group (key), check health of additional groups (value). Node must have specified primary group and additional groups. The following primary groups are supported: Apache, nginx, Fast Redirect. The following additional groups are supported: MariaDB, PostgreSQL.\n\nCommon use case: when web server uses local database server, when checking web server health, check database server health.",
        title="Load Balancer Health Checks Groups Pairs",
    )


class NodeCronDependency(CoreApiModel):
    is_dependency: bool = Field(
        ...,
        description="Will the service become unavailable when this node is unreachable?",
        title="Is Dependency",
    )
    impact: Optional[str] = Field(
        ...,
        description="What impact will this node becoming unreachable have?",
        title="Impact",
    )
    reason: str = Field(
        ...,
        description="Why will the node being unreachable have impact?",
        title="Reason",
    )
    cron: CronResource


class NodeDaemonDependency(CoreApiModel):
    is_dependency: bool = Field(
        ...,
        description="Will the service become unavailable when this node is unreachable?",
        title="Is Dependency",
    )
    impact: Optional[str] = Field(
        ...,
        description="What impact will this node becoming unreachable have?",
        title="Impact",
    )
    reason: str = Field(
        ...,
        description="Why will the node being unreachable have impact?",
        title="Reason",
    )
    daemon: DaemonResource


class NodeHostsEntryDependency(CoreApiModel):
    is_dependency: bool = Field(
        ...,
        description="Will the service become unavailable when this node is unreachable?",
        title="Is Dependency",
    )
    impact: Optional[str] = Field(
        ...,
        description="What impact will this node becoming unreachable have?",
        title="Impact",
    )
    reason: str = Field(
        ...,
        description="Why will the node being unreachable have impact?",
        title="Reason",
    )
    hosts_entry: HostsEntryResource


class PassengerAppIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class PassengerAppResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    port: int = Field(..., title="Port")
    app_type: PassengerAppTypeEnum
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    app_root: str = Field(
        ..., description="Must be in UNIX user home directory.", title="App Root"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    environment: PassengerEnvironmentEnum
    environment_variables: Dict[
        constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")
    ] = Field(
        ...,
        description="Do not store secrets in them in environment variables; they are stored in plain text.",
        title="Environment Variables",
    )
    max_pool_size: int = Field(
        ...,
        description="The maximum amount of concurrent processes (also known as workers). For example, to handle 10 requests simultaneously, set this value to 10.\n\nIf you don't know what to set, set to `10`.",
        title="Max Pool Size",
    )
    max_requests: int = Field(
        ...,
        description="Each process will restart after N requests. This can prevent memory leaks.\n\nIf you don't know what to set, set to `2000`.",
        title="Max Requests",
    )
    pool_idle_time: int = Field(
        ...,
        description="Each process will be stopped after it has not received requests after N seconds. This can decrease memory usage when a busy pool (that started many processes) is no longer busy. However, if all processes are stopped, the first request takes longer as one must be started first.\n\nIf you don't know what to set, set to `10`.",
        title="Pool Idle Time",
    )
    is_namespaced: bool = Field(
        ...,
        description="Apply multiple security measures, most notably:\n\n- Dedicated special devices (`/dev/`)\n- When the cluster UNIX user home directory is `/home`, other directories are hidden. This ensures usernames of other UNIX users are not leaked.\n\nThis setting is recommended for shared environments in which users are not trusted.\n",
        title="Is Namespaced",
    )
    cpu_limit: Optional[int] = Field(..., title="Cpu Limit")
    includes: PassengerAppIncludes
    nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = Field(
        ..., title="Nodejs Version"
    )
    startup_file: Optional[str] = Field(..., title="Startup File")


class SSHKeyIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class SSHKeyResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    public_key: Optional[str] = Field(..., title="Public Key")
    private_key: Optional[str] = Field(..., title="Private Key")
    identity_file_path: Optional[str] = Field(
        ...,
        description="Path to private key if the SSH key is a private key.",
        title="Identity File Path",
    )
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    includes: SSHKeyIncludes


class VirtualHostIncludes(CoreApiModel):
    cluster: ClusterResource
    unix_user: UNIXUserResource
    fpm_pool: Optional[FPMPoolResource]
    passenger_app: Optional[PassengerAppResource]


class VirtualHostResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    unix_user_id: int = Field(..., title="Unix User Id")
    server_software_name: VirtualHostServerSoftwareNameEnum
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]] = Field(
        ..., title="Allow Override Directives"
    )
    allow_override_option_directives: Optional[
        List[AllowOverrideOptionDirectiveEnum]
    ] = Field(..., title="Allow Override Option Directives")
    domain_root: str = Field(..., title="Domain Root")
    cluster_id: int = Field(..., title="Cluster Id")
    domain: str = Field(
        ...,
        description="Unique across all virtual hosts and URL redirects. May not be the same as hostname of any node.\n\nA domain router is created for the domain.",
        title="Domain",
    )
    public_root: str = Field(
        ...,
        description="This directory is created automatically. It is also periodically scanned for CMSes which will be added to the API.\n\nThis is what you should set to a custom value for systems such as Laravel. Often to a subdirectory such as `public`.\n\nDo not confuse with document root (`document_root`), which is the directory that files will be loaded from when receiving an HTTP request.\n\nMust be inside UNIX user virtual hosts directory + specified domain (e.g. `/home/dropflix/dropflix.io/htdocs`).",
        title="Public Root",
    )
    server_aliases: List[str] = Field(
        ...,
        description="May not contain `domain`.\n\nEach server alias is unique across all virtual hosts and URL redirects.\n\nA domain router is created for every server alias.",
        title="Server Aliases",
        unique_items=True,
    )
    document_root: str = Field(
        ...,
        description="When receiving an HTTP request, files will be loaded from this directory.",
        title="Document Root",
    )
    fpm_pool_id: Optional[int] = Field(
        ...,
        description="Let the specified FPM pool handle requests to PHP files.\n\nMay not be set when Passenger app (`passenger_app_id`) is set.",
        title="Fpm Pool Id",
    )
    passenger_app_id: Optional[int] = Field(
        ...,
        description="Let the specified Passenger app handle requests.\n\nMay only be set when server software is set to nginx (`server_software_name`).\n\nMay not be set when FPM pool (`fpm_pool_id`) is set.",
        title="Passenger App Id",
    )
    custom_config: Optional[
        constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    ] = Field(
        ...,
        description="Include custom config snippets using the syntax `{{ custom_config_snippets.name }}`.\n\nReplace `name` with the name of the custom config snippet.\n\nDefault custom config snippets (`is_default`) are inserted after the virtual host specific custom config. To place a default custom config snippet earlier, include it manually in the virtual host specific custom config.\n\nWhen the server software nginx is used, custom configs are added to the `server` context.\n\nIf the virtual host has basic authentication realms, the `auth_basic` and `auth_basic_user_file` directives may not be set in the default context.\n",
        title="Custom Config",
    )
    includes: VirtualHostIncludes


class BasicAuthenticationRealmIncludes(CoreApiModel):
    htpasswd_file: HtpasswdFileResource
    virtual_host: VirtualHostResource
    cluster: ClusterResource


class BasicAuthenticationRealmResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    directory_path: Optional[str] = Field(
        ...,
        description="Specify null for entire virtual host document root. If the specified virtual host uses the server software Apache, must be in its domain root (`domain_root`).",
        title="Directory Path",
    )
    virtual_host_id: int = Field(
        ...,
        description="Must have same UNIX user as specified htpasswd file.",
        title="Virtual Host Id",
    )
    name: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    htpasswd_file_id: int = Field(
        ...,
        description="Must have same UNIX user as specified virtual host.",
        title="Htpasswd File Id",
    )
    includes: BasicAuthenticationRealmIncludes


class BorgArchiveIncludes(CoreApiModel):
    borg_repository: BorgRepositoryResource
    cluster: ClusterResource
    unix_user: Optional[UNIXUserResource]
    database: Optional[DatabaseResource]


class BorgArchiveResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    database_id: Optional[int] = Field(..., title="Database Id")
    unix_user_id: Optional[int] = Field(..., title="Unix User Id")
    cluster_id: int = Field(..., title="Cluster Id")
    borg_repository_id: int = Field(..., title="Borg Repository Id")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    includes: BorgArchiveIncludes


class CMSIncludes(CoreApiModel):
    virtual_host: VirtualHostResource
    cluster: ClusterResource


class CMSResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    software_name: CMSSoftwareNameEnum
    is_manually_created: bool = Field(
        ...,
        description="Value is `false` when CMS was detected automatically. Must be set to `true` in other cases.",
        title="Is Manually Created",
    )
    virtual_host_id: int = Field(..., title="Virtual Host Id")
    includes: CMSIncludes


class CertificateManagerIncludes(CoreApiModel):
    certificate: Optional[CertificateResource]
    cluster: ClusterResource


class CertificateManagerResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    main_common_name: str = Field(..., title="Main Common Name")
    certificate_id: Optional[int] = Field(..., title="Certificate Id")
    last_request_task_collection_uuid: Optional[UUID4] = Field(
        ..., title="Last Request Task Collection Uuid"
    )
    common_names: List[str] = Field(
        ...,
        description="May not contain wildcard domains.\n\nEach common name is unique across all certificate managers.",
        min_items=1,
        title="Common Names",
        unique_items=True,
    )
    provider_name: CertificateProviderNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    request_callback_url: Optional[AnyUrl] = Field(..., title="Request Callback Url")
    includes: CertificateManagerIncludes


class DomainRouterIncludes(CoreApiModel):
    virtual_host: Optional[VirtualHostResource]
    url_redirect: Optional[URLRedirectResource]
    node: Optional[NodeResource]
    certificate: Optional[CertificateResource]
    security_txt_policy: Optional[SecurityTXTPolicyResource]
    cluster: ClusterResource


class DomainRouterResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    domain: str = Field(..., title="Domain")
    virtual_host_id: Optional[int] = Field(
        ...,
        description="May only be set when `category` is `Virtual Host`.",
        title="Virtual Host Id",
    )
    url_redirect_id: Optional[int] = Field(
        ...,
        description="May only be set when `category` is `URL Redirect`.",
        title="Url Redirect Id",
    )
    category: DomainRouterCategoryEnum
    cluster_id: int = Field(..., title="Cluster Id")
    node_id: Optional[int] = Field(
        ...,
        description="\nWhen set, traffic is routed to the specified node rather than load-balanced over all available nodes (default). This prevents resources (such as FPM pools) from being active on multiple nodes, which can decrease costs.\n\nIf the node is unavailable, traffic is failed over to another node.\n\nIf a node with the Admin group also has group(s) that are load-balanced (such as Apache or nginx), the node is not used for domain routers for which it is not explicitly configured by being set as `node_id`.\nThis allows you to use the Admin node for specific domain routers, e.g. second-tier applications such as serving assets to a CDN, while it is not used for regular traffic.\n",
        title="Node Id",
    )
    certificate_id: Optional[int] = Field(..., title="Certificate Id")
    security_txt_policy_id: Optional[int] = Field(..., title="Security Txt Policy Id")
    firewall_groups_ids: Optional[List[int]] = Field(
        ...,
        description="Only IP networks in the specified firewall groups may access this domain router.\n\nIf this is null, all IP networks may.",
        title="Firewall Groups Ids",
    )
    force_ssl: bool = Field(..., title="Force Ssl")
    includes: DomainRouterIncludes


class MailAccountIncludes(CoreApiModel):
    mail_domain: MailDomainResource
    cluster: ClusterResource


class MailAccountResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255) = Field(
        ..., title="Password"
    )
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail alias in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    cluster_id: int = Field(..., title="Cluster Id")
    quota: Optional[int] = Field(
        ...,
        description="When the quota has been reached, emails will be bounced.\n\nIn MB.",
        title="Quota",
    )
    includes: MailAccountIncludes


class MailAliasIncludes(CoreApiModel):
    mail_domain: MailDomainResource
    cluster: ClusterResource


class MailAliasResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    cluster_id: int = Field(..., title="Cluster Id")
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail account in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    forward_email_addresses: List[EmailStr] = Field(
        ..., min_items=1, title="Forward Email Addresses", unique_items=True
    )
    includes: MailAliasIncludes


class NodeDomainRouterDependency(CoreApiModel):
    is_dependency: bool = Field(
        ...,
        description="Will the service become unavailable when this node is unreachable?",
        title="Is Dependency",
    )
    impact: Optional[str] = Field(
        ...,
        description="What impact will this node becoming unreachable have?",
        title="Impact",
    )
    reason: str = Field(
        ...,
        description="Why will the node being unreachable have impact?",
        title="Reason",
    )
    domain_router: DomainRouterResource


class TombstoneDataCertificateIncludes(BaseModel):
    pass


class TombstoneDataDaemonIncludes(BaseModel):
    pass


class TombstoneDataDatabaseIncludes(BaseModel):
    pass


class TombstoneDataFPMPoolIncludes(BaseModel):
    pass


class TombstoneDataPassengerAppIncludes(BaseModel):
    pass


class TombstoneDataRedisInstanceIncludes(BaseModel):
    pass


class TombstoneDataUNIXUserIncludes(BaseModel):
    pass


class TombstoneDataUNIXUserRabbitMQCredentialsIncludes(BaseModel):
    pass


class TombstoneDataVirtualHostIncludes(BaseModel):
    pass


class TombstoneDataDatabaseUserIncludes(BaseModel):
    pass


class TombstoneDataDomainRouterIncludes(BaseModel):
    pass


class TombstoneDataRootSSHKeyIncludes(BaseModel):
    pass


class TombstoneDataSSHKeyIncludes(BaseModel):
    pass


class TombstoneDataMailHostnameIncludes(BaseModel):
    pass


class TombstoneDataCustomConfigIncludes(BaseModel):
    pass


class TombstoneDataDatabaseUser(BaseModel):
    data_type: Literal["database_user"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    host: Optional[HostEnum]
    server_software_name: DatabaseServerSoftwareNameEnum
    includes: TombstoneDataDatabaseUserIncludes


class TombstoneDataDatabase(CoreApiModel):
    data_type: Literal["database"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63) = Field(
        ..., title="Name"
    )
    server_software_name: DatabaseServerSoftwareNameEnum
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataDatabaseIncludes


class TombstoneDataDatabaseUserGrantIncludes(BaseModel):
    database: Union[DatabaseResource, TombstoneDataDatabase] = Field(
        ..., title="Database"
    )
    database_user: Union[DatabaseUserResource, TombstoneDataDatabaseUser] = Field(
        ..., title="Database User"
    )


class TombstoneDataDatabaseUserGrant(BaseModel):
    data_type: Literal["database_user_grant"] = Field(..., title="Data Type")
    table_name: Optional[
        constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    ] = Field(..., title="Table Name")
    privilege_name: MariaDBPrivilegeEnum
    database_id: int = Field(..., title="Database Id")
    database_user_id: int = Field(..., title="Database User Id")
    includes: TombstoneDataDatabaseUserGrantIncludes


class TombstoneDataDomainRouter(BaseModel):
    data_type: Literal["domain_router"] = Field(..., title="Data Type")
    domain: str = Field(..., title="Domain")
    includes: TombstoneDataDomainRouterIncludes


class TombstoneDataRootSSHKey(BaseModel):
    data_type: Literal["root_ssh_key"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    is_private_key: bool = Field(..., title="Is Private Key")
    includes: TombstoneDataRootSSHKeyIncludes


class TombstoneDataSSHKey(BaseModel):
    data_type: Literal["ssh_key"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    identity_file_path: Optional[str] = Field(..., title="Identity File Path")
    includes: TombstoneDataSSHKeyIncludes


class TombstoneDataMailHostname(BaseModel):
    data_type: Literal["mail_hostname"] = Field(..., title="Data Type")
    domain: str = Field(..., title="Domain")
    includes: TombstoneDataMailHostnameIncludes


class TombstoneDataCertificate(CoreApiModel):
    data_type: Literal["certificate"] = Field(..., title="Data Type")
    includes: TombstoneDataCertificateIncludes


class TombstoneDataDaemon(CoreApiModel):
    data_type: Literal["daemon"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    nodes_ids: List[int] = Field(..., min_items=1, title="Nodes Ids", unique_items=True)
    includes: TombstoneDataDaemonIncludes


class TombstoneDataFPMPool(CoreApiModel):
    data_type: Literal["fpm_pool"] = Field(..., title="Data Type")
    version: str = Field(..., title="Version")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    includes: TombstoneDataFPMPoolIncludes


class TombstoneDataPassengerApp(CoreApiModel):
    data_type: Literal["passenger_app"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    app_root: str = Field(..., title="App Root")
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataPassengerAppIncludes


class TombstoneDataRedisInstance(CoreApiModel):
    data_type: Literal["redis_instance"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataRedisInstanceIncludes


class TombstoneDataUNIXUser(CoreApiModel):
    data_type: Literal["unix_user"] = Field(..., title="Data Type")
    home_directory: str = Field(..., title="Home Directory")
    mail_domains_directory: Optional[str] = Field(..., title="Mail Domains Directory")
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataUNIXUserIncludes


class TombstoneDataCronIncludes(BaseModel):
    node: NodeResource
    unix_user: Union[TombstoneDataUNIXUser, UNIXUserResource] = Field(
        ..., title="Unix User"
    )


class TombstoneDataHtpasswdFileIncludes(BaseModel):
    unix_user: Union[UNIXUserResource, TombstoneDataUNIXUser] = Field(
        ..., title="Unix User"
    )


class TombstoneDataHtpasswdFile(BaseModel):
    data_type: Literal["htpasswd_file"] = Field(..., title="Data Type")
    unix_user_id: int = Field(..., title="Unix User Id")
    includes: TombstoneDataHtpasswdFileIncludes


class TombstoneDataMailDomainIncludes(BaseModel):
    unix_user: Union[UNIXUserResource, TombstoneDataUNIXUser] = Field(
        ..., title="Unix User"
    )


class TombstoneDataMailDomain(BaseModel):
    data_type: Literal["mail_domain"] = Field(..., title="Data Type")
    domain: str = Field(..., title="Domain")
    unix_user_id: int = Field(..., title="Unix User Id")
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataMailDomainIncludes


class TombstoneDataMailAccountIncludes(BaseModel):
    mail_domain: Union[MailDomainResource, TombstoneDataMailDomain] = Field(
        ..., title="Mail Domain"
    )


class TombstoneDataMailAccount(CoreApiModel):
    data_type: Literal["mail_account"] = Field(..., title="Data Type")
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64) = Field(
        ...,
        description="May not be in use by mail alias in the same mail domain.",
        title="Local Part",
    )
    mail_domain_id: int = Field(..., title="Mail Domain Id")
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataMailAccountIncludes


class TombstoneDataCron(CoreApiModel):
    data_type: Literal["cron"] = Field(..., title="Data Type")
    node_id: int = Field(..., title="Node Id")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64) = Field(
        ..., title="Name"
    )
    unix_user_id: int = Field(..., title="Unix User Id")
    includes: TombstoneDataCronIncludes


class TombstoneDataUNIXUserRabbitMQCredentials(CoreApiModel):
    data_type: Literal["unix_user_rabbitmq_credentials"] = Field(..., title="Data Type")
    rabbitmq_virtual_host_name: constr(
        regex=r"^[a-z0-9-.]+$", min_length=1, max_length=32
    ) = Field(..., title="Rabbitmq Virtual Host Name")
    includes: TombstoneDataUNIXUserRabbitMQCredentialsIncludes


class TombstoneDataVirtualHost(CoreApiModel):
    data_type: Literal["virtual_host"] = Field(..., title="Data Type")
    domain_root: str = Field(..., title="Domain Root")
    delete_on_cluster: Optional[bool] = Field(False, title="Delete On Cluster")
    includes: TombstoneDataVirtualHostIncludes


class TombstoneDataCustomConfig(CoreApiModel):
    data_type: Literal["custom_config"] = Field(..., title="Data Type")
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128) = Field(
        ..., title="Name"
    )
    includes: TombstoneDataCustomConfigIncludes


class TombstoneIncludes(CoreApiModel):
    cluster: ClusterResource


class TombstoneResource(CoreApiModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    data: Union[
        TombstoneDataPassengerApp,
        TombstoneDataCertificate,
        TombstoneDataFPMPool,
        TombstoneDataUNIXUserRabbitMQCredentials,
        TombstoneDataUNIXUser,
        TombstoneDataCron,
        TombstoneDataDaemon,
        TombstoneDataDatabase,
        TombstoneDataMailAccount,
        TombstoneDataRedisInstance,
        TombstoneDataVirtualHost,
        TombstoneDataDatabaseUser,
        TombstoneDataDatabaseUserGrant,
        TombstoneDataDomainRouter,
        TombstoneDataHtpasswdFile,
        TombstoneDataRootSSHKey,
        TombstoneDataSSHKey,
        TombstoneDataMailDomain,
        TombstoneDataMailHostname,
        TombstoneDataCustomConfig,
    ] = Field(..., discriminator="data_type", title="Data")
    object_id: int = Field(..., title="Object Id")
    object_model_name: ObjectModelNameEnum
    cluster_id: int = Field(..., title="Cluster Id")
    includes: TombstoneIncludes


class NodeDependenciesResource(CoreApiModel):
    hostname: str = Field(..., title="Hostname")
    groups: List[NodeGroupDependency] = Field(..., title="Groups")
    domain_routers: List[NodeDomainRouterDependency] = Field(
        ..., title="Domain Routers"
    )
    daemons: List[NodeDaemonDependency] = Field(..., title="Daemons")
    crons: List[NodeCronDependency] = Field(..., title="Crons")
    hosts_entries: List[NodeHostsEntryDependency] = Field(..., title="Hosts Entries")


class DaemonLogResource(BaseModel):
    application_name: constr(min_length=1, max_length=65535) = Field(
        ..., title="Application Name"
    )
    priority: int = Field(..., title="Priority")
    pid: int = Field(..., title="Pid")
    message: constr(min_length=1, max_length=65535) = Field(..., title="Message")
    node_hostname: str = Field(..., title="Node Hostname")
    timestamp: datetime = Field(..., title="Timestamp")


class NodeSpecificationsResource(BaseModel):
    hostname: str = Field(..., title="Hostname")
    memory_mib: int = Field(..., title="Memory Mib")
    cpu_cores: int = Field(..., title="Cpu Cores")
    disk_gib: int = Field(..., title="Disk Gib")
    usable_cpu_cores: int = Field(..., title="Usable Cpu Cores")
    usable_memory_mib: int = Field(..., title="Usable Memory Mib")
    usable_disk_gib: int = Field(..., title="Usable Disk Gib")


class RequestLogIncludes(BaseModel):
    pass


class RequestLogResource(BaseModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    ip_address: str = Field(..., title="Ip Address")
    path: str = Field(..., title="Path")
    method: HTTPMethod
    query_parameters: Dict[str, str] = Field(..., title="Query Parameters")
    body: Any = Field(
        ...,
        description="JSON body if specified and valid on request. Null if no JSON specified, or invalid.",
        title="Body",
    )
    api_user_id: int = Field(..., title="Api User Id")
    request_id: UUID4 = Field(..., title="Request Id")
    includes: Optional[RequestLogIncludes] = None


class ObjectLogIncludes(BaseModel):
    customer: Optional[CustomerResource]


class ObjectLogResource(BaseModel):
    id: int = Field(..., title="Id")
    created_at: datetime = Field(..., title="Created At")
    updated_at: datetime = Field(..., title="Updated At")
    object_id: int = Field(..., title="Object Id")
    object_model_name: Optional[
        constr(regex=r"^[a-zA-Z]+$", min_length=1, max_length=255)
    ] = Field(..., title="Object Model Name")
    request_id: Optional[UUID4] = Field(..., title="Request Id")
    type: ObjectLogTypeEnum
    causer_type: Optional[CauserTypeEnum]
    causer_id: Optional[int] = Field(..., title="Causer Id")
    customer_id: Optional[int] = Field(..., title="Customer Id")
    includes: Optional[ObjectLogIncludes] = None


NestedPathsDict.update_forward_refs()
