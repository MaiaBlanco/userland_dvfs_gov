from pypapi import papi_high as ph
from pypapi import papi_low as papi
from pypapi import events

# high level api test:
print("Testing papi_high")
cntrs = ph.num_counters()
print("Num Counters:", cntrs)

papi.library_init()

evs = papi.create_eventset()
papi.add_event(evs, events.PAPI_TOT_CYC)
papi.add_event(evs, events.PAPI_L1_DCM)

papi.start(evs)

# Do some computation here

result = papi.stop(evs)
print(result)

papi.cleanup_eventset(evs)
papi.destroy_eventset(evs)