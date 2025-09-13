#!/usr/bin/env python
"""
Test script to verify OEMOF runner integration with Django
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from simulator.oemof_runner import run_oemof_scenario, format_energy_value

def test_oemof_integration():
    """Test the OEMOF runner with the Django environment"""
    
    print("Testing OEMOF integration with Django...")
    print("=" * 50)
    
    # Path to Excel file
    excel_path = './simulator/data/KonfigurationSzenarios.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel file not found: {excel_path}")
        return False
    
    print(f"✅ Excel file found: {excel_path}")
    
    # Run the scenario
    print("\nRunning OEMOF scenario...")
    results = run_oemof_scenario(excel_path, "SimpleSzenarioD")
    
    if results["success"]:
        print("✅ OEMOF optimization completed successfully!")
        print("\n📊 ENERGY BALANCE SUMMARY:")
        print(f"  Sources (before): {format_energy_value(results['sources_before'])}")
        print(f"  Sinks (before):   {format_energy_value(results['sinks_before'])}")
        print(f"  Sources (after):  {format_energy_value(results['sources_after'])}")
        print(f"  Sinks (after):    {format_energy_value(results['sinks_after'])}")
        print(f"  Conversion losses: {format_energy_value(results['conversion_losses'])}")
        
        print(f"\n🔍 VERIFICATION:")
        balance_check = results['energy_balance_check']
        print(f"  Sources - Losses = {format_energy_value(balance_check['sources_minus_losses'])}")
        print(f"  Equals Sinks =     {format_energy_value(balance_check['equals_sinks'])}")
        print(f"  Balanced: {'✅ Yes' if balance_check['balanced'] else '❌ No'}")
        
        print(f"\n🎯 OPTIMIZED VALUES:")
        for param, data in results['changed_values'].items():
            print(f"  {param}: {data['original']:.2f} → {data['optimized']:.2f} {data['unit']}")
        
        return True
    else:
        print(f"❌ OEMOF optimization failed: {results['message']}")
        return False

if __name__ == "__main__":
    success = test_oemof_integration()
    print(f"\n{'='*50}")
    print(f"Test {'PASSED' if success else 'FAILED'}")
