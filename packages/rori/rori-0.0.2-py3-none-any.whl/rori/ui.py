from functools import reduce
from importlib.metadata import version
from typing import Optional

import questionary
from questionary import Style
from rich import box
from rich.console import Console, ConsoleOptions, Group, RenderableType
from rich.measure import measure_renderables
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from rori import config
from rori.models import Rori, Status

FZF_STYLE = Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # token in front of the question
        # Main question/prompt
        ("question", "bold"),
        ("instruction", "italic fg:#666666"),
        # Selected item (highlighted)
        ("selected", "fg:#ffffff bg:#005577 bold"),
        # Pointer/cursor (similar to fzf's >)
        ("pointer", "fg:#005577 bold"),
        # Normal items
        ("", "fg:#cccccc"),
        # Answer (what was selected)
        ("answer", "fg:#00aa00 bold"),
        # Disabled items
        ("disabled", "italic fg:#666666"),
        # Text input
        ("text", "fg:#ffffff"),
        # Fuzzy search match highlighting
        ("fuzzy-match", "fg:#ffff00 bold"),
        # Validation errors
        ("validation-error", "fg:#ff0000 bold"),
        ("separator", "fg:#cc5454"),  # separator in lists
    ]
)


def get_color(status: Status) -> str:
    STATUS_COLORS = {
        Status.ACTIVE: "#4aad52",
        # Status.ACTIVE: config.COLOR_ACCENT,
        Status.BACKOFF: "#f79824",
        Status.INACTIVE: "",
        Status.ERROR: config.COLOR_ERROR,
    }

    return STATUS_COLORS[status]


console = Console(highlight=False)


class ConsoleUI:
    def __init__(self):
        self.console = Console(highlight=False)

    def print(self, *args, **kwargs):
        return self.console.print(*args, **kwargs)

    def error(self, message: str):
        return self.console.print(
            f"{config.ICON_ERROR} {message}",
            style=f"{config.COLOR_ERROR} bold",
            overflow="ignore",
            crop=False,
        )

    def handle_errors(self, errors: list[str]):
        for message in errors:
            self.console.print(
                f"{config.ICON_MULTI_ERROR} {message}",
                overflow="ignore",
                crop=False,
            )

    def info(self, message: str):
        return self.console.print(
            f"{config.ICON_INFO} {message}",
            style=f"{config.COLOR_ACCENT} bold",
            overflow="ignore",
            crop=False,
        )

    def render_all(self, roris: list[Rori], verbose: bool = False) -> RenderableType:
        package_version = version(__package__)

        user_roris = [rori for rori in roris if not rori.is_system]
        if not roris or not user_roris and not verbose:
            return Text(
                f"{config.ICON_INFO} nothing is there yet",
                style=f"{config.COLOR_ACCENT} bold",
            )

        active_count = reduce(
            lambda acc, rori: acc + (1 if rori.status == Status.ACTIVE else 0),
            user_roris,
            0,
        )

        table = Table(
            show_header=True,
            header_style=f"{config.COLOR_MAIN} bold",
            box=box.ROUNDED,
            caption_style="dim",
            caption_justify="right",
        )
        table.add_column("#", style="dim", min_width=2)
        table.add_column("name")
        table.add_column("port from")
        table.add_column("port to")
        table.add_column("status")
        table.add_column("type")
        if active_count:
            table.add_column("uptime", justify="right")

        for rori in roris:
            if rori.is_system and not verbose:
                continue
            status_text = get_status_text(rori)
            port_text = get_port_text(rori)
            row = [
                f"{rori.hid}",
                f"{rori.name}",
                f"{rori.port_from}" if rori.port_from else "-",
                port_text if rori.port_to else "-",
                status_text,
                f"{rori.type_}",
            ]
            if active_count:
                row.append(f"{rori.uptime}")
            style = "dim" if rori.status == Status.INACTIVE or rori.is_system else ""
            table.add_row(*row, style=style)

        if verbose:
            table.title = f"{config.ICON_RORI} rori, {package_version}"
            table.caption = f"{active_count} active / {len(user_roris)} total"

        return table

    def render_one(self, rori: Rori, verbose: bool = False) -> RenderableType:
        column_min_width = 12
        table_min_width = 40
        status_table = Table(
            show_header=False,
            show_footer=False,
            expand=True,
            width=48,
            box=None,
        )
        status_table.add_column("lefside", justify="right", style="dim")
        status_table.add_column("rightside", justify="left")

        status_text = get_status_text(rori)
        color = get_color(rori.status)
        status_table.add_row("name", f"{rori.name}")
        status_table.add_row(
            "status", Text(f"{config.ICON_STATUS} {rori.status}", style=f"bold {color}")
        )
        if rori.status == Status.ACTIVE:
            status_table.add_row("uptime", f"{rori.uptime}")

        status_table.add_row("")
        status_table.add_row("port from", f"{rori.port_from}")
        status_table.add_row("port to", f"{rori.port_to}")
        status_table.add_row("")

        if not verbose:
            status_table.add_row("type", Text(f"{rori.type_}"))

        if verbose:
            status_table.add_row(
                "command", Text(f"{rori.command}", style=f"{config.COLOR_ACCENT} bold")
            )
            if rori.status == Status.ACTIVE:
                status_table.add_row("pid", f"{rori.pid}")
                status_table.add_row("restarts", f"{rori.restarts}")
            status_table.add_row("")
            status_table.add_row("logs", Text(f"{rori.logfile}"))

        status_panel = Panel(
            status_table,
            expand=False,
            # min_width=panel_width,
            title=f"rori {config.ICON_RORI} {rori.hid}",
            border_style=config.COLOR_MAIN,
        )
        result = Group(status_panel)

        if verbose and rori.metadata is not None:
            info_table = Table(
                show_header=False,
                show_footer=False,
                expand=True,
                box=None,
                # min_width=panel_width,
            )
            info_table.add_column(
                "leftside", justify="right", style="dim", min_width=column_min_width
            )
            info_table.add_column(
                "rightside", justify="left", style=config.COLOR_ACCENT
            )

            for key, value in rori.metadata.items():
                info_table.add_row(key, Text(value, overflow="fold"))

            info_panel = Panel(
                info_table,
                expand=False,
                # width=panel_width,
                title=f"{rori.type_} info",
                # border_style=config.COLOR_MAIN,
            )
            result = Group(status_panel, info_panel)
            # options = ConsoleOptions()
            measure = measure_renderables(
                console=console,
                options=console.options,
                renderables=[status_panel, info_panel],
            )
            if verbose:
                status_table.width = measure.maximum
                info_table.width = measure.maximum

        return result


def get_status_text(entry: Rori):
    status: Status = entry.status
    status_text = Text()
    status_text.append(config.ICON_STATUS, style=get_color(status))
    status_text.append(f" {status}", style=get_color(status))
    return status_text


def get_port_text(entry: Rori):
    style = ""
    match entry.status:
        case Status.ACTIVE:
            style = f"bold {get_color(entry.status)}"
        case Status.ERROR:
            style = f"{get_color(entry.status)}"

    return Text(f"{entry.port_to}", style=style)


def fzf_select_from_choices(
    message: str, choices: list[questionary.Choice], allow_quit: bool = True
) -> Optional[str]:
    """FZF-like selection with questionary.Choice objects."""
    try:
        result = questionary.select(
            message,
            choices=choices,
            style=FZF_STYLE,
            qmark="> ",
            # Enable keyboard shortcuts and navigation
            use_shortcuts=False,
            use_arrow_keys=True,
            use_jk_keys=True,  # vim-like j/k navigation
            use_emacs_keys=False,
            # Show instruction
            instruction=" (↑↓/jk to navigate, Enter to select"
            + (", q/Esc to quit" if allow_quit else "")
            + ")",
        ).ask()

        return result
    except (KeyboardInterrupt, EOFError):
        pass
