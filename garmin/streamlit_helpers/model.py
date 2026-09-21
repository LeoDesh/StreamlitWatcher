from dataclasses import asdict, dataclass
from typing import Any, Self

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from garmin.utils.misc import prettify


@dataclass
class GridConfig:
    columns: int
    has_border: bool = True
    height: int | str = "content"
    gap: str = "xsmall"


def create_grid(grid_config: list[GridConfig]) -> list[list[DeltaGenerator]]:
    grid_layout = []
    for config in grid_config:
        cols_config = st.columns(config.columns, gap=config.gap)
        containers = [
            col.container(border=config.has_border, height=config.height)
            for col in cols_config
        ]
        grid_layout.append(containers)
    return grid_layout


@dataclass
class Metric:
    label: str
    value: Any
    delta: Any | None = None
    help: str | None = None

    def render_metric(self) -> None:
        return st.metric(**asdict(self))

    @classmethod
    def create_from_dict(cls, data: dict[str, str]) -> list[Self]:
        return [cls(label=prettify(key), value=value) for key, value in data.items()]


def stream_metrics(
    metrics: list[Metric], *, num_cols: int = 4, border: bool = False
) -> None:
    with st.container(border=border):
        cols = st.columns(num_cols)
        for idx, metric in enumerate(metrics):
            col_idx = idx % num_cols
            with cols[col_idx]:
                metric.render_metric()


def create_metrics_container(header: str, data: dict[str, str]) -> None:
    with st.container(border=True, horizontal_alignment="center"):
        st.header(header)
        metrics = Metric.create_from_dict(data)
        stream_metrics(metrics, num_cols=len(metrics))
