from aiida_humanintheloop import HumanLoopWorkChain
from aiida.orm import Int
from aiida.engine import submit

pk = submit(HumanLoopWorkChain, max_iters=Int(10))
print(f"Submitted HumanLoopWorkChain with PK={pk}")

