import bw2data as bd
import bw2calc as bc
from bw2data.backends import ActivityDataset as AD
from panel_lca_app_concept.helpers import build_nested_options


def list_projects() -> list[str]:
    """List all available Brightway2 projects."""
    return [proj.name for proj in bd.projects]

def set_current_project(project_name: str) -> None:
    """Set the current Brightway2 project."""
    bd.projects.set_current(project_name)

def list_databases() -> list[str]:
    """List all available Brightway2 projects."""
    return list(bd.databases)

def list_processes(db_name: str):
    """List all processes in a given Brightway2 database."""
    db = bd.Database(db_name)
    return list((act for act in db))

def search_db(db, term: str) :
    return bd.Database(db).search(term)

def filter_results(db, name="", product="", location=""):
    """Filter results based on name, product, and location."""
    return [act for act in bd.Database(db)
            if name.lower() in act.get("name").lower() and
            product.lower() in act.get("reference product", "").lower() and
            location.lower() in act.get("location", "").lower()]
    
def query_distinct_process_names(db):
    query = AD.select(AD.name).where(AD.database == db).distinct()
    return [entry.name for entry in query]

def get_method_options():
    method_list = [m for m in bd.methods]
    return build_nested_options(method_list)

def create_process(db, name, product, location, unit, process_production_amount, **metadata):
    """Create a new process in the specified database."""
    db = bd.Database(db)
    process = db.new_node(
        name=name,
        location=location,
        unit=unit,
        **metadata
    )
    process["reference product"] = product
    process.save()
    process.new_edge(
        input=process,
        amount=process_production_amount,
        type="production"
    ).save()
    return process

def list_process_inputs(process_db, process_name, process_product, process_location):
    """List all inputs for a given process."""
    process = bd.get_node(database=process_db, name=process_name, product=process_product, location=process_location)
    if not process:
        raise ValueError("Process not found.")
    return list(process.technosphere())

def list_process_production(process_db, process_name, process_product, process_location):
    """List all production for a given process."""
    process = bd.get_node(database=process_db, name=process_name, product=process_product, location=process_location)
    if not process:
        raise ValueError("Process not found.")
    return list(process.production())


def add_input(process_db, process_name, process_product, process_location, input_db, input_name, input_product, input_location, amount):
    """Add an input to a process."""
    process = bd.get_node(database=process_db, name=process_name, product=process_product, location=process_location)
    input_act = bd.get_node(database=input_db, name=input_name, product=input_product, location=input_location)

    if not process or not input_act:
        raise ValueError("Process or input activity not found.")
    
    process.new_edge(
        input=input_act,
        amount=amount,
        type="technosphere"
    ).save()
    
    return process