# Configuration

Create a `settings.toml` file on your config dir:

- Linux: `~/.config/daily-grind/settings.toml`
- macOS: ` ~/Library/Application Support/daily-grind/settings.toml`

## Groups and apps

The file should contain groups and its apps, in this format:

```toml
[groups.your-group-name]
description = "Your group"
function = "turn_on"
apps = ["App1", "App2", "groups.another-group"]

[groups.another-group]
description = "Another gorup"
function = "turn_on"
apps = ["App4", "App5"]
```

- The `apps` list can contain a reference to other groups, as seen above.
- TODO: The list of apps is hardcoded in the Python code.
- TODO: There is no validation yet for the TOML file: beware of typos.

# Example

```toml
[groups.minimal]
description = "Minimal apps"
function = "turn_on"
apps = ["Bluetooth", "Finicky", "Hammerspoon"]

[groups.background]
description = "Background apps"
function = "turn_on"
apps = ["groups.minimal", "OneDrive", "Docker", "Bitwarden"]
```
