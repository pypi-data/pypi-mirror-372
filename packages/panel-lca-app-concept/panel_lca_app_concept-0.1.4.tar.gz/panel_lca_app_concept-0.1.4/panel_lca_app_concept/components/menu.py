import panel_material_ui as pmu

def create_menu():
    """Create the main navigation menu with hash routing paths"""
    return pmu.widgets.MenuList(
        items=[
            {
                "label": "Home",
                "icon": "home_rounded",
                "path": "home"
            },
            {
                "label": "Modeling",
                "icon": "settings_rounded",
                "selectable": False,
                "items": [
                    {'label': 'Process Definition', 'icon': 'handyman_rounded', 'path': 'modeling/process-definition'},
                    {'label': 'Calculation Setup', 'icon': 'calculate_rounded', 'path': 'modeling/calculation-setup'},
                ]
            },
            {
                "label": "Results",
                "icon": "query_stats_rounded",
                "selectable": False,
                "items": [
                    {'label': 'Impact Overview', 'icon': 'leaderboard_rounded', 'path': 'results/impact-overview'},
                    {'label': 'Contribution Analysis', 'icon': 'pie_chart_rounded', 'path': 'results/contribution-analysis'},
                ]
            },
        ],
        sizing_mode="stretch_width",
        dense=True,
        stylesheets=[
            ":host .MuiMenuItem-root.Mui-disabled {cursor: default !important; pointer-events: none;}"
        ]
    )