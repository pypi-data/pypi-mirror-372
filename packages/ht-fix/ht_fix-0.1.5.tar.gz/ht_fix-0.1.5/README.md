# ht-fix

Convert messy basketball heights into **inches** with clamping.

```python
from ht_fix import fix_height
fix_height("6-7")                 # 79.0
fix_height(["4-Jun", "200 cm"])   # [76.0, 78.740157...]
df["ht_in"] = fix_height(df["ht"])  # clamps outside 5–8 ft to NaN
