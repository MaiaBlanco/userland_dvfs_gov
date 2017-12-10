from pypapi import papi_high as ph
from pypapi import events as pe

# high level api test:
print("Testing papi_high")
flops = ph.flops()
print("Flops:", flops)