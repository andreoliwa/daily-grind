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
from typing import Dict, List, Tuple

import click
from clib import dry_run_option
from clib.files import fzf
from clib.ui import success

from daily_grind import ActionFunction, App, get_recursive_apps, turn_off, turn_on
from daily_grind.config import settings


def function_from_str(function_name: str):
    return turn_on if "on" in function_name else turn_off


@click.command()
@dry_run_option
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
