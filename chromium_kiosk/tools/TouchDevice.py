import dataclasses


@dataclasses.dataclass
class TouchDevice:
    name: bytes
    identifier: str
