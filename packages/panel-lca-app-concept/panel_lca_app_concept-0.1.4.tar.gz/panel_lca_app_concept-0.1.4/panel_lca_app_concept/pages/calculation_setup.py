import panel as pn
import panel_material_ui as pmu
import pandas as pd
from panel_lca_app_concept.bw import list_projects, set_current_project, list_databases, list_processes, get_method_options, list_process_production, list_process_inputs

# Module-level shared state for calculation setup
_shared_state = {
    'current_project': None,
    'current_db': None,
    'df_processes': pd.DataFrame(columns=["Product", "Process", "Location"]),
    'widgets': None,
    'selected_process': None
}

def get_calculation_setup_widgets():
    """Get or create calculation setup widgets (singleton pattern)"""
    if _shared_state['widgets'] is not None:
        return _shared_state['widgets']
    
    _shared_state['widgets'] = create_calculation_setup_widgets()
    return _shared_state['widgets']

def create_calculation_setup_widgets():
    """Create all widgets for calculation setup page"""

    # Project & Database selection
    select_project = pmu.widgets.Select(
        label="Project",
        value=None,
        options=list_projects(),
        searchable=True,
        sizing_mode="stretch_width",
        # stylesheets=[
        #     ":host .MuiSelect-select {padding: 10px;}"
        # ]
    )

    select_db = pmu.widgets.Select(
        label="Database",
        searchable=True,
        options=["Select project first"],
        disabled=True,
        sizing_mode="stretch_width",        
        # stylesheets=[
        #     ":host .MuiSelect-select {padding: 10px;}"
        # ]
    )
    no_db_alert = pmu.Alert(
        title="Select Project & Database",
        severity="warning",
        margin=10,
        stylesheets=[
            ":host .MuiAlert-message {padding: 0; margin-top: 0.6em} :host .MuiAlert-icon {display: flex; align-items: center; padding: 0}"
        ],
        sizing_mode="stretch_width",
    )

    # Tables
    processes_tabulator = pn.widgets.Tabulator(
        _shared_state['df_processes'],
        sizing_mode="stretch_both",
        widths={
            "Product": "25%",
            "Process": "53%",
            "Location": "22%",
        },
        name="Processes",
        pagination="remote",
        show_index=False,
        sorters=[{"field": "Product", "dir": "asc"}],
        disabled=True,
        selectable=False,
        header_filters={
            "Product": {"type": "input", "func": "like", "placeholder": "Filter Products..."},
            "Process": {"type": "input", "func": "like", "placeholder": "Filter Processes..."},
            "Location": {"type": "input", "func": "like", "placeholder": "Filter Locations..."},
        },
        stylesheets=[
            ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
        ],
        )
    
    add_process_button = pmu.widgets.Button(
        label="Create New Process",
        icon="add",
        variant="contained",
        color="primary",
        sizing_mode="stretch_width",
        # stylesheets=[
        #     ":host .MuiButton-root {margin-top: 12px;}"
        # ]
    )
    
    dialog_create__button = pmu.widgets.Button(
        label="Create",
        icon="check",
        variant="contained",
        color="primary",
        sizing_mode="stretch_width",
    )
    dialog_discard_button = pmu.widgets.Button(
        label="Discard",
        icon="delete",
        variant="outlined",
        color="default",
        sizing_mode="stretch_width",
    )


    dialog_new_process = pmu.Dialog("""
# Ceate a new process

You will be able to enter new process data here.
""",
        pn.Row(dialog_create__button, dialog_discard_button),
        close_on_click=True,
        # show_close_button=True,
    )

    add_process_button.js_on_click(args={'dialog': dialog_new_process}, code="dialog.data.open = true")
    
    def _on_create_new_process(event):
        pn.state.notifications.success("New process created successfully! Except not, as this is a demo.")
    def _on_discard_process(event):
        pn.state.notifications.info("Process creation discarded.")
        
    dialog_create__button.js_on_click(args={'dialog': dialog_new_process}, code="dialog.data.open = false")
    dialog_create__button.on_click(_on_create_new_process)
    dialog_discard_button.js_on_click(args={'dialog': dialog_new_process}, code="dialog.data.open = false")
    dialog_discard_button.on_click(_on_discard_process)

    functional_unit = pn.widgets.Tabulator(
        pd.DataFrame(columns=["Amount", "Product", "Process", "Location"]),
        buttons={
            "delete": "<span class='material-icons'>delete_forever</span>",
        },
        sizing_mode="stretch_width",
        layout="fit_data_stretch",
        name="Processes",
        show_index=False,
        sorters=[{"field": "Product", "dir": "asc"}],
        editors={
            "Amount": "number",
            "Product": None,
            "Process": None,
            "Location": None,
        },
        stylesheets=[
            ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
        ],
    )

    # Callbacks
    def _on_project_select(event):
        print(f"Project selected: {event.new}")
        _shared_state['current_project'] = event.new
        set_current_project(event.new)
        select_db.disabled = False
        select_db.options = list_databases()[::-1]
        method_select.disabled = False
        options, levels = get_method_options()
        method_select.options = options
        method_select.levels = ["Source", "Method", "Category", "Indicator"]
        method_select.layout = {"type": pn.GridBox, "ncols": 2}

    def _on_db_select(event):
        print(f"Database selected: {event.new}")
        _shared_state['current_db'] = event.new
        no_db_alert.visible = False
        select_db.loading = True
        set_current_project(_shared_state['current_project'])
        _shared_state['df_processes'] = pd.DataFrame(
            [
                {
                    "Product": p.get("reference product"),
                    "Process": p.get("name"),
                    "Location": p.get("location"),
                }
                for p in list_processes(_shared_state['current_db'])
            ]
        )
        processes_tabulator.value = _shared_state['df_processes']
        processes_tabulator.pagination="remote"
        processes_tabulator.page_size = None
        processes_tabulator.layout = "fit_data_stretch"
        # processes_tabulator.layout = "fit_data_table"
        select_db.loading = False
        processes_tabulator.visible = True
        functional_unit.visible = True

    def _on_process_click(event):
        try:
            # Ignore clicks that are not on a data row
            if event.row is None:
                return
            # Get the clicked row from the *current* processes tabulator view
            # Use the currently displayed dataframe to respect active filters/sorts
            df_view = processes_tabulator.value
            clicked = df_view.iloc[[event.row]].copy()
            # Ensure columns and prepend default Amount
            clicked.insert(0, "Amount", 1.0)

            # Append to functional unit
            fu_df = functional_unit.value
            fu_df = pd.concat([fu_df, clicked], ignore_index=True)
            functional_unit.value = fu_df
            calculate_button.disabled = functional_unit.value.empty
            print(clicked)
            product_name.value = clicked["Product"].iloc[0]
            process_name.value = clicked["Process"].iloc[0]
            location_name.value = clicked["Location"].iloc[0]
            process_production = list_process_production(
                _shared_state['current_db'],
                clicked["Process"].iloc[0],
                clicked["Product"].iloc[0],
                clicked["Location"].iloc[0]
            )
            outputs.value = pd.DataFrame(
                [
                    (
                        e.amount,
                        e.input["reference product"],
                        e.input["name"],
                        e.input["location"],
                    )
                    for e in process_production
                ],
                columns=["Amount", "Product", "Process", "Location"],
            )
            process_inputs = list_process_inputs(
                _shared_state['current_db'],
                clicked["Process"].iloc[0],
                clicked["Product"].iloc[0],
                clicked["Location"].iloc[0]
            )
            inputs.value = pd.DataFrame(
                [
                    (
                        e.amount,
                        e.input["reference product"],
                        e.input["name"],
                        e.input["location"],
                    )
                    for e in process_inputs
                ],
                columns=["Amount", "Product", "Process", "Location"],
            )
            # description.value = clicked["Description"].iloc[0]

        except Exception as e:
            print(f"Process row click error: {e}")

    def _on_fu_click(event):
        try:
            if event.row is None or event.column != "delete":
                return
            df = functional_unit.value.reset_index(drop=True)
            if 0 <= event.row < len(df):
                df = df.drop(index=event.row).reset_index(drop=True)
                functional_unit.value = df
        except Exception as e:
            print(f"Functional unit delete error: {e}")
        calculate_button.disabled = functional_unit.value.empty

    # Wire up callbacks
    select_project.param.watch(_on_project_select, "value")
    select_db.param.watch(_on_db_select, "value")
    processes_tabulator.on_click(_on_process_click)
    functional_unit.on_click(_on_fu_click)

    method_select = pmu.NestedSelect(
        options=dict(),
        levels=[], #["Database", "Method", "Category", "Indicator"],
        # layout={"type": pn.GridBox, "ncols": 2},
        disabled=True,
    )

    calculate_button = pmu.widgets.Button(
        name="Calculate & Show Results",
        icon="calculate",
        icon_size="1.5em",
        variant="contained",
        color="primary",
        disabled=functional_unit.value.empty,
        size="large",
        sizing_mode="stretch_width",
    )

    def _on_calculate_click(event):
        pn.state.location.hash = "#results/impact-overview"

    calculate_button.on_click(_on_calculate_click)

    ### Edit Processes
    product_name = pmu.widgets.TextInput(
        label="Product Name",
        sizing_mode="stretch_width",
    )

    process_name = pmu.widgets.TextInput(
        label="Process Name",
        sizing_mode="stretch_width",
    )

    location_name = pmu.widgets.TextInput(
        label="Process Location",
        sizing_mode="stretch_width",
    )

    description = pmu.widgets.TextAreaInput(
        label="Process Description",
        sizing_mode="stretch_width",
    )

    outputs = pn.widgets.Tabulator(
        pd.DataFrame(columns=["Amount", "Product", "Process", "Location"]),
        sizing_mode="stretch_width",
        layout="fit_data_stretch",
        # widths={
        #     "Amount": "10%",
        #     "Product": "25%",
        #     "Process": "50%",
        #     "Location": "15%",
        # },
        show_index=False,
        editors={
            "Amount": "number",
            "Product": None,
            "Process": None,
            "Location": None,
        },
        stylesheets=[
            ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
        ],
    )

    inputs = pn.widgets.Tabulator(
        pd.DataFrame(columns=["Amount", "Product", "Process", "Location"]),
        sizing_mode="stretch_both",
        layout="fit_data_stretch",
        # widths={
        #     "Amount": "10%",
        #     "Product": "25%",
        #     "Process": "50%",
        #     "Location": "15%",
        # },
        show_index=False,
        editors={
            "Amount": "number",
            "Product": None,
            "Process": None,
            "Location": None,
        },
        stylesheets=[
            ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
        ],
    )

    return {
        'no_db_alert': no_db_alert,
        'select_project': select_project,
        'select_db': select_db,
        'processes_tabulator': processes_tabulator,
        'add_process_button': add_process_button,
        'dialog_new_process': dialog_new_process,
        'functional_unit': functional_unit,
        'method_select': method_select,
        'calculate_button': calculate_button,
        'product_name': product_name,
        'process_name': process_name,
        'location_name': location_name,
        'description': description,
        'inputs': inputs,
        'outputs': outputs,
    }

def create_calculation_setup_right_col():
    """Create the calculation setup page view"""
    widgets = get_calculation_setup_widgets()

    # Functional Unit section
    fu_header = pmu.pane.Markdown("""
## Functional Unit

These are the products selected for assessment. Amounts can be edited directly in the corresponding table cells.
""")
    fu_section = pmu.Column(
        fu_header,
        widgets['functional_unit'],
        sizing_mode="stretch_width",
    )
    
    # Method section
    method_header = pmu.pane.Markdown("""
## Method

Select the method to use for the analysis.
""")
    method_section = pmu.Column(
        method_header,
        widgets['method_select'],
        sizing_mode="stretch_width",
    )
    calc_setup = pmu.Column(
        fu_section,
        method_section,
        widgets['calculate_button'],
        sizing_mode="stretch_width",
    )
    
    process_edits = pmu.Column(
        widgets['product_name'],
        widgets['process_name'],
        widgets['location_name'],
        widgets['description'],
        widgets['outputs'],
        widgets['inputs'],
        sizing_mode="stretch_width",
    )

    return pmu.Tabs(
        ("Edit Processes", process_edits),
        ("Calculation Setup", calc_setup),
    )

def create_calculation_setup_left_col():
    """Create the calculation setup page sidebar"""
    widgets = get_calculation_setup_widgets()

    processes_section = pmu.Column(
        widgets['processes_tabulator'],
        sizing_mode="stretch_both",
    )

    return pmu.Column(
        widgets["no_db_alert"],
        pmu.Row(
            widgets["select_project"],
            widgets["select_db"],
            sizing_mode="stretch_width",
        ),
        widgets['processes_tabulator'],
        widgets['add_process_button'],
        widgets['dialog_new_process'],
        width=500,
        # sizing_mode="stretch_both",
    )

def create_calculation_setup_view():
    """Create the calculation setup page view"""
    return pmu.Row(
        create_calculation_setup_left_col(),
        create_calculation_setup_right_col(),
    )
