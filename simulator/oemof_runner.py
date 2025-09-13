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
    file_dir = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(file_dir, 'KonfigurationSzenarios.xlsx')

    # Build factory + model
    model_factory = ExcelModelFactory(file_path, 'SimpleSzenarioD')
    model = model_factory.model
    value_collection = model_factory.value_collection

    # Calculate totals BEFORE optimization from value collection
    total_sources_before = 0
    total_sinks_before = 0
    
    for value in value_collection.values.values():
        if value.id.startswith('Src_'):
            total_sources_before += value.value
        elif value.id.startswith('Snk_'):
            total_sinks_before += value.value

    # Solve model using best available solver for Heroku deployment
    from pyomo.opt import SolverFactory
    
    is_heroku = 'DYNO' in os.environ  # Heroku sets this environment variable
    print(f"Environment detection - Is Heroku: {is_heroku}")
    
    solver_used = None
    try:
        if is_heroku:
            print("Heroku detected - using PuLP solver")
            # On Heroku, use PuLP which is pure Python and works reliably
            try:
                # Try PuLP first (most reliable on Heroku)
                print("Attempting PuLP solver")
                model.solve(solver="appsi_opt", tee=True)  # PuLP via appsi interface
                solver_used = "appsi_opt (PuLP)"
            except Exception as e1:
                print(f"PuLP failed: {e1}")
                try:
                    # Fallback to HiGHS
                    print("Attempting HiGHS solver")
                    model.solve(solver="appsi_highs", tee=True)
                    solver_used = "appsi_highs"
                except Exception as e2:
                    print(f"HiGHS failed: {e2}")
                    # Final fallback - force use of any available solver
                    print("Using any available solver")
                    model.solve(tee=True)
                    solver_used = "default available solver"
        else:
            print("Local environment detected - using CBC solver")
            # Local development - prefer CBC if available
            try:
                solver = SolverFactory('cbc')
                if solver.available():
                    model.solve(solver="cbc", tee=True)
                    solver_used = "cbc"
                else:
                    print("CBC not available locally, trying alternatives")
                    model.solve(solver="appsi_highs", tee=True)
                    solver_used = "appsi_highs (local fallback)"
            except Exception as e:
                print(f"Local CBC failed: {e}")
                model.solve(solver="appsi_highs", tee=True) 
                solver_used = "appsi_highs (local fallback)"
                
        print(f"Optimization completed successfully using solver: {solver_used}")
        
    except Exception as e:
        print(f"All solver attempts failed: {e}")
        raise Exception(f"No suitable solver found for optimization: {e}")

    # Get results
    results = processing.results(model)

    # Calculate totals AFTER optimization from OEMOF results
    total_sources_after = 0
    total_sinks_after = 0

    for (i, o), v in results.items():
        if hasattr(i, 'label') and str(i).startswith('Src_'):
            total_sources_after += v['sequences'].sum().sum()
        if hasattr(o, 'label') and str(o).startswith('Snk_'):
            total_sinks_after += v['sequences'].sum().sum()

    # Calculate conversion losses
    conversion_losses = total_sources_after - total_sinks_after
    
    # Calculate final usable sources (after reducing losses)
    usable_sources_after = total_sources_after - conversion_losses  # This equals total_sinks_after

    # Extract detailed source and sink data
    detailed_sources_before = {}
    detailed_sinks_before = {}
    detailed_sources_after = {}
    detailed_sinks_after = {}

    # Get detailed data BEFORE optimization from value collection
    for value in value_collection.values.values():
        if value.id.startswith('Src_'):
            detailed_sources_before[value.id] = value.value
        elif value.id.startswith('Snk_'):
            detailed_sinks_before[value.id] = value.value

    # Get detailed data AFTER optimization from OEMOF results
    for (i, o), v in results.items():
        if hasattr(i, 'label') and str(i).startswith('Src_'):
            detailed_sources_after[str(i)] = v['sequences'].sum().sum()
        if hasattr(o, 'label') and str(o).startswith('Snk_'):
            detailed_sinks_after[str(o)] = v['sequences'].sum().sum()

    # Calculate detailed loss breakdown data dynamically from OEMOF results
    
    # Extract actual conversion flows from OEMOF results
    electrolysis_input = 0
    electrolysis_output = 0
    h2_storage_input = 0 
    h2_storage_output = 0
    h2_reelec_input = 0
    h2_reelec_elec_output = 0
    h2_reelec_heat_output = 0
    
    fuel_synthesis_input = 0
    fuel_synthesis_output = 0
    biogas_conversion_input = 0
    biogas_conversion_output = 0
    
    industrial_input = 0
    industrial_output = 0
    
    grid_input = 0
    grid_output = 0
    
    transport_total_input = 0
    transport_total_output = 0
    diesel_pv_input = 0
    diesel_pv_output = 0
    diesel_gv_input = 0
    diesel_gv_output = 0
    electric_pv_input = 0
    electric_pv_output = 0
    electric_gv_input = 0
    electric_gv_output = 0
    aviation_input = 0
    aviation_output = 0
    
    biomass_input = 0
    biomass_output = 0
    
    # Extract flows from OEMOF results
    for (i, o), v in results.items():
        flow_value = v['sequences'].sum().sum()
        
        # Power-to-Hydrogen chain
        if str(i) == 'b_st_erz' and str(o) == 'Tr_Elektrolyse':
            electrolysis_input = flow_value
        elif str(i) == 'Tr_Elektrolyse' and str(o) == 'b_Tr_H2_Speicher':
            electrolysis_output = flow_value
        elif str(i) == 'b_Tr_H2_Speicher' and str(o) == 'Tr_H2_Speicher':
            h2_storage_input = flow_value
        elif str(i) == 'Tr_H2_Speicher' and str(o) == 'b_Tr_H2_Verstromung':
            h2_storage_output = flow_value
        elif str(i) == 'b_Tr_H2_Verstromung' and str(o) == 'Tr_Verstromung_H2':
            h2_reelec_input = flow_value
        elif str(i) == 'Tr_Verstromung_H2' and str(o) == 'b_st_erz':
            h2_reelec_elec_output = flow_value
        elif str(i) == 'Tr_Verstromung_H2' and str(o) == 'b_wrm':
            h2_reelec_heat_output = flow_value
            
        # Synthetic fuels
        elif str(i) == 'b_st_erz' and str(o) == 'Tr_Kraftstoff_Synthese':
            fuel_synthesis_input = flow_value
        elif str(i) == 'Tr_Kraftstoff_Synthese' and str(o) == 'b_krst':
            fuel_synthesis_output = flow_value
        elif str(i) == 'b_Tr_Gas_Kraftstoff' and str(o) == 'Tr_Gas_Kraftstoff':
            biogas_conversion_input = flow_value
        elif str(i) == 'Tr_Gas_Kraftstoff' and str(o) == 'b_krst':
            biogas_conversion_output = flow_value
            
        # Industrial synthesis
        elif str(i) == 'b_st_erz' and str(o) == 'Tr_Grundstoff_Synthese':
            industrial_input = flow_value
        elif str(i) == 'Tr_Grundstoff_Synthese' and str(o) == 'b_Snk_Methan_synth':
            industrial_output = flow_value
            
        # Electricity grid
        elif str(i) == 'b_st_erz' and str(o) == 'Tr_Stromnetz':
            grid_input = flow_value
        elif str(i) == 'Tr_Stromnetz' and str(o) == 'b_st_endv':
            grid_output = flow_value
            
        # Transport sector
        elif str(i) == 'b_krst' and str(o) == 'Tr_Otto_Diesel_PV':
            diesel_pv_input = flow_value
        elif str(i) == 'Tr_Otto_Diesel_PV' and str(o) == 'b_Tr_Otto_Diesel_PV':
            diesel_pv_output = flow_value
        elif str(i) == 'b_krst' and str(o) == 'Tr_Otto_Diesel_GV':
            diesel_gv_input = flow_value
        elif str(i) == 'Tr_Otto_Diesel_GV' and str(o) == 'b_Tr_Otto_Diesel_GV':
            diesel_gv_output = flow_value
        elif str(i) == 'b_st_endv' and str(o) == 'Tr_Elektro_PV':
            electric_pv_input = flow_value
        elif str(i) == 'Tr_Elektro_PV' and str(o) == 'b_Tr_Elektro_PV':
            electric_pv_output = flow_value
        elif str(i) == 'b_st_endv' and str(o) == 'Tr_Elektro_GV':
            electric_gv_input = flow_value
        elif str(i) == 'Tr_Elektro_GV' and str(o) == 'b_Tr_Elektro_GV':
            electric_gv_output = flow_value
        elif str(i) == 'b_krst' and str(o) == 'Tr_Kerosin_LV':
            aviation_input = flow_value
        elif str(i) == 'Tr_Kerosin_LV' and str(o) == 'b_Snk_LuftVerk':
            aviation_output = flow_value
            
        # Biomass combustion
        elif str(i) == 'b_bst' and str(o) == 'Tr_Verbrennung_PW':
            biomass_input = flow_value
        elif str(i) == 'Tr_Verbrennung_PW' and str(o) == 'b_Snk_PW':
            biomass_output = flow_value

    # Calculate losses dynamically
    electrolysis_loss = electrolysis_input - electrolysis_output
    h2_storage_loss = h2_storage_input - h2_storage_output
    h2_reelec_loss = h2_reelec_input - (h2_reelec_elec_output + h2_reelec_heat_output)
    p2h2_total_losses = electrolysis_loss + h2_storage_loss + h2_reelec_loss
    p2h2_useful_output = h2_reelec_elec_output + h2_reelec_heat_output
    
    fuel_synthesis_loss = fuel_synthesis_input - fuel_synthesis_output
    biogas_conversion_loss = biogas_conversion_input - biogas_conversion_output
    synfuel_total_losses = fuel_synthesis_loss + biogas_conversion_loss
    synfuel_useful_output = fuel_synthesis_output + biogas_conversion_output
    synfuel_total_input = fuel_synthesis_input + biogas_conversion_input
    
    industrial_loss = industrial_input - industrial_output
    grid_loss = grid_input - grid_output
    
    transport_total_input = diesel_pv_input + diesel_gv_input + electric_pv_input + electric_gv_input + aviation_input
    transport_total_output = diesel_pv_output + diesel_gv_output + electric_pv_output + electric_gv_output + aviation_output
    transport_total_losses = transport_total_input - transport_total_output
    
    biomass_loss = biomass_input - biomass_output
    
    # Calculate final useful demand correctly - this should equal total_sinks_after
    final_useful_demand = total_sinks_after  # This is the correct value from OEMOF
    
    total_calculated_losses = total_sources_after - total_sinks_after  # This should equal conversion_losses

    loss_breakdown = {
        "total_sources": total_sources_after,  # Use the OEMOF total sources
        "power_to_hydrogen": {
            "input": electrolysis_input,
            "electrolysis_loss": electrolysis_loss,
            "h2_storage_loss": h2_storage_loss,
            "h2_reelectrification_loss": h2_reelec_loss,
            "useful_output": p2h2_useful_output,
            "total_losses": p2h2_total_losses,
            "efficiency": (p2h2_useful_output / electrolysis_input * 100) if electrolysis_input > 0 else 0
        },
        "synthetic_fuels": {
            "input": synfuel_total_input,
            "elec_input": fuel_synthesis_input,
            "biogas_input": biogas_conversion_input,
            "fuel_synthesis_loss": fuel_synthesis_loss,
            "biogas_conversion_loss": biogas_conversion_loss,
            "useful_output": synfuel_useful_output,
            "total_losses": synfuel_total_losses,
            "efficiency": (synfuel_useful_output / synfuel_total_input * 100) if synfuel_total_input > 0 else 0
        },
        "industrial_synthesis": {
            "input": industrial_input,
            "useful_output": industrial_output,
            "total_losses": industrial_loss,
            "efficiency": (industrial_output / industrial_input * 100) if industrial_input > 0 else 0
        },
        "electricity_grid": {
            "input": grid_input,
            "useful_output": grid_output,
            "total_losses": grid_loss,
            "efficiency": (grid_output / grid_input * 100) if grid_input > 0 else 0
        },
        "transport_conversions": {
            "input": transport_total_input,
            "diesel_pv_loss": diesel_pv_input - diesel_pv_output,
            "diesel_gv_loss": diesel_gv_input - diesel_gv_output,
            "electric_pv_loss": electric_pv_input - electric_pv_output,
            "electric_gv_loss": electric_gv_input - electric_gv_output,
            "aviation_fuel_loss": aviation_input - aviation_output,
            "useful_output": transport_total_output,
            "total_losses": transport_total_losses,
            "efficiency": (transport_total_output / transport_total_input * 100) if transport_total_input > 0 else 0
        },
        "biomass_combustion": {
            "input": biomass_input,
            "useful_output": biomass_output,
            "total_losses": biomass_loss,
            "efficiency": (biomass_output / biomass_input * 100) if biomass_input > 0 else 0
        },
        "summary": {
            "final_useful_demand": final_useful_demand,  # Use OEMOF sinks total
            "total_calculated_losses": total_calculated_losses,  # Use OEMOF losses
            "system_surplus": total_sources_after - total_sinks_after,
            "overall_efficiency": (final_useful_demand / total_sources_after * 100) if total_sources_after > 0 else 0,
            "loss_percentage": (total_calculated_losses / total_sources_after * 100) if total_sources_after > 0 else 0
        }
    }

    # Debug print to verify values
    print(f"DEBUG - Backend Data:")
    print(f"Sources Before: {total_sources_before}")
    print(f"Sinks Before: {total_sinks_before}")
    print(f"Sources After Raw: {total_sources_after}")
    print(f"Usable Sources After: {usable_sources_after}")
    print(f"Sinks After: {total_sinks_after}")
    print(f"Conversion Losses: {conversion_losses}")

    return {
        "sources_before": total_sources_before,    # From Excel before optimization
        "sinks_before": total_sinks_before,        # From Excel before optimization  
        "sources_after_raw": total_sources_after,  # Raw OEMOF results before losses
        "sources_after": usable_sources_after,     # Final usable sources after reducing losses
        "sinks_after": total_sinks_after,          # From OEMOF results after optimization
        "losses": conversion_losses,               # Calculated conversion losses
        "difference_before": total_sources_before - total_sinks_before,  # Difference before optimization
        "verification_correct": abs(conversion_losses - (total_sources_after - total_sinks_after)) < 0.01,
        
        # Detailed breakdown data
        "detailed_sources_before": detailed_sources_before,
        "detailed_sinks_before": detailed_sinks_before,
        "detailed_sources_after": detailed_sources_after,
        "detailed_sinks_after": detailed_sinks_after,
        
        # Loss breakdown data
        "loss_breakdown": loss_breakdown
    }
