from __future__ import annotations

__version__ = "0.0.0"

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Union

import click
from invoke import Config, Context, Result

GROUPS_PREFIX = "groups."

# Reuse "echo" from the global Invoke config,
# but not "pty", because it doesn't work with background processes.
config_dict = {"run": {"echo": bool(os.environ.get("INVOKE_RUN_ECHO", False))}}
CONTEXT = Context(Config(config_dict))


class App:
    """A desktop application or a command-line script."""

    ALL_NAMES: Dict[str, App] = {}
    collection: Dict[Optional[str], Set[App]] = defaultdict(set)

    dry_run = False

    def __init__(
        self,
        name: str,
        *,
        pkill: str = None,
        open_commands: List[str] = None,
        kill_commands: List[str] = None,
        cli=False,
        background=False,
        collection_key: str = None,  # TODO: refactor: remove unused collection_key
        path: str = None,
    ) -> None:
        self.name = name
        self._full_name = f"{name}.app"
        self.cli = cli
        self.path = Path(path).expanduser() if path else None
        if cli:
            which_results = CONTEXT.run(f"which {name}", hide=True).stdout.splitlines()
            if which_results:
                self.path = Path(which_results[0])
        if not self.path:
            self.path = Path(f"/Applications/{self._full_name}")
        self.pkill = pkill
        self.open_commands = open_commands or []
        self.kill_commands = kill_commands or []
        self.background = background

        self.ALL_NAMES[clean_name(name)] = self
        self.collection[collection_key].add(self)

    def __repr__(self):
        """String representation."""
        return f"<App {self._full_name}>"

    def on(self):
        """Open the app."""
        back = ""
        kwargs = {}
        if self.background:
            back = " &"
            kwargs["asynchronous"] = True

        if self.open_commands:
            for command in self.open_commands:
                self._run(f"{command}{back}", **kwargs)
            return
        quoted_path = f"'{self.path}'"
        if self.cli:
            self._run(f"{quoted_path}{back}", **kwargs)
        else:
            self._run(f"open {quoted_path}{back}", **kwargs)

    def off(self):
        """Close/kill the app."""
        if self.kill_commands:
            for command in self.kill_commands:
                self._run(command)
        else:
            self._run(f"pkill '{self.pkill or self.name}'")

    def _run(self, command: str, **kwargs) -> Result | None:
        """Run a command."""
        if self.dry_run:
            print(command)
            return None
        return CONTEXT.run(command, **kwargs, warn=True)


def clean_name(name: str) -> str:
    return name.strip().replace(" ", "").lower()


class Script(App):
    """A command-line script."""


ActionFunction = Callable[[Iterable[App]], None]


class Action(NamedTuple):
    """An action on a list of apps."""

    description: str
    function: ActionFunction
    apps: Iterable[Union[App, str]]


def turn_on(apps: Iterable[App]):
    """Open the apps."""
    for app in apps:
        app.on()


def turn_off(apps: Iterable[App]):
    """Close the apps."""
    for app in apps:
        app.off()


def get_recursive_apps(group: str, seen: Set = None) -> List[App]:
    """Get a list of recursive apps from a group."""
    if seen is None:
        seen = set()

    from daily_grind.config import settings

    box = settings.groups.get(group)
    if not box:
        failure(f"Group does not exist: {group}")
        return []

    # Use all apps if the "apps" keys is empty on the TOML file
    apps_in_group = box.apps
    if not apps_in_group:
        return list(App.collection[None])

    found_apps: List[App] = []
    for app_name in apps_in_group:
        if app_name in seen:
            continue
        seen.add(app_name)

        if app_name.startswith(GROUPS_PREFIX):
            found_apps.extend(get_recursive_apps(app_name.replace(GROUPS_PREFIX, ""), seen))
        else:
            app = App.ALL_NAMES.get(clean_name(app_name))
            if app:
                found_apps.append(app)
            else:
                click.secho(f"App {app_name} not found!", fg="red")
    return found_apps


def ps_aux_kill(app_partial_name: str, *, exclude: List[str] = None, sudo: bool = False, force: bool = False):
    """Return a command to run ps aux on a string and kill the processes.

    Only ask for ``sudo`` password when needeed:
    check if there are PIDs first, then run the ``sudo kill`` command if there are PIDs.
    """
    exclude_str = "".join(f" | rg -v {item}" for item in exclude or [])
    list_pids = f"ps aux | rg {app_partial_name} | rg -v 'rg {app_partial_name}'{exclude_str} | awk '{{print $2}}'"
    dash_nine = " -9" if force else ""
    if sudo:
        return f'test -n "$({list_pids})" && {list_pids} | sudo xargs kill{dash_nine}'
    return f"{list_pids} | xargs kill{dash_nine}"


def success(message: str) -> None:
    """Display a success message."""
    click.secho(message, fg="bright_green")


def failure(message: str, exit_code: int = None) -> None:
    """Display an error message and optionally exit."""
    click.secho(message, fg="bright_red", err=True)
    if exit_code is not None:
        sys.exit(exit_code)
