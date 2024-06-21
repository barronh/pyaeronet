__doc__ = """pyaeronet
---------

pyaeronet.aeronet is an api interface for python. The goal is to make it easy
to get AERONET data.

See https://aeronet.gsfc.nasa.gov/print_web_data_help_v3_new.html for more
details on the underlying webapi.

Example
-------

.. code-block:: python

    import pyaeronet
    
    api = pyaeronet.aeronet()
    df = api.to_dataframe(
        site='Cart_Site', SDA20=1, AVG=10,
        year=2000, month=6, day=1,
        year2=2000, month2=6, day2=30,
        add_lst=True
    )
    ax = df.plot.scatter(x='time_lst', y='Total_AOD_500nm[tau_a]')
    ax.figure.savefig('cart.png')
"""
__version__ = '0.1.0'

_data_types = [
    'AOD10', 'AOD15', 'AOD20', 'SDA10', 'SDA15', 'SDA20',
    'TOT10', 'TOT15', 'TOT20',
]
_reqopts = [
    'AVG', 'year', 'month', 'day',
]
_opts = [
    'hour', 'year2', 'month2', 'day2', 'hour2',
    'site', 'lat1', 'lat2', 'lon1', 'lon2',
    'lunar_merge', 'ldp_year', 'ldp_month', 'ldp_day',
    'if_no_html'
]
_knownopts = set(_reqopts + _data_types + _opts)


def _aeronet_read(path, add_utc=False, add_lst=False):
    import pandas as pd
    df = pd.read_csv(path, skiprows=5, na_values=[-999])
    df.columns = [k.strip() for k in df.columns]
    if add_lst or add_utc:
        try:
            ts = df['Date(dd:mm:yyyy)'] + 'T' + df['Time(hh:mm:ss)']
            utc = pd.to_datetime(ts, format='%d:%m:%YT%H:%M:%S')
        except KeyError:
            ts = df['Date_(dd:mm:yyyy)'] + 'T' + df['Time_(hh:mm:ss)']
            utc = pd.to_datetime(ts, format='%d:%m:%YT%H:%M:%S')
        if add_utc:
            df['time_utc'] = utc
        if add_lst:
            offset = df['Site_Longitude(Degrees)'] // 15
            df['time_lst'] = utc + pd.to_timedelta(offset, unit='h')

    return df


class aeronet:
    def __init__(self, apiroot=None, **kwds):
        """
        Arguments
        ---------
        apiroot : str or None
            If None, defaults to https://aeronet.gsfc.nasa.gov/cgi-bin/
            print_web_data_v3
        kwds : mappable
            If provided, used as default options for subsequent calls.
        """
        if apiroot is None:
            apiroot = 'https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3'
        self._apiroot = apiroot
        self._opts = {}
        self.set_defopts(**kwds)

    def set_defopts(self, kwargs=None, **kwds):
        """
        Arguments
        ---------
        kwargs : mappable
            If provided, used as params to web api.
        kwds : mappable
            If provided, combined with kwargs as params to web api.
        """
        self._opts = self._validate(kwargs, required=False, **kwds)
        self._opts.setdefault('if_no_html', 1)

    def _validate(self, kwargs=None, required=True, **kwds):
        """
        Loads defaults from kwds at initialization and defaults AVG to 10.
        Then checks required keys are present

        Arguments
        ---------
        kwargs : mappable
            If provided, used as params to web api.
        kwds : mappable
            If provided, combined with kwargs as params to web api.
        required : bool
            Confirm that all required arguments are provided.
        """
        opts = {k: v for k, v in self._opts.items()}
        opts.update(kwds)
        if kwargs is not None:
            opts.update(kwargs)
        opts.setdefault('AVG', 10)
        if required:
            reqmiss = set(_reqopts).difference(opts)
            if len(reqmiss) > 0:
                raise KeyError(f'Missing required keys {reqmiss}')
            for key in _data_types:
                if key in opts:
                    break
            else:
                raise KeyError(f'Missing required data_type: {_data_types}')
        unknown = set(opts).difference(_knownopts)
        if len(unknown) > 0:
            raise KeyError(f'Unknown options {unknown}')

        return opts

    def _get(self, kwargs=None, **kwds):
        """
        Arguments
        ---------
        kwargs : mappable
            If provided, used as params to web api.
        kwds : mappable
            If provided, combined with kwargs as params to web api.
        """
        import requests
        opts = self._validate(kwargs, **kwds)
        r = requests.get(self._apiroot, params=opts)
        r.raise_for_status()
        return r

    def to_dataframe(
        self, kwargs=None, outpath=None, add_utc=False, add_lst=False, **kwds
    ):
        f"""
        Arguments
        ---------
        kwargs : mappable
            If provided, used as params to web api.
        kwds : mappable
            If provided, combined with kwargs as params to web api.
            See https://aeronet.gsfc.nasa.gov/print_web_data_help_v3_new.html
            for details about available kwds ({_knownopts})
        outpath : str
            Path to store retrieved data or retrieve if cached.
        add_utc : bool
            If True, add time_utc column.
        add_lst : bool
            If True, add time_lst column with utc offset derived from
            Site_Longitude(Degrees)

        Returns
        -------
        df : pandas.DataFrame
            DataFrame from AERONET v3 Web-API with optionally derived time
            columns
        """
        import os
        import io
        import warnings

        if outpath is not None and os.path.exists(outpath):
            warnings.warn(f'using cached {outpath}')
            return _aeronet_read(outpath, add_utc=add_utc, add_lst=add_lst)

        r = self._get(**kwds)
        if outpath is not None:
            outpath = os.path.realpath(outpath)
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            with open(outpath, 'wb') as outf:
                outf.write(r.content)
            return _aeronet_read(outpath, add_utc=add_utc, add_lst=add_lst)
        else:
            fobj = io.BytesIO(r.content)
            return _aeronet_read(fobj, add_utc=add_utc, add_lst=add_lst)
