import sys

from garmin.jobs import run_scheduler, run_worker
from garmin.streamlit_helpers.nagivation import (
    define_sidebar,
    get_navigation,
    render_logo,
)


def run_app() -> None:
    render_logo()
    define_sidebar()
    nav = get_navigation()
    nav.run()


def main():

    mode = sys.argv[1] if len(sys.argv) > 1 else "streamlit"
    match mode:
        case "streamlit":
            run_app()
        case "worker":
            run_worker()
        case "schedule":
            run_scheduler()
        case _:
            raise ValueError(f"Unknown application mode: {mode}")


if __name__ == "__main__":
    main()
