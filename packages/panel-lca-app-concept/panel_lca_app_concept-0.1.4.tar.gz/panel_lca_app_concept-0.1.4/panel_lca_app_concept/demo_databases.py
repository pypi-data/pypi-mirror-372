import bw2data as bd


def add_chem_demo_project():
    """
    Create a single demo project for a chemical/pharma background with
    a single background database containing a few common processes and
    plausible CO2 intensities. Numbers are rough, order-of-magnitude
    placeholders for demo purposes only.
    """
    # Reset demo project
    if "chem_demo" in bd.projects:
        bd.projects.delete_project("chem_demo", delete_dir=True)
        bd.projects.purge_deleted_directories()
    bd.projects.set_current("chem_demo")

    # Minimal biosphere with CO2
    biosphere = bd.Database("biosphere")
    biosphere.write({
        ("biosphere", "CO2"): {
            "type": "emission",
            "name": "carbon dioxide",
            "unit": "kilogram",
        }
    })

    node_co2 = biosphere.get("CO2")

    # Single background database with made-up processes
    if "background_chem" in bd.databases:
        del bd.databases["background_chem"]
    background = bd.Database("background_chem")
    background.register()

    # Rough CO2 intensities per unit output (very approximate demo values)
    processes = [
        {"code": "methanol", "name": "methanol", "unit": "kilogram", "co2": 0.9},          # ~0.7–1.4 kg CO2/kg
        {"code": "ethanol", "name": "ethanol", "unit": "kilogram", "co2": 1.5},            # fossil route, order of magnitude
        {"code": "acetone", "name": "acetone", "unit": "kilogram", "co2": 1.8},            # ~1.6–2.1 kg CO2/kg
        {"code": "ammonia", "name": "ammonia", "unit": "kilogram", "co2": 2.0},            # ~1.6–2.4 kg CO2/kg
        {"code": "acetic_acid", "name": "acetic acid", "unit": "kilogram", "co2": 1.7},    # ~1.5–2.0 kg CO2/kg
        # Additional solvent-like chemicals
        {"code": "toluene", "name": "toluene", "unit": "kilogram", "co2": 2.3},          # ~2–2.5 kg CO2/kg
        {"code": "xylene", "name": "xylene", "unit": "kilogram", "co2": 2.4},            # ~2–2.6 kg CO2/kg
        {"code": "chloroform", "name": "chloroform", "unit": "kilogram", "co2": 2.8},    # ~2.5–3.0 kg CO2/kg
        {"code": "dichloromethane", "name": "dichloromethane", "unit": "kilogram", "co2": 3.0},  # ~2.7–3.2 kg CO2/kg
        {"code": "acetonitrile", "name": "acetonitrile", "unit": "kilogram", "co2": 2.0}, # ~1.8–2.2 kg CO2/kg
        {"code": "electricity", "name": "electricity", "unit": "kilowatt hour", "co2": 0.4},  # ~0.4 kg CO2/kWh generic mix
        {"code": "process_heat", "name": "process heat, natural gas", "unit": "megajoule", "co2": 0.056},     # ~56 kg CO2/GJ ≈ 0.056 kg/MJ
    ]

    for p in processes:
        node = background.new_node(
            p["code"], name=f"production of {p['name']}", unit=p["unit"], location="somewhere"
        )
        node["reference product"] = p["name"]
        node.save()
        # Production reference
        node.new_edge(input=node, amount=1, type="production").save()
        # CO2 emission to biosphere
        node.new_edge(input=node_co2, amount=p["co2"], type="biosphere").save()

    # Simple GWP method that counts only CO2
    bd.Method(("example source", "simple", "climate change", "GWP100")).write([
        (("biosphere", "CO2"), 1),
    ])
