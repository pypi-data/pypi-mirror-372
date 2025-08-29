import os

import consul

from ai_app.utils import PydanticForbidExtra, disable_urllib_insecure_request_warning


class ConsulKeyValue(PydanticForbidExtra):
    host: str
    key: str
    token: str | None = None
    scheme: str = "https"
    port: int = 443
    verify: bool = False

    @classmethod
    def from_env_variables(cls):
        host = os.environ["CONSUL_HOST"]
        key = os.environ["CONSUL_KEY"]
        token = os.environ.get("CONSUL_TOKEN")
        consul_key_value = cls(host=host, token=token, key=key)
        return consul_key_value

    def model_post_init(self, _context) -> None:
        if not self.verify:
            disable_urllib_insecure_request_warning()

    def get_client(self):
        client = consul.Consul(
            host=self.host,
            port=self.port,
            token=self.token,
            scheme=self.scheme,
            verify=self.verify,
        )
        return client

    def load(self) -> bytes:
        client = self.get_client()
        index, data = client.kv.get(self.key)
        value = data["Value"]
        return value

    def save(self, value: str | bytes) -> None:
        client = self.get_client()
        client.kv.put(self.key, value)
