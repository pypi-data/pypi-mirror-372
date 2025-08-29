from typing import Any, Dict


class XteaError(Exception):
    def __init__(self, massage: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super(*args, **kwargs)
        self.message = massage


class AesError(Exception):
    def __init__(self, massage: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super(*args, **kwargs)
        self.message = massage


class KuznechikError(Exception):
    def __init__(self, massage: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
        super(*args, **kwargs)
        self.message = massage
