from __future__ import annotations

from daily_grind import Action, App, ps_aux_kill, turn_off, turn_on

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
PyCharm = App("PyCharm", pkill="pycharm")
Zoom = App("zoom.us")
ScanSnapHome = App("ScanSnapHomeMain", kill_commands=[ps_aux_kill("scansnap")])  # Has some background processes
Finicky = App("Finicky")
Docker = App("Docker")
OneDrive = App(
    "OneDrive",
    # TODO for now, don't force kill OneDrive because it might lead to sync errors
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

GROUPS = {
    "off": Action("Turn off all apps and go to sleep", turn_off, App.collection[None]),
    "switch": Action(
        "Turn off all apps before switching laptops", turn_off, App.collection[None] | App.collection["switch"]
    ),
    "background": Action(
        "Background apps",
        turn_on,
        ["minimal", OneDrive, KeepingYouAwake, Todoist, RescueTime, TogglTrack, Docker, DontForget, Bitwarden, Logseq],
    ),
    "minimal": Action("Minimalistic apps", turn_on, [Bluetooth, Finicky, Hammerspoon]),
    "sync": Action("Sync apps", turn_on, [OneDrive, ExtensionsPane, ActivityMonitor]),
    "web": Action("Browse the web", turn_on, [Finicky, BraveBrowserBeta]),
    "nitpick": Action("Nitpick", turn_on, [Hammerspoon, "web", TogglTrack, VisualStudioCode, PyCharm]),
    "development": Action("Development", turn_on, [TogglTrack, Docker, "web", VisualStudioCode, PyCharm]),
    "music": Action("Listen to music", turn_on, [Spotify, SpotifyNowPlaying, BeardedSpice]),
    "psychotherapy": Action(
        "Therapy", turn_on, ["minimal", KeepingYouAwake, Skype, Gnucash, SimpleFloatingClock, Logseq]
    ),
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
