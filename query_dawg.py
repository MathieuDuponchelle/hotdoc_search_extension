from dawg import FrozenDawg
from souper import filtered_frozen_lookup

FrozenDawg.filtered_lookup = filtered_frozen_lookup

with open('dumped.dawg', 'rb') as f:
    data = f.read()

fdawg = FrozenDawg(data)
exists = fdawg.filtered_lookup('website')
print(exists)
skipped = fdawg.filtered_lookup('website')
print(exists)
