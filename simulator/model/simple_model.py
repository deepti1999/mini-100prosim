import pandas as pd

from oemof.solph import Source, Sink, Bus, Flow, Model, EnergySystem, processing, views
from value.value_factory import *
from value.value_collection import ValueCollection

"""
Simulation of a simple model to get started with Oemof:
-------------------------------------------------------

                                      |
Solar PV FF (150 GWh) --------------->|
Formula: D_PV_FF = D015 * D100        |
                                      |---------------> El. Consumer (300 GWh)
                                      |                 Value: D_EL_CONS
Solar PV DF (100 GWh) --------------->|
Value: D_PV_DF                        |
                                      |

Optimization: Result for D_PV_FF = --> D015 = 2,0!

"""


# Definition of dedicated value factory (just for this model) with mockup data:
class MockupValueFactory(ValueFactory):

    def value(self, vid) -> Value:
        if vid == "D_PV_FF":
            return FormulaValue(vid, 'D015*D100', Unit.GWh, 'D015', self)
        elif vid == "D100":
            return SimpleValue(vid, 100, Unit.GWh)
        elif vid == "D015":
            return SimpleValue(vid, 1.5, Unit.noUnit)
        elif vid == "D_PV_DF":
            return SimpleValue(vid, 100, Unit.GWh)
        elif vid == "D_EL_CONS":
            return SimpleValue(vid, 300, Unit.GWh)


print("Start simple model...")

# define value collection:
value_collection = ValueCollection(MockupValueFactory())

# create energy system:
es = EnergySystem(timeindex=pd.date_range('1/1/2021', periods=1, freq='D'))

# and add electrical bus:
b_el = Bus(label="el_bus")
es.add(b_el)

#
# --- prepare oemof entities and add them to energySystem
#
d_pv_ff = value_collection.value('D_PV_FF').value
es.add(
    Source(label='D_PV_FF',
           outputs={b_el: Flow(nominal_value=int(d_pv_ff), max=1000)})   # default: max = 1
)
d_pv_df = value_collection.value('D_PV_DF').value
es.add(
    Source(label='D_PV_DF',
           outputs={b_el: Flow(nominal_value=int(d_pv_df), fix=1)})      # value is fixed in optimization
)
d_el_cons = value_collection.value('D_EL_CONS').value
es.add(
    Sink(label='D_EL_CONS',
         inputs={b_el: Flow(nominal_value=int(d_el_cons), fix=1)})       # value is fixed in optimization
)

#
# --- set up the oemof model:
#
om = Model(energysystem=es)

#
# --- print values in collection before optimization
#
print('')
print('Values in collection before model optimization:')
for value in value_collection.values.values():
    print('-', value)
print('')

#
# --- solve the energy model using the CBC solver
#
om.solve(solver='cbc', solve_kwargs={'tee': False})    # tee = True: show detailed log output

#
# --- get processing results
#
results = processing.results(om)

#
# --- set optimized values in collection to calculate 'containing' values
#
for src, tgt in om.flows.keys():
    for entity in (src, tgt):
        if entity.__class__ in (Source, Sink):
            entity_name = str(entity)                                           # get name of source or sink
            entity_value = views.node(results, entity)['sequences'].iloc[0][0]  # get value of source or sink
            value_collection.value(entity_name).value = entity_value            # set value in collection:
            # print(entity_name, ': ', entity_value)

#
# --- print values in collection after optimization
#
print('')
print('Values in collection after model optimization ((!): value was modified):')
for value in value_collection.values.values():
    print(value)

print('')
print('... has ended!')
