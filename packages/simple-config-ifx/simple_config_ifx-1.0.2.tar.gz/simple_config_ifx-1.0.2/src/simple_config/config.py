from typing import Any


class ConfigSection:
    def __init__(self, conf_section: dict):
        self._conf = conf_section

        for key, item in self._conf.items():
            if isinstance(item, dict):
                self._conf[key] = ConfigSection(item)

    def __getitem__(self, key: str) -> Any:
        value = self._conf
        for key_item in key.split(":"):
            value = value[key_item]
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(value, dict):
            value = ConfigSection(value)
        self._conf[key] = value

    def __str__(self) -> str:
        return str(self._conf)

    def __repr__(self) -> str:
        return repr(self._conf)

    def keys(self):
        return self._conf.keys()

    def values(self):
        return self._conf.values()

    def items(self):
        return self._conf.items()


class Configuration(ConfigSection):
    pass


__all__ = ["Configuration"]
