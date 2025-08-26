import enum


class MethodType(enum.Enum):
    METHOD = 0
    CONSTRUCTOR = 1
    PROPERTY = 2


class Statement(enum.Enum):
    SINGLELINE = 0
    MULTILINE = 1
