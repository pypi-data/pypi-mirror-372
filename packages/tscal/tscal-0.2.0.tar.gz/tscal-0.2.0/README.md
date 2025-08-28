![PyPI - Version](https://img.shields.io/pypi/v/tscal)
# Simple calendar for usage in popups.

![Screenshot](./screenshots/screen.jpg)

## Installation

```sh
uv tool install tscal
```

## Example usage (in Sway):

```sh
kitty --class="kitty-tscal" tscal
```

### Then is Sway config:

```
for_window [app_id="kitty-tscal"] floating enable, resize set width 500 px height 250 px, move position cursor
```

### Custom style can be provided with ‘-s’ flag:
```sh
uv run tscal -s /custom/style/path.tcss
```

## Keyboard commands:

- Ctrl+f - next month
- Ctrl+b - previous month
- Ctrl+n - next year
- Ctrl+p - previous year
- Ctrl+t - today
