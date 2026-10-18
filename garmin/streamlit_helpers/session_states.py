from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

import streamlit as st


class ChartEvents(StrEnum):
    STEPS_DIALOG = auto()
    DISTANCE_DIALOG = auto()
    PACE_RANGE_DIALOG = auto()
    DISTANCE_RANGE_DIALOG = auto()


@dataclass
class ChartEventState:
    value: Any | None = None
    counter: int = 0

    def reset_event(self) -> None:
        self.counter += 1


def set_event_state(event: str, value: Any | None = None) -> None:
    if event not in st.session_state:
        st.session_state[event] = ChartEventState()
    else:
        st.session_state[event].value = value


def reset_event_state(event: str) -> None:
    st.session_state[event].reset_event()


def get_event_state(event: str) -> Any:
    return st.session_state[event].value


def get_event_chart_name(event: str) -> str:
    chart_event = st.session_state[event]
    return f"{event}_chart_{chart_event.counter}"
