import numpy as np
import scipy.signal
from ._core import TimePeriod
import abc


class Data:
    def __init__(self, data, dims):
        self.data = data
        self.dims = dims

    def _dims_to_axes(self, dim):
        if isinstance(dim, (int, str)):
            dim = [dim]
        included_axes = []
        for ax in dim:
            if isinstance(ax, str):
                ax = self.dims.index(ax)
            included_axes.append(ax)
        included_axes = tuple(included_axes)
        excluded_dims = tuple(dim for idx, dim in enumerate(self.dims) if idx not in included_axes)
        return included_axes, excluded_dims

    def reduce(self, function, dim, *args, **kwargs):
        reduce_axes, new_dims = self._dims_to_axes(dim)
        data = function(self.data, axis=reduce_axes, *args, **kwargs)
        
        if not isinstance(data, Data):
            try:
                data = type(self)(data=data, dims=new_dims)
            except TypeError:
                data = Data(data=data, dims=new_dims)
        return data


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

    def __init__(self, data, start_time, samplerate, dims=None, *args, **kwargs):
        self._start_time = start_time
        self.samplerate = samplerate
        
        if dims is None:
            if data.ndim == 1:
                dims = 'time',
            elif data.ndim == 2:
                dims = 'channels', 'time'

        super().__init__(data=data, dims=dims, *args, **kwargs)

    @property
    def time_period(self):
        return TimePeriod(start=self._start_time, duration=self.data.shape[-1] / self.samplerate)

    def time_subperiod(self, time=None, /, *, start=None, stop=None, center=None, duration=None):
        window = self.time_period.subperiod(time, start=start, stop=stop, center=center, duration=duration)
        start = (window.start - self._start_time).total_seconds()
        stop = (window.stop - self._start_time).total_seconds()
        # Indices assumed to be seconds from start
        start = np.math.floor(start * self.samplerate)
        stop = np.math.ceil(stop * self.samplerate)

        return type(self)(
            data=self.data[..., start:stop],
            start_time=self._start_time.add(seconds=start / self.samplerate),
            samplerate=self.samplerate,
            dims=self.dims,
        )

    def reduce(self, function, dim, *args, **kwargs):
        reduce_axes, new_dims = self._dims_to_axes(dim)
        data = function(self.data, axis=reduce_axes, *args, **kwargs)
        
        if not isinstance(data, Data):
            if 'time' in new_dims:
                data = TimeData(data, start_time=self.start_time, samplerate=self.samplerate, dims=new_dims)
            else:
                data = Data(data, dims=new_dims)
        return data


class FrequencyData(Data):
    def __init__(self, data, frequency, bandwidth, dims=None, *args, **kwargs):
        self.frequency = frequency
        self.bandwidth = bandwidth

        if dims is None:
            if data.ndim == 1:
                dims = 'frequency',
            elif data.ndim == 2:
                dims = 'channels', 'frequency'

        super().__init__(data=data, dims=dims, *args, **kwargs)

    def reduce(self, function, dim, *args, **kwargs):
        reduce_axes, new_dims = self._dims_to_axes(dim)
        data = function(self.data, axis=reduce_axes, *args, **kwargs)

        if not isinstance(data, Data):
            if 'frequency' in new_dims:
                data = FrequencyData(data, frequency=self.frequency, bandwidth=self.bandwidth, dims=new_dims)
            else:
                data = Data(data, dims=new_dims)
        return data


class TimeFrequencyData(Data):
    def __init__(self, data, start_time, samplerate, frequency, bandwidth, dims=None, *args, **kwargs):
        self.frequency = frequency
        self.bandwidth = bandwidth
        self._start_time = start_time
        self.samplerate = samplerate

        if dims is None:
            if data.ndim == 2:
                dims = 'frequency', 'time'
            elif data.ndim == 3:
                dims = 'channels', 'frequency', 'time'

        super().__init__(data=data, dims=dims, *args, **kwargs)

    @property
    def time_period(self):
        return TimePeriod(start=self._start_time, duration=self.data.shape[-1] / self.samplerate)

    def time_subperiod(self, time=None, /, *, start=None, stop=None, center=None, duration=None):
        window = self.time_period.subperiod(time, start=start, stop=stop, center=center, duration=duration)
        start = (window.start - self._start_time).total_seconds()
        stop = (window.stop - self._start_time).total_seconds()
        # Indices assumed to be seconds from start
        start = np.math.floor(start * self.samplerate)
        stop = np.math.ceil(stop * self.samplerate)
        return type(self)(
            data=self.data[..., start:stop],
            start_time=self._start_time.add(seconds=start / self.samplerate),
            samplerate=self.samplerate,
            frequency=self.frequency,
            bandwidth=self.bandwidth,
            dims=self.dims,
        )

    def reduce(self, function, dim, *args, **kwargs):
        reduce_axes, new_dims = self._dims_to_axes(dim)
        data = function(self.data, axis=reduce_axes, *args, **kwargs)

        if not isinstance(data, Data):
            if 'frequency' in new_dims and 'time' in new_dims:
                data = TimeFrequencyData(
                    data,
                    start_time=self.start_time,
                    samplerate=self.samplerate,
                    frequency=self.frequency,
                    bandwidth=self.bandwidth,
                    dims=new_dims,
                )
            elif 'frequency' in new_dims:
                data = FrequencyData(data, frequency=self.frequency, bandwidth=self.bandwidth, dims=new_dims)
            elif 'time' in new_dims:
                data = TimeData(data, start_time=self.start_time, samplerate=self.samplerate, dims=new_dims)
            else:
                data = Data(data, dims=new_dims)
        return data


class Spectrogram(TimeFrequencyData):
    @classmethod
    def from_time_data(cls, time_data, window_duration, window='hann', overlap=0.5):
        if not isinstance(time_data, TimeData):
            raise TypeError(f"Cannot calculate the spectrogram of object of type '{time_data.__class__.__name__}'")
        window_samples = round(window_duration * time_data.samplerate)
        overlap_samples = round(window_duration * overlap * time_data.samplerate)
        f, t, Sxx = scipy.signal.spectrogram(
            x=time_data.data,
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
