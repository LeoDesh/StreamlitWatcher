from dataclasses import asdict, dataclass
from typing import Any

import streamlit as st

from garmin.utils.misc import prettify


@dataclass
class Metric:
    label: str
    value: Any
    delta: Any | None = None
    help: str | None = None

    def render_metric(self) -> None:
        return st.metric(**asdict(self))


def stream_metrics(
    metrics: list[Metric], *, num_cols: int = 4, border: bool = False
) -> None:
    with st.container(border=border):
        cols = st.columns(num_cols)
        for idx, metric in enumerate(metrics):
            col_idx = idx % num_cols
            with cols[col_idx]:
                metric.render_metric()


def create_metrics_container(header: str, activites: dict[str, str]) -> None:
    with st.container(border=True, horizontal_alignment="center"):
        st.header(header)
        metrics = [
            Metric(label=prettify(label), value=value)
            for label, value in activites.items()
        ]
        stream_metrics(metrics, num_cols=len(metrics))
