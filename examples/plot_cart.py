"""
Simple Site Time-series Plot
============================

Uses AERONet API to create a pandas dataframe with derived time column.
Then plots Total_AOD500nm as a function of time."""

# %%
# Prepare API
# -----------

import pyaeronet

api = pyaeronet.aeronet()

# %%
# Query AERONET
# -------------

opts = dict(
    site='Cart_Site', SDA20=1, AVG=10,
    year=2000, month=6, day=1, year2=2000, month2=6, day2=30,
    add_lst=True
)
df = api.to_dataframe(**opts)

# %%
# Plot AERONET
# ------------

ax = df.plot.scatter(x='time_lst', y='Total_AOD_500nm[tau_a]', figsize=(12, 4))
ax.set_title('{site} {year}-{month:02d}'.format(**opts))
ax.figure.savefig('cart.png')
