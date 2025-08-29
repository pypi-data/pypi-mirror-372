from dataclasses import dataclass


@dataclass
class CallException(Exception):
    body: str
    status_code: int


@dataclass
class AuthenticationException(Exception):
    body: str
    status_code: int
