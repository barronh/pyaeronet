"""
Example Evaluation of EQUATES CMAQ AOD
======================================

Uses EQUATES and AERONet from APIs that create xarray and pandas
data structure.  The final output is a comparison between AERONet
L2 AOD_500nm and PHOTDIAG1 AOD550 both spatially as a monthly average
and as a scatter plot of hourly values.
"""

# %%
# Import Libraries
# ----------------

import pycno
import pyproj
import pyrsig
import pyaeronet
import matplotlib.pyplot as plt

# %%
# Load Data and Projection Info
# -----------------------------

aeronet = pyaeronet.aeronet()
aeronetdf = aeronet.to_dataframe(
    outpath='aeronet_L2_20190101_20190107.txt', AOD20=1, AVG=10,
    year=2019, month=1, day=1,
    year2=2019, month2=1, day2=7,
)
rsig = pyrsig.RsigApi()
eqds = rsig.to_ioapi(
    'cmaq.equates.conus.integrated.AOD550',
    bdate='2019-01-01T00', edate='2019-01-07T23:59:59'
)
proj = pyproj.Proj(eqds.crs_proj4)
cno = pycno.cno(proj=proj)
aeronetdf['x'], aeronetdf['y'] = proj(
    aeronetdf['Site_Longitude(Degrees)'], aeronetdf['Site_Latitude(Degrees)']
)

# %%
# Pair EQUATES w/ AERONet in Domain
# ---------------------------------

eaeronetdf = aeronetdf.query(
    f'x >= 0 and x <= {eqds.NCOLS}'
    f' and y >= 0 and y <= {eqds.NROWS}'
).copy()
eaeronetdf['COL'] = eaeronetdf['x'].astype('i')
eaeronetdf['ROW'] = eaeronetdf['y'].astype('i')
tidx = (eaeronetdf['Day_of_Year(Fraction)'] * 24 - 24).astype('i').to_xarray()
jidx = eaeronetdf['ROW'].astype('i').to_xarray()
iidx = eaeronetdf['COL'].astype('i').to_xarray()
ataeronet = eqds['AOD550'].isel(TSTEP=tidx, ROW=jidx, COL=iidx)
eaeronetdf['CMAQ_AOD550'] = ataeronet.values


# %%
# Create AERONet Averages
# -----------------------

paeronetcdf = eaeronetdf.groupby(['ROW', 'COL']).agg(
    AOD_500nm=('AOD_500nm', 'mean'), count=('AOD_500nm', 'count')
).query('count > 25').reset_index()

fig, axx = plt.subplots(1, 2, figsize=(12, 4))
qm = eqds['AOD550'].mean('TSTEP').plot(ax=axx[0])
paeronetcdf.plot.scatter(
    x='COL', y='ROW', c='AOD_500nm', ax=axx[0], edgecolor='w',
    norm=qm.norm, cmap=qm.cmap, colorbar=False
)
cno.drawstates(ax=axx[0])
eaeronetdf.plot.hexbin(
    x='CMAQ_AOD550', y='AOD_500nm', mincnt=1, cmap='viridis', ax=axx[1]
)
vmax = eaeronetdf[['CMAQ_AOD550', 'AOD_500nm']].max().max()
vmin = min(0, eaeronetdf[['CMAQ_AOD550', 'AOD_500nm']].min().min())
axx[1].set(
    facecolor='gainsboro', xlim=(vmin, vmax), ylim=(vmin, vmax), aspect=1
)
fig.savefig('equates_aeronet.png')
