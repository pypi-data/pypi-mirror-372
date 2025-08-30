import numpy as np
import xarray as xr
from . import positional


class _DataWrapper:
    @classmethod
    def _wrap_output(cls, data):
        if not isinstance(data, xr.DataArray):
            return data
        if 'time' in data.dims and 'frequency' in data.dims:
            return TimeFrequencyData(data)
        if 'time' in data.dims:
            return TimeData(data)
        if 'frequency' in data.dims:
            return FrequencyData(data)
        return data

    def __add__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data + other)

    def __radd__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other + self.data)

    def __sub__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data - other)

    def __rsub__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other - self.data)

    def __mul__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data * other)

    def __rmul__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other * self.data)

    def __truediv__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data / other)

    def __rtruediv__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other / self.data)

    def __floordiv__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data // other)

    def __rfloordiv__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other // self.data)

    def __pow__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data ** other)

    def __rpow__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other ** self.data)

    def __mod__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(self.data % other)

    def __rmod__(self, other):
        if isinstance(other, _DataWrapper):
            other = other.data
        return self._wrap_output(other % self.data)

    def __neg__(self):
        return self._wrap_output(-self.data)

    def __abs__(self):
        return self._wrap_output(abs(self.data))


def _assign_time_vector(data, start_time, samplerate):
    if samplerate is None:
        return data
    if start_time is None:
        if 'time' in data.coords:
            start_time = data.time[0].item()
        start_time = 'now'
    n_samples = data.sizes['time']
    start_time = positional.time_to_np(start_time)
    offsets = np.arange(n_samples) * 1e9 / samplerate
    time = start_time + offsets.astype('timedelta64[ns]')
    return data.assign_coords(time=('time', time, {'rate': samplerate}))


class TimeData(_DataWrapper):
    def __init__(self, data, start_time=None, samplerate=None, dims=None, coords=None):
        if not isinstance(data, xr.DataArray):
            if dims is None:
                if data.ndim == 1:
                    dims = 'time'
                else:
                    raise ValueError(f'Cannot guess dimensions for time data with {data.ndim} dimensions')
            data = xr.DataArray(data, dims=dims)

        data = data.assign_coords(coords)
        data = _assign_time_vector(data, samplerate=samplerate, start_time=start_time)
        self.data = data

    @property
    def samplerate(self):
        return self.data.time.rate

    @property
    def time_window(self):
        # Calculating duration from number and rate means the stop points to the sample after the last,
        # which is more intuitive when considering signal durations etc.
        return positional.TimeWindow(
            start=self.data.time.data[0],
            duration=self.data.sizes['time'] / self.samplerate,
        )

    def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
        original_window = self.time_window
        new_window = original_window.subwindow(time, start=start, stop=stop, center=center, duration=duration, extend=extend)
        if isinstance(new_window, positional.TimeWindow):
            start = (new_window.start - original_window.start).total_seconds()
            stop = (new_window.stop - original_window.start).total_seconds()
            # Indices assumed to be seconds from start
            start = np.math.floor(start * self.samplerate)
            stop = np.math.ceil(stop * self.samplerate)
            idx = slice(start, stop)
        else:
            idx = (new_window - original_window.start).total_seconds()
            idx = round(idx * self.samplerate)

        selected_data = self.data.isel(time=idx)
        return type(self)(selected_data)


def _assign_frequency_bandwidth_vectors(data, frequency, bandwidth):
    if frequency is None:
        return data
    coords = {'frequency': frequency}
    if bandwidth is not None:
        coords['bandwidth'] = ('frequency', np.broadcast_to(bandwidth, np.shape(frequency)))
    return data.assign_coords(coords)


class FrequencyData(_DataWrapper):
    def __init__(self, data, frequency=None, bandwidth=None, dims=None, coords=None, **kwargs):
        if not isinstance(data, xr.DataArray):
            if dims is None:
                if data.ndim == 1:
                    dims = 'frequency'
                else:
                    raise ValueError(f'Cannot guess dimensions for frequency data with {data.ndim} dimensions')
            data = xr.DataArray(data, dims=dims)
        data = data.assign_coords(coords)
        data = _assign_frequency_bandwidth_vectors(data, frequency=frequency, bandwidth=bandwidth)
        self.data = data

    def estimate_bandwidth(self):
        frequency = np.asarray(self.data.frequency)
        # Check if the frequency array seems linearly or logarithmically spaced
        if frequency[0] == 0:
            diff = frequency[2:] - frequency[1:-1]
            frac = frequency[2:] / frequency[1:-1]
        else:
            diff = frequency[1:] - frequency[:-1]
            frac = frequency[1:] / frequency[:-1]
        diff_err = np.std(diff) / np.mean(diff)
        frac_err = np.std(frac) / np.mean(frac)
        # Note: if there are three values and the first is zero, the std is 0 for both.
        # The equals option makes us end up in the linear frequency case.
        if diff_err <= frac_err:
            # Central differences, with forwards and backwards at the ends
            central = (frequency[2:] - frequency[:-2]) / 2
            first = frequency[1] - frequency[0]
            last = frequency[-1] - frequency[-2]
        else:
            # upper edge is at sqrt(f_{l+1} * f_l), lower edge is at sqrt(f_{l-1} * f_l)
            # the difference simplifies as below.
            central = (frequency[2:]**0.5 - frequency[:-2]**0.5) * frequency[1:-1]**0.5
            # extrapolating to one bin below lowest and one above highest using constant ratio
            # the expression above then simplifies to the expressions below
            first = (frequency[1] - frequency[0]) * (frequency[0] / frequency[1])**0.5
            last = (frequency[-1] - frequency[-2]) * (frequency[-1] / frequency[-2])**0.5
        bandwidth = np.concatenate([[first], central, [last]])
        return xr.DataArray(bandwidth, coords={'frequency': self.data.frequency})


class TimeFrequencyData(TimeData, FrequencyData):
    def __init__(self, data, start_time=None, samplerate=None, frequency=None, bandwidth=None, dims=None, coords=None, **kwargs):
        if not isinstance(data, xr.DataArray):
            if dims is None:
                raise ValueError('Cannot guess dimensions for time-frequency data')
            data = xr.DataArray(data, dims=dims)
        data = data.assign_coords(coords)
        data = _assign_time_vector(data, samplerate=samplerate, start_time=start_time)
        data = _assign_frequency_bandwidth_vectors(data, frequency=frequency, bandwidth=bandwidth)
        self.data = data
