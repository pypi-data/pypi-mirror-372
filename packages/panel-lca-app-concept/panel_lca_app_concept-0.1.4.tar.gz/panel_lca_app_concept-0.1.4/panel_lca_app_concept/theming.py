import panel as pn

theme_config = {
    "light": {
        "palette": {
            "primary": {"main": "#00549F"},
            "secondary": {"main": "#E30066"},
            "background": {"default": "#f7f7fb", "paper": "#ffffff"},
            "text": {"primary": "#1c1b29", "secondary": "#4b4a5e"},
        },
        "shape": {"borderRadius": 12},
    },
    "dark": {
        "palette": {
            "primary": {"main": "#00549F"},
            "secondary": {"main": "#E30066"},
            "background": {"default": "#0f0f17", "paper": "#1a1a24"},
            "text": {"primary": "#e8e7f5", "secondary": "#b6b4d6"},
        },
        "shape": {"borderRadius": 12},
    },
}


def current_bg_color() -> str:
    mode = str(getattr(pn.config, "theme", "dark")).lower()
    key = "dark" if "dark" in mode else "light"
    return theme_config[key]["palette"]["background"]["paper"]
