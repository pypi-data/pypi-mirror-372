import sys
from typing import Optional, TypedDict, Unpack

import click
import questionary

from rori.cli_utils import (
    AliasedGroup,
    handle_rori_errors,
    interactive_option,
    k8s_options,
    name_option,
    rori_manager,
    ssh_options,
    ui,
)
from rori.command import CommandK8s, CommandSsh
from rori.models import EntryTypes, Rori, RoriError
from rori.ui import fzf_select_from_choices


@click.group(invoke_without_command=True, cls=AliasedGroup)
@click.version_option(message="rori, version %(version)s")
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.pass_context
@handle_rori_errors
def cli(
    ctx,
    verbose: bool,
) -> None:
    if ctx.invoked_subcommand is None:
        _status(None, verbose=verbose)


@cli.command(short_help="show information about managed configurations")
@click.argument("rori_alias", metavar="rori", required=False)
@click.option("-v", "--verbose", is_flag=True, default=False)
@handle_rori_errors
def status(
    rori_alias: Optional[str],
    verbose: bool,
) -> None:
    _status(rori_alias, verbose)


def _status(
    rori_alias: Optional[str] = None,
    verbose: bool = False,
) -> None:
    if rori_alias is not None:
        rori = rori_manager.get_rori(rori_alias)
        ui.print(ui.render_one(rori, verbose=verbose))
        return
    roris = rori_manager.get_roris()
    ui.print(ui.render_all(roris, verbose=verbose))


def safe_get(rori_alias: str) -> Rori:
    rori = rori_manager.get_rori(rori_alias)
    if rori.is_system:
        ui.error(f"cannot manage system rori {rori.name}")
        sys.exit(1)
    return rori


@cli.group(
    short_help="add new port forwarding configuration",
    invoke_without_command=True,
)
@interactive_option
@click.pass_context
@handle_rori_errors
def add(
    ctx,
    interactive: bool,
):
    ctx.ensure_object(dict)
    ctx.obj["start"] = False
    if interactive:
        # TODO: move to UI
        _mapping = {
            EntryTypes.KUBERNETES: add_kubernetes,
            EntryTypes.SSH: add_ssh,
        }
        type_choices = [
            questionary.Choice(f"{entry_type}", f"{entry_type}")
            for entry_type in EntryTypes.choices()
        ]
        selected_type = fzf_select_from_choices("select forwarding type", type_choices)
        ctx.obj["interactive"] = True
        ctx.forward(_mapping[selected_type])
        return

    if ctx.invoked_subcommand is None:
        subcommands = ", ".join(EntryTypes.choices())
        raise click.UsageError(f"please specify one of subcommands: {subcommands}")


@add.command("kubernetes")
@name_option
@k8s_options
@click.pass_context
@handle_rori_errors
def add_kubernetes(
    ctx,
    name: Optional[str],
    interactive: bool,
    port_from: int,
    port_to: int,
    context: str,
    namespace: str,
    service: Optional[str],
    pod: Optional[str],
) -> None:
    command_builder = CommandK8s()
    if interactive:
        command_context = command_builder.interactive()
    else:
        command_context = command_builder.build(
            context=context,
            namespace=namespace,
            pod=pod,
            service=service,
            port_from=port_from,
            port_to=port_to,
        )
    rori = rori_manager.create(name=name, context=command_context)
    # ctx.obj.get("start"):
    ui.info(f"added new configuration {rori.name}")


@add.command("ssh")
@name_option
@ssh_options
@click.pass_context
@handle_rori_errors
def add_ssh(
    ctx,
    name: Optional[str],
    interactive: bool,
    port_from: int,
    port_to: int,
    host_from: str,
    remote_user: str,
    remote_server: str,
) -> None:
    command_builder = CommandSsh()
    if interactive:
        command_context = command_builder.interactive()
    else:
        command_context = command_builder.build(
            port_from=port_from,
            port_to=port_to,
            host_from=host_from,
            remote_user=remote_user,
            remote_server=remote_server,
        )
    rori = rori_manager.create(name=name, context=command_context)
    ui.info(f"added new configuration {rori.name}")


@cli.group(
    short_help="add new port forwarding and start it immediately",
    invoke_without_command=True,
)
@interactive_option
@click.pass_context
@handle_rori_errors
def forward(
    ctx,
    interactive: bool,
) -> None:
    ctx.ensure_object(dict)
    if interactive:
        ctx.obj["interactive"] = True
        raise RoriError("interactive mode is not supported yet")


@forward.command("ssh")
@name_option
@ssh_options
@click.pass_context
@handle_rori_errors
def forward_ssh(
    ctx,
    interactive: bool,
    name: Optional[str],
    port_from: int,
    port_to: int,
    host_from: str,
    remote_user: str,
    remote_server: str,
) -> None:
    command_builder = CommandSsh()
    if interactive:
        command = command_builder.interactive()
    else:
        command = command_builder.build(
            port_from=port_from,
            port_to=port_to,
            host_from=host_from,
            remote_user=remote_user,
            remote_server=remote_server,
        )

    rori = rori_manager.create(name=name, context=command)
    rori_manager.start(rori)
    ui.info(
        f"saved {rori.name} and started forwarding: {rori.port_from}→{rori.port_to}"
    )


@forward.command("kubernetes")
@name_option
@k8s_options
@handle_rori_errors
def forward_kubernetes(
    interactive: bool,
    name: Optional[str],
    port_from: int,
    port_to: int,
    context: str,
    namespace: str,
    service: Optional[str],
    pod: Optional[str],
) -> None:
    builder = CommandK8s()
    if interactive:
        # command = run_interactive_port_forward()
        command_context = builder.interactive()
    else:
        command_context = builder.build(
            port_from=port_from,
            port_to=port_to,
            context=context,
            namespace=namespace,
            pod=pod,
            service=service,
        )

    rori = rori_manager.create(name=name, context=command_context)
    rori_manager.start(rori, context=command_context)
    ui.info(
        f"saved {rori.name} and started forwarding: {rori.port_from}→{rori.port_to}"
    )


@cli.command()
@click.argument("rori_alias", metavar="rori")
@click.option("-f", "--follow", is_flag=True, default=False)
@handle_rori_errors
def logs(
    rori_alias: str,
    follow: bool,
) -> None:
    rori = rori_manager.get_rori(rori_alias)
    lines = rori_manager.logs(rori, follow=follow)
    if follow:
        ui.info(f"streaming logs for {rori.name} from {rori.logfile}")
    else:
        ui.info(f"printing logs for {rori.name} from {rori.logfile}")
    for line in lines:
        ui.print(line)


@cli.command()
@click.argument("rori_alias", metavar="rori")
@handle_rori_errors
def start(
    rori_alias: str,
) -> None:
    rori: Rori = safe_get(rori_alias)
    rori_manager.start(rori)
    ui.info(f"started forwarding for {rori.name}: {rori.port_from}→{rori.port_to}")


@cli.command()
@click.argument("rori_alias", metavar="rori")
@handle_rori_errors
def stop(
    rori_alias: str,
) -> None:
    rori: Rori = safe_get(rori_alias)
    rori_manager.stop(rori)
    ui.info(f"forwarding for {rori.name} stopped")


@cli.command(short_help="stops the port forwarding process and starts it again")
@click.argument("rori_alias", metavar="rori", required=True)
@handle_rori_errors
def restart(rori_alias: str):
    rori: Rori = safe_get(rori_alias)
    rori_manager.restart(rori)
    ui.info(f"{rori.name} has been restarted")


@cli.command(short_help="sets a new name/alias for the existing entry")
@click.argument("rori_alias", metavar="rori", required=True)
@click.argument("new_name", metavar="new-name", required=True)
@handle_rori_errors
def rename(
    rori_alias: str,
    new_name: str,
) -> None:
    rori: Rori = safe_get(rori_alias)
    name = rori.name
    rori_manager.rename(rori, new_name)
    ui.info(f"renamed entry {name} to {new_name}")


@cli.command()
@click.argument("rori_alias", metavar="rori")
@click.option("-f", "--force", is_flag=True, default=False)
@handle_rori_errors
def delete(
    rori_alias: str,
    force: bool,
) -> None:
    rori: Rori = safe_get(rori_alias)
    name = rori.name
    rori_manager.delete(rori, force=force)
    ui.info(f"deleted entry {name}")


if __name__ == "__main__":
    cli()
