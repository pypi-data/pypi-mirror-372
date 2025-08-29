## LCV Schedule Creater
Electric LCV schedule tool

**LCVScheduleCreater** is a Python-based tool designed for the creation of schedules for electric light commercial vehicles (LCV)

## Installation
**1.** Create a new environment or use your own environment and install: Pip install efleetscheduler


## How to use the tool
You can use the entire tool by running the notebook:
- notebooks/Schedule Generation Module.ipynb to create schedules for an electric LCV fleet

## Configurations

The software configuration is structured around four sections that manage the generation of schedules:

Environement configuration (env_config):
    - "original_seed" , is the seed for for random generation of schedulers 
    - "gen_start_date": "yyyy-mm-dd 00:00:00",  start date
    - "gen_end_date", end date
    - "freq": "h",  'h' means hourly frequency. .
    - "EVs", is the number of electric vehicles in the fleet
    - "consumption_factor_file", is path to the CSV file with energy consumption factor

 Schedule generator configurations (sch_config): Define the parameters required to generate the travel and charging patterns for each vehicle in the LCV fleet.
    - "Vehicles number", is Number of vehicles in the fleet
    - "Type of schedule": {"type a": n, "type b": n, "type c": n},  # Define the number of vehciles with each type of schedule in the fleet. (C is for costum and you need to enter the characteristic in Costum Schedule)
    - "Type of vehicle": {"Renault": n, "Pegeaut": n},  # Renault or Peugeut
    - "Company type": companytype.Costum, # Types of company: Distribution, LineHaul, CraftServWithGoods, CraftServWithoutGoods, Food, Mail, Building, Highdistance, Generalcargo, Nogoods, Costum
    - "Schedule name", Name of the schedule


## Citation
If you use , please cite:
Gil Ribeiro, C. (2025). eFleetScheduler V1.0.1 (V1.0.1). Zenodo. https://doi.org/10.5281/zenodo.16992450