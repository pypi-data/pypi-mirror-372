"""Handling of timed sequences, time windows, and extracting time ranges of sequences."""

import datetime
import numpy as np
import abc

# TODO: kill this module and move the parsing and TimeWindow class into the positional module.
# It made more sense to have `Timestamped`, `Referenced`, `Sampled` only for position tracks,
# Everything else is sampled, but is not helped by the `TimedSequence` objects since
# indexing is no longer based on selecting a smaller range of in-memory data.


def parse_timestamp(stamp):
    stamp = ''.join(c for c in stamp if c in '1234567890')
    num_chars = len(stamp)
    year = int(stamp[0:4])
    month = int(stamp[4:6]) if num_chars > 4 else 1
    day = int(stamp[6:8]) if num_chars > 6 else 1
    hour = int(stamp[8:10]) if num_chars > 8 else 0
    minute = int(stamp[10:12]) if num_chars > 10 else 0
    second = int(stamp[12:14]) if num_chars > 12 else 0
    microsecond = int(stamp[14:18].ljust(6, '0')) if num_chars > 12 else 0
    return datetime.datetime(year, month, day, hour, minute, second, microsecond)


class TimedSequence(abc.ABC):
    @property
    @abc.abstractmethod
    def time(self):
        ...

    @property
    def start(self):
        return self._window.start

    @property
    def stop(self):
        return self._window.stop

    @property
    def duration(self):
        return self._window.duration

    @property
    def center(self):
        return self._window.center

    @abc.abstractmethod
    def time_range(self, start, stop):
        if isinstance(start, datetime.datetime):
            start = (start - self.start).total_seconds()

        if isinstance(stop, datetime.datetime):
            stop = (stop - self.start).total_seconds()

        if start < 0:
            raise ValueError('Cannot access signal before measurement start')
        if start > self.duration:
            raise ValueError('Cannot access signal after measurement stop')
        if stop < 0:
            raise ValueError('Cannot access signal before measurement start')
        if stop > self.duration:
            raise ValueError('Cannot access signal after measurement stop')

        return start, stop


class TimedstampedSequence(TimedSequence):
    def __init__(self, timestamps):
        self.timestamps = timestamps
        self._window = TimeWindow(start=timestamps[0], stop=timestamps[-1])

    @property
    def time(self):
        np.asarray([
            (stamp - self.start).total_seconds()
            for stamp in self.timestamps
        ])

    def time_range(self, start, stop):
        start, stop = super().time_range(start, stop)
        for idx, stamp in enumerate(self.timestamps):
            if (stamp - self.start).total_seconds() >= start:
                start_idx = idx
                break

        for idx, stamp in enumerate(self.timestamps[start_idx:], start_idx):
            if (stamp - self.start).total_seconds() >= stop:
                stop_idx = idx
                break

        return start_idx, stop_idx


class ReferencedSequence(TimedSequence):
    def __init__(self, times, reference):
        self._times = times
        self._reference = reference
        self._window = TimeWindow(
            start=reference + datetime.timedelta(seconds=times[0]),
            stop=reference + datetime.timedelta(seconds=times[-1]),
        )

    @property
    def time(self):
        return self._times - (self.start - self._reference).total_seconds()

    def time_range(self, start, stop):
        start, stop = super().time_range(start, stop)

        start_idx = np.searchsorted(self._times, start)
        stop_idx = np.searchsorted(self._times, stop)
        return start_idx, stop_idx


class SampledSequence(TimedSequence):
    def __init__(self, samplerate, start, num_samples):
        self.samplerate = samplerate
        self.num_samples = num_samples
        self._start = start
        self._window = TimeWindow(start=start, duration=num_samples / samplerate)

    @property
    def time(self):
        return np.arange(self.num_samples) / self.samplerate

    def time_range(self, start, stop):
        start, stop = super().time_range(start, stop)
        start_idx = round(start * self.samplerate)
        stop_idx = round(stop * self.samplerate)
        return start_idx, stop_idx


class TimeWindow:
    def __init__(self, start=None, stop=None, center=None, duration=None):
        if isinstance(start, str):
            start = parse_timestamp(start)
        if isinstance(stop, str):
            stop = parse_timestamp(stop)
        if isinstance(center, str):
            center = parse_timestamp(center)

        if None not in (start, stop):
            self.start = start
            self.stop = stop
            start = stop = None
        elif None not in (center, duration):
            self.start = center - datetime.timedelta(seconds=duration / 2)
            self.stop = center + datetime.timedelta(seconds=duration / 2)
            center = duration = None
        elif None not in (start, duration):
            self.start = start
            self.stop = start + datetime.timedelta(seconds=duration)
            start = duration = None
        elif None not in (stop, duration):
            self.stop = stop
            self.start = stop - datetime.timedelta(seconds=duration)
            stop = duration = None
        elif None not in (start, center):
            self.start = start
            self.stop = start + (center - start) / 2
            start = center = None
        elif None not in (stop, center):
            self.stop = stop
            self.start = stop - (stop - center) / 2
            stop = center = None

        if (start, stop, center, duration) != (None, None, None, None):
            raise ValueError('Cannot input more than two input arguments to a time window!')

    @property
    def duration(self):
        return (self.stop - self.start).total_seconds()

    @property
    def center(self):
        return self.start + datetime.timedelta(seconds=self.duration / 2)
