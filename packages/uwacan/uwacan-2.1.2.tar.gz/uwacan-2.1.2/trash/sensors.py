from . import positional

import xarray as xr
import numpy as np


def sensor(label, sensitivity=None, position=None, depth=None):
    data_vars = {}
    if sensitivity is not None:
        data_vars['sensitivity'] = sensitivity
    if position is not None:
        position = positional.position(position)
        data_vars['latitude'] = position.latitude
        data_vars['longitude'] = position.longitude
    if depth is not None:
        data_vars['depth'] = depth

    return xr.Dataset(data_vars=data_vars, coords={'sensor': label})


def sensor_array(*sensors, **kwargs):
    """Collects sensor information in an xarray.

    The function accepts two types of calls, positional sensors or keywords with dicts.
    The positional format is `sensor_array(sensor_1, sensor_2, ...)`
    where each sensor is an xarray with at least `sensor` containing the label for that sensor.
    Such xarrays can be created with the `sensor` function.
    The other format is keyword arguments with said labels as the keys, and a dictionary
    with the sensor information as the value, e.g.,

    ```
    sensor_array(
        soundtrap_1={'position': (58.25, 11.14), 'sensitivity': -182},
        soundtrap_2={'position': (58.26, 11.15), 'sensitivity': -183},
    )
    ```
    Note that labels that are not valid arguments can still be created using dict unpacking
    ```
    sensor_array(**{
        'SoundTrap 1': {'position': (58.25, 11.14), 'sensitivity': -182},
        'SoundTrap 2': {'position': (58.26, 11.15), 'sensitivity': -183},
    })
    """
    if kwargs:
        sensors = sensors + (
            sensor(label, **values)
            for label, values in kwargs.items()
        )
    sensors = xr.concat(sensors, dim='sensor')
    for key, value in sensors.items():
        if np.ptp(value.values) == 0:
            sensors[key] = value.mean()
    return sensors


def align_property_to_sensors(sensors, values, allow_scalar=False):
    sensor_names = sensors.sensor

    if isinstance(values, xr.DataArray):
        return values
    if allow_scalar:
        try:
            len(values)
        except TypeError:
            return values

    if len(values) != sensor_names.size:
        raise ValueError(f"Cannot assign {len(values)} values to {sensor_names.size} sensors")

    try:
        return xr.DataArray(values, coords={'sensor': sensor_names})
    except ValueError:
        pass
    return xr.DataArray([values[key] for key in sensor_names.values], coords={'sensor': sensor_names})
