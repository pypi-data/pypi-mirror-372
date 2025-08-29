import datetime
from json import JSONEncoder
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID


class CustomEncoder(JSONEncoder):
    def default(self, o: Any) -> str:
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        elif isinstance(o, (IPv6Address, IPv4Address, UUID)):
            return str(o)

        return super().default(o)
