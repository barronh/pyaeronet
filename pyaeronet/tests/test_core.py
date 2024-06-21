from .. import _data_types
import functools


def _testreturn(**kwds):
    from .. import aeronet
    api = aeronet()
    df = api.to_dataframe(**kwds)
    assert df.shape[0] > 0
    assert 'AERONET_Site' in df.columns
    return df


def _test(**kwds):
    _testreturn(**kwds)


for dt in _data_types:
    opts = {
        'site': 'Cart_Site',
        'year': 2000, 'month': 6, 'day': 1, 'hour': 10,
        'year2': 2000, 'month2': 6, 'day2': 1, 'hour2': 14,
        dt: 1, 'AVG': 20
    }
    globals()[f'test_site_data_type_{dt}'] = functools.partial(_test, **opts)

for avg in [10, 20]:
    opts = {
        'site': 'Cart_Site',
        'year': 2000, 'month': 6, 'day': 1,
        'year2': 2000, 'month2': 6, 'day2': 30,
        'SDA20': 1, 'AVG': avg
    }
    globals()[f'test_site_data_avg_{avg}'] = functools.partial(_test, **opts)


def test_all_data_type_AOD20():
    _test(
        AOD20=1, AVG=20,
        year=2000, month=6, day=1,
        year2=2000, month2=6, day2=14,
    )


def test_validate():
    try:
        _test(
            site='Cart_Site',
            year=2000, month=6, day=1
        )
        raise ValueError('should have failed')
    except KeyError:
        pass
    try:
        _test(
            site='Cart_Site',
            month=6, day=1, AOD20=1
        )
        raise ValueError('should have failed')
    except KeyError:
        pass
    try:
        _test(
            oopsy='?',
            month=6, day=1, AOD20=1
        )
        raise ValueError('should have failed')
    except KeyError:
        pass
