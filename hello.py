"""Start and stop apps."""
from __future__ import annotations

from collections import defaultdict
from os import path
from pathlib import Path
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple, Union

import click
from clib import dry_run_option
from clib.files import fzf, shell
from clib.ui import failure, success


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
        collection_key: str = None,
        path: str = None,
    ) -> None:
        self.name = name
        self._full_name = f"{name}.app"
        self.cli = cli
        self.path = path
        if cli:
            which_results = shell(f"which {name}", return_lines=True, quiet=True)
            if which_results:
                self.path = Path(which_results[0])
        if not self.path:
            self.path = Path(f"/Applications/{self._full_name}")
        self.pkill = pkill
        self.open_commands = open_commands or []
        self.kill_commands = kill_commands or []
        self.background = background

        self.ALL_NAMES[name] = self
        self.collection[collection_key].add(self)

    def __repr__(self):
        """String representation."""
        return f"<App {self._full_name}>"

    def on(self):
        """Open the app."""
        func = print if self.dry_run else shell
        back = " &" if self.background else ""

        if self.open_commands:
            for command in self.open_commands:
                func(f"{command}{back}")
            return
        if self.cli:
            func(f"'{self.path}'{back}")
        else:
            func(f"open '{self.path}'")

    def off(self):
        """Close/kill the app."""
        func = print if self.dry_run else shell
        if self.kill_commands:
            for command in self.kill_commands:
                func(command)
        else:
            func(f"pkill '{self.pkill or self.name}'")


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


Spotify = App("Spotify")
SpotifyNowPlaying = App("Spotify - now playing")
Telegram = App("Telegram", kill_commands=["pkill -9 Telegram"])
WhatsApp = App("WhatsApp")

# Kill Signal twice because it's die hard
Signal = App("Signal", kill_commands=["sleep .5", "pkill Signal"] * 2)

VisualStudioCode = App("Visual Studio Code", pkill="Electron")
BraveBrowser = App("Brave Browser")
BraveBrowserDev = App("Brave Browser Dev")
Skype = App("Skype")
TogglTrack = App("Toggl Track")
PyCharm = App("PyCharm", pkill="pycharm")
Zoom = App("zoom.us")

# Scan Snap has some background processes
ScanSnapHome = App("ScanSnapHomeMain", kill_commands=[ps_aux_kill("scansnap")])

Finicky = App("Finicky")
Docker = App("Docker")
OneDrive = App("OneDrive", kill_commands=["pkill OneDrive", ps_aux_kill("OneDrive.+FinderSync", force=True)])
Dropbox = App("Dropbox")
DontForget = App(
    "dontforget",
    cli=True,
    open_commands=["dontforget menu"],
    background=True,
    kill_commands=[ps_aux_kill("dontforget")],
)
KeepingYouAwake = App("KeepingYouAwake")
RescueTime = App("RescueTime")
BeardedSpice = App("BeardedSpice")
PrivateInternetAccess = App("Private Internet Access")
Slack = App("Slack")
Hammerspoon = App("Hammerspoon")
Bluetooth = App(
    "blueutil", cli=True, open_commands=["blueutil -p 1"], kill_commands=["blueutil -p 0"], collection_key="switch"
)
Tunnelblick = App("Tunnelblick")
CloudflareWARP = App("Cloudflare WARP", kill_commands=["warp-cli disconnect", "pkill 'Cloudflare WARP'"])
Todoist = App("Todoist")
Bitwarden = App("Bitwarden")
VLC = App("VLC")
XQuartz = App("XQuartz", kill_commands=["pkill -9 launchd_startx"])
BeFocused = App("Be Focused")
Flameshot = App("flameshot")
DeepL = App("DeepL")
AppPolice = App("AppPolice")
ExtensionsPane = App("Extensions.prefPane", path="/System/Library/PreferencePanes/Extensions.prefPane")
ActivityMonitor = App("Activity Monitor", path="/System/Applications/Utilities/Activity Monitor.app")
Toolbox = App("JetBrains Toolbox", pkill="jetbrains-toolbox")
Postman = App("Postman")
Gnucash = App("Gnucash")


GROUPS = {
    "off": Action("Turn off all apps and go to sleep", turn_off, App.collection[None]),
    "switch": Action(
        "Turn off all apps before switching laptops", turn_off, App.collection[None] | App.collection["switch"]
    ),
    "background": Action(
        "Background apps",
        turn_on,
        ["minimal", OneDrive, KeepingYouAwake, Todoist, RescueTime, TogglTrack, Docker, DontForget, Bitwarden],
    ),
    "minimal": Action("Minimalistic apps", turn_on, [Bluetooth, Finicky, Hammerspoon]),
    "sync": Action("Sync apps", turn_on, [OneDrive, ExtensionsPane, ActivityMonitor]),
    "web": Action("Browse the web", turn_on, [Finicky, BraveBrowserDev]),
    "nitpick": Action("Nitpick", turn_on, [Hammerspoon, "web", TogglTrack, VisualStudioCode, PyCharm]),
    "development": Action("Development", turn_on, [TogglTrack, Docker, "web", VisualStudioCode, PyCharm]),
    "music": Action("Listen to music", turn_on, [Spotify, SpotifyNowPlaying, BeardedSpice]),
    "psychotherapy": Action("Therapy", turn_on, ["minimal", KeepingYouAwake, Skype, Gnucash]),
    "work": Action(
        "Work apps",
        turn_on,
        [
            Finicky,
            BraveBrowser,
            VisualStudioCode,
            Slack,
            Signal,
            Telegram,
            WhatsApp,
            Flameshot,
            CloudflareWARP,
            Toolbox,
        ],
    ),
    "famiglia": Action(
        "Video call with the family", turn_on, ["minimal", "web", KeepingYouAwake, TogglTrack, Skype, WhatsApp]
    ),
    "pod-demo": Action(
        "Pod demo in the bi-weekly BA Review",
        turn_on,
        [Bluetooth, Finicky, Hammerspoon, BraveBrowser, KeepingYouAwake, VisualStudioCode, Zoom],
    ),
    "chat": Action("Open all chat apps (plus DeepL to translate stuff)", turn_on, [Signal, Telegram, WhatsApp, DeepL]),
    "conference": Action("Open all video conference apps", turn_on, [Zoom, Skype]),
}


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
        chosen = fzf(list(GROUPS.keys()) + list(App.ALL_NAMES.keys()), query=query)
        if not chosen:
            continue

        if chosen in GROUPS:
            action = GROUPS[chosen]
            desired_function = turn_off if off else action.function
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


if __name__ == "__main__":
    main()
