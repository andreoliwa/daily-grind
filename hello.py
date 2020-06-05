"""Start and stop apps."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, NamedTuple, Set, Tuple, Union

import click
from clib import dry_run_option
from clib.files import fzf, shell
from clib.ui import failure, success


class App:
    """A desktop application."""

    ALL_APPS: Set[App] = set()
    ALL_NAMES: Dict[str, App] = {}

    dry_run = False

    def __init__(self, name: str, pkill: str = None, kill_commands: List[str] = None) -> None:
        self.name = name
        self.path = Path(f"/Applications/{name}.app")
        self.pkill = pkill
        self.kill_commands = kill_commands or []

        self.ALL_APPS.add(self)
        self.ALL_NAMES[name] = self

    def __repr__(self):
        """String representation."""
        return f"<App {self.name}>"

    def on(self):
        """Open the app."""
        func = print if self.dry_run else shell
        func(f"open '{self.path}'")

    def off(self):
        """Close/kill the app."""
        func = print if self.dry_run else shell
        if self.kill_commands:
            for command in self.kill_commands:
                func(command)
        else:
            func(f"pkill '{self.pkill or self.name}'")


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

    action = GROUPS.get(group)
    if not action:
        failure(f"Group does not exist: {group}")
        return []

    found_apps = []
    for app in action.apps:
        if app in seen:
            continue
        seen.add(app)

        if isinstance(app, str):
            found_apps.extend(get_recursive_apps(app, seen))
        else:
            found_apps.append(app)
    return found_apps


Spotify = App("Spotify")
SpotifyNotifications = App("Spotify Notifications")
Telegram = App("Telegram")
WhatsApp = App("WhatsApp")

# Kill Signal twice because it's die hard
Signal = App("Signal", kill_commands=["sleep .5", "pkill Signal"] * 2)

VisualStudioCode = App("Visual Studio Code", pkill="Electron")
BraveBrowser = App("Brave Browser")
BraveBrowserDev = App("Brave Browser Dev")
Skype = App("Skype")
TogglDesktop = App("TogglDesktop")
PyCharmCE = App("PyCharm CE", pkill="pycharm")
Zoom = App("zoom.us")

# Scan Snap has some background processes
ScanSnapHome = App("ScanSnapHomeMain", kill_commands=["ps aux | rg scansnap | awk '{print $2}' | xargs kill"])

Finicky = App("Finicky")
Docker = App("Docker")
OneDrive = App("OneDrive")
Dropbox = App("Dropbox")
MiaForGmail = App("Mia for Gmail")
KeepingYouAwake = App("KeepingYouAwake")
RescueTime = App("RescueTime")
BeardedSpice = App("BeardedSpice")
PrivateInternetAccess = App("Private Internet Access")
Slack = App("Slack")
Hammerspoon = App("Hammerspoon")

GROUPS = {
    "off": Action("Turn off all apps and go to sleep", turn_off, App.ALL_APPS),
    "background": Action(
        "Background apps",
        turn_on,
        [Finicky, Docker, OneDrive, KeepingYouAwake, RescueTime, MiaForGmail, TogglDesktop, Hammerspoon],
    ),
    "web": Action("Browse the web", turn_on, [Finicky, BraveBrowserDev]),
    "dev": Action("Development", turn_on, [TogglDesktop, Docker, "web", VisualStudioCode, PyCharmCE]),
    "music": Action("Listen to music", turn_on, [Spotify, SpotifyNotifications, BeardedSpice]),
    "psychotherapy": Action("Therapy", turn_on, [KeepingYouAwake, Signal, VisualStudioCode, "web"]),
    "sennder": Action("Sennder apps", turn_on, [Finicky, BraveBrowser, VisualStudioCode, Slack]),
}


@click.command()
@dry_run_option
@click.option("--list", "-l", "list_", is_flag=True, default=False, help="List the available groups")
@click.argument("group_or_app", nargs=-1, required=False)
def main(dry_run: bool, list_, group_or_app: Tuple[str]):
    """Start and stop apps in groups, processed in the order they were informed."""
    App.dry_run = dry_run

    if list_ or not group_or_app:
        success("Groups:")
        max_len = max(len(key) for key in GROUPS)
        for key, action in GROUPS.items():
            click.echo(f"{key:{max_len}}  {action.description}")

        success("Apps:")
        click.echo("  " + ", ".join(sorted(App.ALL_NAMES.keys())))
        return

    # Group by app, keeping only the last function for each app
    # This way, an app won't be off/on/off/on multiple times... last action is "on".
    app_mapping: Dict[App, ActionFunction] = {}
    for query in group_or_app:
        chosen_app = ""
        chosen_group = fzf(GROUPS.keys(), query=query)
        if not chosen_group:
            chosen_app = fzf(App.ALL_NAMES.keys(), query=query)

        if chosen_group:
            action = GROUPS[chosen_group]
            success(f"Group: {chosen_group} / Action: {action.function}")
            names = []
            for app in get_recursive_apps(chosen_group):
                app_mapping[app] = action.function
                names.append(app.name)
            click.echo("  " + ", ".join(names))
        elif chosen_app:
            # If an app was informed, we assume it should be open
            app = App.ALL_NAMES[chosen_app]
            app_mapping[app] = turn_on

    # Group by function again
    function_mapping: Dict[ActionFunction, List[App]] = defaultdict(list)
    for app, func in app_mapping.items():
        function_mapping[func].append(app)

    success("Executing the actions")
    for func, list_apps in function_mapping.items():
        func(list_apps)


if __name__ == "__main__":
    main()
