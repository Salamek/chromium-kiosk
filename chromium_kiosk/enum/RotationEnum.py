import enum


@enum.unique
class RotationEnum(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    NORMAL = "normal"
    INVERTED = "inverted"
