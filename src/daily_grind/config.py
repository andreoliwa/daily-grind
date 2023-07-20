from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

from daily_grind import App, ps_aux_kill
from daily_grind.constants import CONFIG_DIR, PROJECT_NAME_SHORT, SETTINGS_TOML

Spotify = App("Spotify")
SpotifyNowPlaying = App("Spotify - now playing")
Telegram = App("Telegram", kill_commands=["pkill -9 Telegram"])
WhatsApp = App("WhatsApp")
Signal = App("Signal", kill_commands=["sleep .5", "pkill Signal"] * 2)  # Kill twice because it's die hard
VisualStudioCode = App("Visual Studio Code", pkill="Electron")
BraveBrowser = App("Brave Browser")
BraveBrowserBeta = App("Brave Browser Beta")
Skype = App("Skype")
TogglTrack = App("Toggl Track")
PyCharm = App("PyCharm", pkill="pycharm", path="~/Applications/JetBrains Toolbox/PyCharm Professional.app")
Zoom = App("zoom.us")
ScanSnapHome = App("ScanSnapHomeMain", kill_commands=[ps_aux_kill("scansnap")])  # Has some background processes
Finicky = App("Finicky")
Docker = App("Docker")
OneDrive = App(
    "OneDrive",
    # TODO: fix: don't force kill OneDrive because it might lead to sync errors
    kill_commands=[
        "echo Quit OneDrive manually to avoid sync errors # pkill OneDrive",
        # ps_aux_kill("OneDrive.+FinderSync", force=True)
    ],
)
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
LogitechGHub = App("lghub")
DymoPrintingHost = App("DYMO.DLS.Printing.Host")
SimpleFloatingClock = App("SimpleFloatingClock")
Logseq = App("Logseq")

settings = Dynaconf(
    envvar_prefix=PROJECT_NAME_SHORT.upper(),
    settings_files=[SETTINGS_TOML, Path(CONFIG_DIR) / SETTINGS_TOML],
)
