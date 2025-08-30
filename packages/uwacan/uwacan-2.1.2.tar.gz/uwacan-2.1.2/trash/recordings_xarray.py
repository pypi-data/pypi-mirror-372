# class _SampleTimer:
#     def __init__(self, xr_obj):
#         if 'time' not in xr_obj.dims:
#             raise TypeError(".sampling accessor only available for xarrays with 'time' coordinate")
#         self._xr_obj = xr_obj

#     @property
#     def rate(self):
#         return self._xr_obj.coords['time'].attrs['rate']

#     @property
#     def num(self):
#         return self._xr_obj.sizes['time']

#     @property
#     def window(self):
#         start = positional.time_to_datetime(self._xr_obj.time.data[0])
#         # Calculating duration from number and rate means the stop points to the sample after the last,
#         # which is more intuitive when considering signal durations etc.
#         return positional.TimeWindow(
#             start=start,
#             duration=self.num / self.rate,
#         )

#     def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
#         original_window = self.window
#         new_window = original_window.subwindow(time, start=start, stop=stop, center=center, duration=duration, extend=extend)
#         if isinstance(new_window, positional.TimeWindow):
#             start = (new_window.start - original_window.start).total_seconds()
#             stop = (new_window.stop - original_window.start).total_seconds()
#             # Indices assumed to be seconds from start
#             start = np.math.floor(start * self.rate)
#             stop = np.math.ceil(stop * self.rate)
#             idx = slice(start, stop)
#         else:
#             idx = (new_window - original_window.start).total_seconds()
#             idx = round(idx * self.rate)

#         new_obj = self._xr_obj.isel(time=idx)
#         return new_obj


# class _StampedTimer:
#     def __init__(self, xr_obj):
#         self._xr_obj = xr_obj

#     @property
#     def window(self):
#         start = positional.time_to_datetime(self._xr_obj.time.data[0])
#         stop = positional.time_to_datetime(self._xr_obj.time.data[-1])
#         return positional.TimeWindow(start=start, stop=stop)

#     def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
#         original_window = self.window
#         new_window = original_window.subwindow(time, start=start, stop=stop, center=center, duration=duration, extend=extend)
#         if isinstance(new_window, positional.TimeWindow):
#             start = new_window.start.in_tz('UTC').naive()
#             stop = new_window.stop.in_tz('UTC').naive()
#             return self._xr_obj.sel(time=slice(start, stop))
#         else:
#             return self._xr_obj.sel(time=new_window.in_tz('UTC').naive(), method='nearest')


# def _make_sampler(xr_obj):
#     if 'time' not in xr_obj.dims:
#         raise TypeError(".sampling accessor only available for xarrays with 'time' coordinate")
#     if 'rate' in xr_obj.time.attrs:
#         return _SampleTimer(xr_obj)
#     else:
#         return _StampedTimer(xr_obj)


# xr.register_dataarray_accessor('sampling')(_make_sampler)
# xr.register_dataset_accessor('sampling')(_make_sampler)

# def time_data(data, start_time, samplerate, dims=None, coords=None):
#     if not isinstance(data, xr.DataArray):
#         if dims is None:
#             if data.ndim == 1:
#                 dims = 'time'
#             else:
#                 raise ValueError(f'Cannot guess dimensions for time data with {data.ndim} dimensions')
#         data = xr.DataArray(data, dims=dims)

#     n_samples = data.sizes['time']
#     start_time = positional.time_to_np(start_time)
#     offsets = np.arange(n_samples) * 1e9 / samplerate
#     time = start_time + offsets.astype('timedelta64[ns]')
#     data = data.assign_coords(
#         time=('time', time, {'rate': samplerate}),
#         **{name: coord for (name, coord) in (coords or {}).items() if name != 'time'}
#     )

#     return data


# def frequency_data(data, frequency, bandwidth, dims=None, coords=None):
#     if not isinstance(data, xr.DataArray):
#         if dims is None:
#             if data.ndim == 1:
#                 dims = 'frequency'
#             else:
#                 raise ValueError(f'Cannot guess dimensions for frequency data with {data.ndim} dimensions')
#         data = xr.DataArray(data, dims=dims)
#     data = data.assign_coords(
#         frequency=frequency,
#         bandwidth=('frequency', np.broadcast_to(bandwidth, np.shape(frequency))),
#          **{name: coord for (name, coord) in (coords or {}).items() if name != 'frequency'}
#     )
#     return data


# def time_frequency_data(data, start_time, samplerate, frequency, bandwidth, dims=None, coords=None):
#     if not isinstance(data, xr.DataArray):
#         if dims is None:
#             raise ValueError('Cannot guess dimensions for time-frequency data')
#         data = xr.DataArray(data, dims=dims)
#     data = time_data(data, start_time=start_time, samplerate=samplerate)
#     data = frequency_data(data, frequency, bandwidth)
#     return data.assign_coords(**{name: coord for (name, coord) in (coords or {}).items() if name not in ('time', 'frequency', 'bandwidth')})

class Recording(abc.ABC):
    # class _Sampling(abc.ABC):
    #     def __init__(self, recording):
    #         self.recording = recording
    #
    #     @property
    #     @abc.abstractmethod
    #     def rate(self):
    #         ...
    #
    #     @property
    #     @abc.abstractmethod
    #     def window(self):
    #         ...
    #
    #     @abc.abstractmethod
    #     def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
    #         ...

    # self.sampling = self._Sampling(self)  # pylint: disable=abstract-class-instantiated

class RecordingArray(Recording):
    # class _Sampling(Recording._Sampling):
    #     @property
    #     def rate(self):
    #         rates = [recording.sampling.rate for recording in self.recording.recordings.values()]
    #         if np.ptp(rates) == 0:
    #             return rates[0]
    #         return xr.DataArray(rates, dims='sensor', coords={'sensor': list(self.recording.recordings.keys())})

    #     @property
    #     def window(self):
    #         windows = [recording.sampling.window for recording in self.recording.recordings.values()]
    #         return positional.TimeWindow(
    #             start=max(w.start for w in windows),
    #             stop=min(w.stop for w in windows),
    #         )

    #     def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
    #         subwindow = self.window.subwindow(time, start=start, stop=stop, center=center, duration=duration, extend=extend)
    #         return type(self.recording)(*[
    #             recording.sampling.subwindow(subwindow)
    #             for recording in self.recording.recordings.values()
    #         ])

    def __init__(self, *recordings):
        # self.sampling = self._Sampling(self)

class FileRecording(Recording):
        # class _Sampling(Recording._Sampling):
    #     @property
    #     def rate(self):
    #         return self.recording.files[0].samplerate

    #     @property
    #     def window(self):
    #         try:
    #             return self._window
    #         except AttributeError:
    #             self._window = positional.TimeWindow(
    #                 start=self.recording.files[0].start_time,
    #                 stop=self.recording.files[-1].stop_time,
    #             )
    #         return self._window

    #     def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
    #         original_window = self.window
    #         new_window = original_window.subwindow(time, start=start, stop=stop, center=center, duration=duration, extend=extend)
    #         new = type(self.recording)(
    #             files=self.recording.files,
    #             sensor=self.recording.sensor,
    #         )
    #         new.sampling._window = new_window
    #         return new
