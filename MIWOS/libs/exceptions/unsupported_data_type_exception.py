from MIWOS.libs.exceptions.MIWOS_exception import MIWOSException


class UnsupportedDataTypeException(MIWOSException):
    def __init__(self, data_type: str):
        super().__init__(f"Unsupported data type: {data_type}")
