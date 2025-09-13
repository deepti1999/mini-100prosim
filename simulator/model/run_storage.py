# -*- coding: utf-8 -*-
"""
General description
-------------------
A basic example to show how to model a simple energy system with oemof.solph.
The following energy system is modeled:
                input/output  bgas     bel
                     |          |        |       |
                     |          |        |       |
 wind(FixedSource)   |------------------>|       |
                     |          |        |       |
 pv(FixedSource)     |------------------>|       |
                     |          |        |       |
 demand(Sink)        |<------------------|       |
                     |          |        |       |
 storage(Storage)    |<------------------|       |
                     |------------------>|       |
"""
import pandas as pd
import os
import logging
# import pprint as pp

from oemof.solph import EnergySystem, Bus, Sink, Source, Flow, Model, Investment, processing, views, helpers
from oemof.tools import economics
from oemof.solph.components import GenericStorage
from oemof.tools import logger

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_run_storage.log",
    screen_level=logging.INFO,
    file_level=logging.INFO,
)


logging.info("Initialize the energy system")
debug = False
timeindex = pd.date_range('1/1/2016', periods=365, freq='D')
energy_system = EnergySystem(timeindex=timeindex)

logging.info("Reading in data")
data = pd.read_csv(os.path.join(os.getcwd(), "..\\data\\Daten_Jahresgang.csv"))

sum_data = data['Constant'].sum()  # Columns are 'PV', 'Wind', 'Constant' and 'Demand_el'

logging.info("Create oemof objects")

# define bus
b_el = Bus(label='b_el')
energy_system.add(b_el)

name_es = 'Try6'

if name_es == 'Try6':
    val_src_pv = 613132
    val_src_wind = 511833
    val_demand_el = val_src_pv  # + val_src_wind  # + 100000  # only with + 100000

    # If the period is one year the equivalent periodical costs (epc) of an
    # investment are equal to the annuity. Use oemof's economic tools.
    epc_pv = economics.annuity(capex=1000, n=20, wacc=0.05)
    epc_storage = economics.annuity(capex=1000, n=20, wacc=0.05)

    # create excess component for the electricity bus to allow overproduction
    # snk_ex = Sink(label="snk_ex", inputs={b_el: Flow()})

    # create fixed source object representing pv power plants
    src_pv = Source(label="src_pv", outputs={b_el: Flow(fix=data["PV"], investment=Investment(ep_costs=epc_pv))})

    # create fixed source object representing wind power plants
    # src_wind = Source(label="src_wind", outputs={b_el: Flow(fix=data["Wind"], nominal_value=val_src_wind)})

    # create simple sink object representing the electrical demand
    snk_el = Sink(label="snk_el", inputs={b_el: Flow(fix=data["Demand_el"], nominal_value=val_demand_el)})

    # create storage object representing a battery
    sto_el = GenericStorage(label="sto_el",
                            inputs={b_el: Flow(variable_costs=0.0001)},
                            outputs={b_el: Flow()},
                            loss_rate=0.00,
                            # initial_storage_level=0,
                            # invest_relation_input_capacity=1 / 6,
                            # invest_relation_output_capacity=1 / 6,
                            inflow_conversion_factor=1,
                            outflow_conversion_factor=1,
                            investment=Investment(ep_costs=epc_storage))

    energy_system.add(src_pv, snk_el, sto_el)  # , snk_ex src_wind,

elif name_es == 'Try5':
    # Eingangsparameter
    val_src_pv = 613132
    val_demand_el = val_src_pv  # - 100000  # and with +- 100000
    max_src_ex = max(0.1, min(100, val_demand_el-val_src_pv))
    max_snk_ex = max(0.1, min(100, val_src_pv-val_demand_el))
    #
    # define sources:
    #
    src_pv = Source(label='src_pv',
                    outputs={b_el: Flow(fix=data['PV'],
                                        nominal_value=val_src_pv)})
    src_ex = Source(label='src_ex',
                    outputs={b_el: Flow(nominal_value=100000,
                                        max=100,
                                        variable_cost=1000,
                                        summed_max=max_src_ex
                                        )})
    snk_el = Sink(label='snk_el',
                  inputs={b_el: Flow(fix=data['Demand_el'],
                                     nominal_value=val_demand_el)})
    snk_ex = Sink(label='snk_ex',
                  inputs={b_el: Flow(nominal_value=100000,
                                     max=100,
                                     variable_cost=1000,
                                     summed_max=max_snk_ex
                                     )})
    nom_storage_cap = 10000000
    sto_el = GenericStorage(label='sto_el',
                            nominal_storage_capacity=nom_storage_cap,
                            inputs={b_el: Flow(nominal_value=nom_storage_cap/6,
                                               variable_cost=0)},
                            outputs={b_el: Flow(nominal_value=nom_storage_cap/6,
                                                variable_cost=0)}
                            )
    energy_system.add(src_pv, snk_el, sto_el, src_ex)

elif name_es == 'Try4':
    # Eingangsparameter
    val_src_pv = 613132
    val_demand_el = val_src_pv  # + 100000  # (and larger values)
    #
    # define sources:
    #
    src_pv = Source(label='src_pv', outputs={b_el: Flow(fix=data['PV'], nominal_value=val_src_pv)})
    src_ex = Source(label='src_ex',
                    outputs={b_el: Flow(nominal_value=1000, max=100, variable_cost=1000)}  # , summed_max=1
                    )
    snk_el = Sink(label='snk_el', inputs={b_el: Flow(fix=data['Demand_el'], nominal_value=val_demand_el)})
    # snk_ex = Sink(label='snk_ex',
    #               inputs={b_el: Flow(nominal_value=10000, max=100, variable_cost=1000)})
    nom_storage_cap = 10000000
    sto_el = GenericStorage(label='sto_el',
                            nominal_storage_capacity=nom_storage_cap,
                            inputs={b_el: Flow(nominal_value=nom_storage_cap/6, variable_cost=1)},
                            outputs={b_el: Flow(nominal_value=nom_storage_cap/6, variable_cost=1)}
                            )
    energy_system.add(src_pv, snk_el, sto_el, src_ex)  # src_ex,

elif name_es == 'Try3':
    # Eingangsparameter
    val_src_pv = 613132
    val_demand_el = 613131  # if >= val_src_pv: no conversion
    #
    # define sources:
    #
    src_pv = Source(label='src_pv', outputs={b_el: Flow(fix=data['PV'], nominal_value=val_src_pv)})
    snk_el = Sink(label='snk_el', inputs={b_el: Flow(fix=data['Demand_el'], nominal_value=val_demand_el)})
    snk_ex = Sink(label='snk_ex', inputs={b_el: Flow(nominal_value=10000, max=100, variable_cost=1)})
    sto_el = GenericStorage(label='sto_el',
                            nominal_storage_capacity=10000000,
                            inputs={b_el: Flow()},
                            outputs={b_el: Flow()},
                            loss_rate=0.000000001,
                            )
    energy_system.add(src_pv, snk_el, snk_ex, sto_el)

elif name_es == 'Try2':
    # Eingangsparameter
    val_src_pv = 613132
    val_demand_el = 613131  # if >= val_src_pv: no conversion
    #
    # define sources:
    #
    src_pv = Source(label='src_pv', outputs={b_el: Flow(fix=data['PV'], nominal_value=val_src_pv)})
    snk_el = Sink(label='snk_el', inputs={b_el: Flow(fix=data['Demand_el'], nominal_value=val_demand_el)})
    snk_ex = Sink(label='snk_ex', inputs={b_el: Flow(nominal_value=10000, max=100, variable_cost=1)})
    sto_el = GenericStorage(label='sto_el',
                            nominal_storage_capacity=10000000,
                            inputs={b_el: Flow()},
                            outputs={b_el: Flow()},
                            # loss_rate=0.0001,
                            # initial_storage_level=0.3,
                            # balanced=True,  # first=last value in time series
                            )
    energy_system.add(src_pv, snk_el, snk_ex, sto_el)

elif name_es == 'Try1':
    # Eingangsparameter
    val_src_pv = 613132
    val_demand_el = 550000
    #
    # define sources: work with unbalanced storage:
    #
    src_pv = Source(label='src_pv', outputs={b_el: Flow(fix=data['PV'], nominal_value=val_src_pv)})
    snk_el = Sink(label='snk_el', inputs={b_el: Flow(fix=data['Demand_el'], nominal_value=val_demand_el)})
    sto_el = GenericStorage(label='sto_el',
                            nominal_storage_capacity=6000000,  # 14022500, 14022500000,
                            inputs={b_el: Flow()},
                            outputs={b_el: Flow()},
                            loss_rate=0.0001,
                            initial_storage_level=0.35,  # 0.08,  # 0.34,
                            balanced=False,  # True: first=last value in time series
                            )
    energy_system.add(src_pv, snk_el, sto_el)

logging.info("Optimise the energy system")
# initialise the operational model
oemof_model = Model(energy_system)

if debug:
    filename = os.path.join(
        helpers.extend_basic_path("lp_files"), "run_storage.lp"
    )
    logging.info("Store lp-file in {0}.".format(filename))
    oemof_model.write(filename, io_options={"symbolic_solver_labels": True})

# results = oemof_model.results()  # value sequences before optimization

logging.info("Solve the optimization problem")
oemof_model.solve(solver='cbc', solve_kwargs={'tee': False})

# Ergebnisse
# results = processing.results(oemof_model)
# results = oemof_model.results()
# abc = processing.get_tuple(results)

# column_name = (('your_storage_label', 'None'), 'storage_content')
# sc = views.node(results, 'your_storage_label')['sequences'][column_name]

# # Ergebnisse für Speicher
# df_storage = views.node(results, 'sto_el')['sequences']

logging.info("Store the energy system with the results.")
# add results to the energy system to make it possible to store them.
energy_system.results["main"] = processing.results(oemof_model)
energy_system.results["meta"] = processing.meta_results(oemof_model)

# store energy system with results
energy_system.dump(dpath=None, filename=None)  # stored to $HOME\.oemof\es_dump.oemof directory

logging.info("Restore the energy system and the results.")
energy_system = EnergySystem()
energy_system.restore(dpath=None, filename=None)

# define an alias for shorter calls below (optional)
results = energy_system.results["main"]
sto_el = energy_system.groups["sto_el"]

# print a time slice of the state of charge
print("")
print("********* State of Charge (slice) *********")
print(results[(sto_el, None)]["sequences"]["2016-01-01":"2016-01-05"])
print(results[(sto_el, None)]["sequences"]["2016-12-25":"2016-12-30"])
print("")

# abc = views.net_storage_flow(results, node_type=GenericStorage)
# abc = results.get((b_el, snk_el))  # ["sequences"]["2016-01-01":"2016-01-05"]
# print(results[(sto_el, snk_el)]["sequences"]["2016-01-01":"2016-01-05"])

# abc = processing.parameter_as_dict(oemof_model)

# get all variables of a specific component/bus
ent_1 = views.node(results, "snk_el")  # sto_el, src_pv, snk_el
# ent_1 = views.node(results, ('b_el', 'snk_el'))  # sto_el, src_pv, snk_el
ent_2 = views.node(results, "src_pv")  # b_el
# ent_3 = views.node(results, "snk_el")  # b_el
ent_3 = views.node(results, "sto_el")  # sto_el
ent_b_el = views.node(results, "b_el")  # b_el

# plot the time series (sequences) of a specific component/bus
if plt is not None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ent_1["sequences"].plot(ax=ax, kind="line", drawstyle="steps-post")
    plt.legend(loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.25), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    ent_2["sequences"].plot(ax=ax, kind="line", drawstyle="steps-post")
    plt.legend(loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.25), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    ent_3["sequences"].plot(ax=ax, kind="line", drawstyle="steps-post")
    plt.legend(loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.25), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

    # fig, ax = plt.subplots(figsize=(10, 5))
    # ent_4["sequences"].plot(ax=ax, kind="line", drawstyle="steps-post")
    # plt.legend(loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.25), ncol=2)
    # fig.subplots_adjust(top=0.8)
    # plt.show()

    fig, ax = plt.subplots(figsize=(10, 5))
    ent_b_el["sequences"].plot(ax=ax, kind="line", drawstyle="steps-post")
    plt.legend(loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.3), ncol=2)
    fig.subplots_adjust(top=0.8)
    plt.show()

# # print the solver results
# print("********* Meta results *********")
# pp.pprint(energy_system.results["meta"])
# print("")

# print the sums of the flows around the electricity bus
print("********* Main results *********")
print(ent_b_el["sequences"].sum(axis=0))

# results = processing.results(oemof_model)
# abc = views.node(results, "sto_el")["scalars"]
# storage = views.node(results, "sto_el")["scalars"]["invest"]  # / 1e6
# print("Storage: ", storage)
# pv_src = views.node(results, "src_pv")["scalars"]["invest"]  # / 1e3
# print("PV: ", pv_src)

print('... done!')
