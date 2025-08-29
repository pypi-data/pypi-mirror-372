from typing import Optional


class DataGatewayError(Exception):
    def __init__(self, message: str, error: Optional[Exception] = None) -> None:
        super().__init__(f'{message}. {error}' if error else message)
        self.error = error


class DataGatewayDecryptError(DataGatewayError):
    pass


class DataGatewayDeviceProtocolParsingError(DataGatewayError):
    pass


class DataGatewayBSProtocolParsingError(DataGatewayError):
    pass
