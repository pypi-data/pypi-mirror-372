import numpy as np
import scipy.signal
from ._core import TimePeriod
import xarray as xr


class SampleTimer:
    def __init__(self, xr_obj):
        if 'samples' not in xr_obj.coords:
            raise TypeError('.sampling accessor only avaliable for xarrays with samples dimention')
        self._xr_obj = xr_obj

    @property
    def rate(self):
        return self._xr_obj.coords['samples'].attrs['rate']

    @property
    def num(self):
        return self._xr_obj.coords['samples'].size

    @property
    def time_period(self):
        start_time = self._xr_obj.coords['samples'].attrs['start_time']
        duration = self.num / self.rate
        return TimePeriod(start=start, duration=duration)

    def time_subperiod(self, time=None, /, *, start=None, stop=None, center=None, duration=None):
        original_period = self.time_period
        new_period = original_period.subperiod(time, start=start, stop=stop, center=center, duration=duration)
        start = (new_period.start - original_period.start).total_seconds()
        stop = (new_period.stop - original_period.start).total_seconds()
        # Indices assumed to be seconds from start
        start = np.math.floor(start * self.samplerate)
        stop = np.math.ceil(stop * self.samplerate)

        new_obj = self._xr_obj.isel(samples=slice(start, stop))
        new_obj.coords['samples'].attrs['start_time'] = self._start_time.add(seconds=start / self.samplerate)
        return new_obj


class Data:
    def __init__(self, data, dims=None, coords=None, attrs=None):
        if not isinstance(data, xr.DataArray):
            data = xr.DataArray(data, dims=dims, coords=coords, attrs=attrs)
        self._data = data

    def __add__(self, other):
        if isinstance(other, Data):
            other = other._data
        return self._remake(self._data + data)
        # new = type(self)(data=self._data + data)
        # self._transfer_attrs(new)
        # return new

    def reduce(self, function, dim, **kwargs):
        return self._remake(self._data.reduce(function, dim, **kwargs))
        # new = type(self)(data=self._data.reduce(function, dim, **kwargs))
        # self._transfer_attrs(new)
        # return new 

    def _remake(self, data):
        return Data(data=data)

    @property
    def data(self):
        import warnings
        warnings.warn('The data property should probably not be used', category=DeprecationWarning)
        return self._data.data

    # def _transfer_attrs(self, other):
    #     pass


class TimeData(Data):
    @classmethod
    def calibrated(cls, data, calibration, **kwargs):
        data = np.asarray(data)
        calibration = np.asarray(calibration).astype('float32')
        c = 10**(calibration / 20) / 1e-6  # Calibration values are given as dB re. 1μPa
        c = c.reshape((-1,) + (1,) * (data.ndim - 1))
        if data.dtype in (np.int8, np.int16, np.int32, np.float32):
            c = c.astype(np.float32)

        calibrated = data / c
        obj = cls(data=calibrated, **kwargs)
        return obj

    def __init__(self, data, start_time=None, samplerate=None, **kwargs):
        super().__init__(data=data, **kwargs)
        if 'start_time' not in self._data.attrs:
            if start_time is None:
                raise TypeError('Start time has to be given as input argument if it is missing from the xarray data')
            self._data = self._data.assign_attrs(start_time=start_time)
        if 'samplerate' not in self._data.attrs:
            if samplerate is None:
                raise TypeError('Samplerate has to be given as input argument if it is missing from the xarray data')
            self._data = self._data.assign_attrs(samplerate=samplerate)

    @property
    def samplerate(self):
        return self._data.samplerate

    @property
    def num_samples(self):
        return self._data.time.size

    @property
    def time_period(self):
        return TimePeriod(start=self._data.start_time, duration=self.num_samples / self.samplerate)

    def time_subperiod(self, time=None, /, *, start=None, stop=None, center=None, duration=None):
        original_period = self.time_period
        new_period = original_period.subperiod(time, start=start, stop=stop, center=center, duration=duration)
        start = (new_period.start - original_period.start).total_seconds()
        stop = (new_period.stop - original_period.start).total_seconds()
        # Indices assumed to be seconds from start
        start = np.math.floor(start * self.samplerate)
        stop = np.math.ceil(stop * self.samplerate)

        return self._remake(self._data.isel(time=slice(start, stop)).assign_attrs(start_time=self._start_time.add(seconds=start / self.samplerate)))

    def _remake(self, data):
        if 'time' in data.dims:
            return TimeData(data=data, samplerate=self.samplerate, start_time=self.start_time)
        return Data(data=data)

    # def _transfer_attrs(self, other):
    #     super()._transfer_attrs(other)
    #     if isinstance(other, TimeData):
    #         other._data = other._data.assign_attrs(samplerate=self.samplerate, start_time=self.start_time)
    
    # def reduce(self, function, dim, **kwargs):
    #     new_data = self._data.reduce(function, dim, **kwargs)
    #     if 'time' in new_data.dims:
    #         new = TimeData(data=new_data)  # Will break since you don't pass all arguments
    #     else:
    #         new = Data(data=new_data)
    #     self._transfer_attrs(new)
    #     return new


class FrequencyData(Data):
    def __init__(self, data, frequency=None, bandwidth=None, **kwargs):
        super().__init__(data, **kwargs)
        if 'frequency' not in self._data.coords:
            if frequency is None:
                raise TypeError('Frequency vector has to be given as input argument if it is missing from the xarray data')
            self._data = self._data.assign_coords(frequency=frequency)
        if 'bandwidth' not in self._data.attrs:
            if bandwidth is None:
                raise TypeError('Bandwidth has to be given as input argument if it is missing from the xarray data')
            self._data = self._data.assign_attrs(bandwidth=bandwidth)     

    def _remake(self, data):
        if 'frequency' in data.dims:
            return FrequencyData(data=data, frequency=self.frequency, bandwidth=self.bandwidth)
        return Data(data=data)


class TimeFrequencyData(TimeData, FrequencyData):
    def __init__(self, data, start_time=None, samplerate=None, frequency=None, bandwidth=None, **kwargs):
        super().__init__(data, start_time=start_time, samplerate=samplerate, frequency=frequency, bandwidth=bandwidth, **kwargs)

    def _remake(self, data):
        if 'time' in data.dims and 'frequency' in data.dims:
            return TimeFrequencyData(
                data=data,
                start_time=self.start_time,
                samplerate=self.samplerate,
                frequency=self.frequency,
                bandwidth=self.bandwidth
            )
        elif 'time' in data.dims:
            return TimeData(
                data=data,
                start_time=self.start_time,
                samplerate=self.samplerate,
            )
        elif 'frequency' in data.dims:
            return FrequencyData(
                data=data,
                frequency=self.frequency,
                bandwidth=self.bandwidth
            )
        else:
            return Data(data=data)


class Spectrogram(TimeFrequencyData):
    @classmethod
    def from_time_data(cls, time_data, window_duration, window='hann', overlap=0.5):
        if not isinstance(time_data, TimeData):
            raise TypeError(f"Cannot calculate the spectrogram of object of type '{time_data.__class__.__name__}'")
        window_samples = round(window_duration * time_data.samplerate)
        overlap_samples = round(window_duration * overlap * time_data.samplerate)
        f, t, Sxx = scipy.signal.spectrogram(
            x=time_data._data.data,
            fs=time_data.samplerate,
            window=window,
            nperseg=window_samples,
            noverlap=overlap_samples,
        )
        return cls(
            data=Sxx.copy(),  # Using a copy here is a performance improvement in later processing stages.
            # The array returned from the spectrogram function is the real part of the original stft, reshaped.
            # This means that the array takes twice the memory (the imaginary part is still around),
            # and it's not contiguous which slows down filtering a lot.
            samplerate=time_data.samplerate / (window_samples - overlap_samples),
            start_time=time_data.time_period.start.add(seconds=t[0]),
            frequency=f,
            bandwidth=time_data.samplerate / window_samples,
        )
