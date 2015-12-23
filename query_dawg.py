import sys

from dawg import FrozenDawg
from create_index import filtered_frozen_lookup

FrozenDawg.filtered_lookup = filtered_frozen_lookup

with open('dumped.dawg', 'rb') as f:
    data = f.read()

fdawg = FrozenDawg(data)
print(fdawg.filtered_lookup(sys.argv[1]))
