"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mdaily_grind` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``daily_grind.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``daily_grind.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import click

from daily_grind import CONTEXT, ActionFunction, App, get_recursive_apps, success, turn_off, turn_on
from daily_grind.config import settings


def function_from_str(function_name: str):
    return turn_on if "on" in function_name else turn_off


@click.command()
@click.option(
    "--dry-run", "-n", default=False, is_flag=True, help="Only show what would be done, without actually doing it"
)
@click.option("--list", "-l", "show_list", is_flag=True, default=False, help="List the available groups")
@click.option("--off", "-x", is_flag=True, default=False, help="Turn off the apps instead of opening")
@click.argument("group_or_app", nargs=-1, required=False)
def main(dry_run: bool, show_list: bool, off: bool, group_or_app: Tuple[str]) -> None:
    """Start and stop apps in groups, processed in the order they were informed."""
    App.dry_run = dry_run

    if show_list or not group_or_app:
        success("Groups:")
        max_len = max(len(key) for key in settings.groups.keys())
        for key, box in settings.groups.items():
            click.echo(f"{key:{max_len}}  {box.description}")

        success("Apps:")
        click.echo("  " + ", ".join(sorted(App.ALL_NAMES.keys())))
        return

    # Group by app, keeping only the last function for each app
    # This way, an app won't be off/on/off/on multiple times... last action is "on".
    app_mapping: Dict[App, ActionFunction] = {}
    for query in group_or_app:
        chosen = fzf(list(settings.groups.keys()) + list(App.ALL_NAMES.keys()), query=query)
        if not chosen:
            continue

        if chosen in settings.groups.keys():
            box = settings.groups[chosen]
            desired_function = turn_off if off else function_from_str(box.function)
            success(f"Group: {chosen} / Action: {desired_function.__name__}")
            names = []
            for app in get_recursive_apps(chosen):
                app_mapping[app] = desired_function
                names.append(app.name)
            click.echo("  " + ", ".join(names))

        elif chosen in App.ALL_NAMES:
            # If an app was informed, we assume it should be open
            app = App.ALL_NAMES[chosen]
            app_mapping[app] = turn_off if off else turn_on

    # Group by function again
    function_mapping: Dict[ActionFunction, List[App]] = defaultdict(list)
    for app, func in app_mapping.items():
        function_mapping[func].append(app)

    if not function_mapping:
        raise click.ClickException("Choose an app or group")

    success("Executing the actions")
    for func, list_apps in function_mapping.items():
        func(list_apps)


def fzf(
    items: List[Any], *, reverse=False, query: str = None, auto_select: bool = None, exit_no_match: bool = None
) -> Optional[str]:
    """Run fzf to select among multiple choices."""
    choices = "\n".join([str(item) for item in items])

    query_opt = ""
    if query:
        query_opt = f" --query={query}"
        # If there is a query, set auto-select flags when no explicit booleans were informed
        if auto_select is None:
            auto_select = True
        if exit_no_match is None:
            exit_no_match = True

    select_one_opt = " --select-1" if auto_select else ""
    tac_opt = " --tac" if reverse else ""
    exit_zero_opt = " --exit-0" if exit_no_match else ""

    result = CONTEXT.run(
        f'echo "{choices}" | fzf --height 40% --reverse --inline-info '
        f"{query_opt}{tac_opt}{select_one_opt}{exit_zero_opt} --cycle",
        warn=True,
        echo=False,
        pty=False,
    )
    return min(result.stdout.splitlines(), default=None)
