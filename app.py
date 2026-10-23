import sys

from garmin.streamlit_helpers.nagivation import (
    define_sidebar,
    get_navigation,
    render_logo,
)
from jobs import run_scheduler, run_worker


def run_app() -> None:
    render_logo()
    define_sidebar()
    nav = get_navigation()
    nav.run()


def main():

    mode = sys.argv[1] if len(sys.argv) > 1 else "streamlit"

    if mode == "streamlit":
        run_app()

    elif mode == "worker":
        run_worker()

    elif mode == "schedule":
        run_scheduler()

    else:
        raise ValueError(f"Unknown application mode: {mode}")


if __name__ == "__main__":
    main()

main()
