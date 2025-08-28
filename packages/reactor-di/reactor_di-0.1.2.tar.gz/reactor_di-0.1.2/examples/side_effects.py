from functools import cached_property

from reactor_di import CachingStrategy, law_of_demeter, module


class ConnectionConfig:
    url_access = 0

    @cached_property
    def url(self) -> str:
        ConnectionConfig.url_access += 1
        return "schema://authority/path?query=value#fragment"


@law_of_demeter("_config")
class ConnectionManager:
    _config: ConnectionConfig
    _url: str  # from _config

    def __init__(self):
        self.connections = 0

    def connect(self) -> str:
        self.connections += 1
        return self._url


@module(CachingStrategy.NOT_THREAD_SAFE)
@law_of_demeter("manager", prefix="")
class ConnectionApp:
    config: ConnectionConfig
    manager: ConnectionManager
    connections: int  # from manager

    def connect(self) -> str:
        return self.manager.connect()


def test_side_effects():
    """Test that side effects are properly handled."""

    app = ConnectionApp()
    assert app.connections == 0
    assert ConnectionConfig.url_access == 0

    assert app.connect() == "schema://authority/path?query=value#fragment"
    assert app.connections == 1
    assert ConnectionConfig.url_access == 1

    assert app.connect() == "schema://authority/path?query=value#fragment"
    assert app.connections == 2
    assert ConnectionConfig.url_access == 1
