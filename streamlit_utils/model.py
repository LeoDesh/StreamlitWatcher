from dataclasses import dataclass


@dataclass
class GridConfig:
    columns: int
    has_border: bool = True
    height: int | str = "content"
    gap: str = "xsmall"
