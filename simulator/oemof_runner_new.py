import os
import pandas as pd
from oemof.solph import processing
from .model.model_factory import ExcelModelFactory

def run_oemof_scenario():
    """
    Run OEMOF energy system optimization scenario
    
    Returns:
        dict: Dictionary containing energy balance results
    """
    # Path to your Excel config
    file_dir = os.path.join(os.path.dirname(__file__), '../data')
    file_path = os.path.join(file_dir, 'KonfigurationSzenarios.xlsx')

    # Build factory + model
    model_factory = ExcelModelFactory(file_path, 'SimpleSzenarioD')
    model = model_factory.model

    # Solve model
    model.solve(solver="cbc")

    # Get results
    results = processing.results(model)

    # === Calculate totals exactly as you do in run_model.py ===
    total_sources = 0
    total_sinks = 0
    losses = 0

    for (i, o), v in results.items():
        if hasattr(i, 'label') and str(i).startswith('Src_'):
            total_sources += v['sequences'].sum().sum()
        if hasattr(o, 'label') and str(o).startswith('Snk_'):
            total_sinks += v['sequences'].sum().sum()

    # Losses = difference between sources and sinks
    losses = total_sources - total_sinks

    return {
        "sources_before": total_sources,   # Excel input potentials if you want
        "sinks_before": total_sinks,       # Demand before optimization
        "sources_after": total_sinks,      # Net usable sources
        "sinks_after": total_sinks,
        "losses": losses,
    }
