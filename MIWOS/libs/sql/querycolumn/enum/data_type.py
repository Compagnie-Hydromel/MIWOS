from enum import Enum


class DataType(Enum):
    PRIMARY_KEY = 0
    INT = 1
    FLOAT = 2
    STRING = 3
    BOOLEAN = 4
    DATE = 5
    DATETIME = 6
    REFERENCES = 7
    TIMESTAMP = 8
