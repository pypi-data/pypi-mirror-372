import sys
from rich.live import Live
from rich.spinner import Spinner
from analyst_klondike.features.data_context.arg_file_load.arg_load import (
    TooManyArgumentsException,
    process_args
)
from analyst_klondike.ui.runner_app import get_app


def analyst_klondike():

    spinner = Spinner("dots", text="App is loading...")
    with Live(spinner, screen=True, refresh_per_second=10) as live:

        # clear console with spinner
        def _clear_console():
            live.console.clear()

        try:
            app = get_app()
            app.on_mounted_callback = _clear_console
            process_args(sys.argv)
            app.run()
        except (FileNotFoundError, TooManyArgumentsException) as err:
            live.console.print(err)
            sys.exit(1)


if __name__ == "__main__":
    analyst_klondike()
