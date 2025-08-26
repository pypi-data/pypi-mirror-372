import panel_material_ui as pmu


def create_home_view():
    """Create the home page view"""
    content = pmu.Container(
        pmu.pane.Markdown(
"""

# Welcome to the PMI-LCA Tool

This prototype is part of our proposal to develop a full-featured web-based tool for calculating sustainability metrics using Process Mass Intensity (PMI) and Life Cycle Assessment (LCA).  

The aim of this demo is to illustrate the potential of transforming current spreadsheet-based PMI-LCA workflows into a modern, interactive, and scalable web application. It highlights how such a tool can improve usability, streamline workflows, and make results easier to explore and communicate.  

In the complete implementation, the app would support real datasets, robust analytics, and advanced visualization features, enabling researchers, industry, and policymakers to make better-informed decisions.  

With this proposal, we are seeking approval and support to carry out the full development. This demo is only a first glimpse—what follows could become a powerful, widely applicable decision-support platform. 

  
*Brought to you by:*

![Institute of Technical Thermodynamics, RWTH Aachen University](https://www.ltt.rwth-aachen.de/global/show_picture.asp?id=aaaaaaaaaanvmia)

"""
        )
    )
    return content


def create_home_sidebar():
    """Create the home page sidebar"""
    return pmu.Column(
        pmu.pane.Markdown("## About\nThis app demonstrates an LCA workflow.\nUse the menu to navigate."),
        sizing_mode="stretch_width",
    )
