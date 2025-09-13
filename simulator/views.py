from django.shortcuts import render
from .oemof_runner import run_oemof_scenario

def home(request):
    """Home page - Page 1"""
    return render(request, "home.html")

def results(request):
    data = run_oemof_scenario()   # This now runs the real OEMOF model
    return render(request, "results.html", {"data": data})
