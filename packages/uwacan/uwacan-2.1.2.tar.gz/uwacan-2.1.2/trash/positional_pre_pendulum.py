"""Handles positional tracks.

This manages logs over positions of measurement objects via e.g. GPS.
Some of the operations include smoothing data, calculating distances,
and reading log files.
"""

import abc
import numpy as np
import scipy.interpolate
import scipy.signal
from geographiclib.geodesic import Geodesic
# from . import timestamps
import datetime
import dateutil
import bisect
geod = Geodesic.WGS84


one_knot = 1.94384


def parse_timestamp(stamp):
    return dateutil.parser.parse(stamp)
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


class TimeWindow:
    def __init__(self, start=None, stop=None, center=None, duration=None):
        if isinstance(start, str):
            start = parse_timestamp(start)
        if isinstance(stop, str):
            stop = parse_timestamp(stop)
        if isinstance(center, str):
            center = parse_timestamp(center)

        if None not in (start, stop):
            self._start = start
            self._stop = stop
            start = stop = None
        elif None not in (center, duration):
            self._start = center - datetime.timedelta(seconds=duration / 2)
            self._stop = center + datetime.timedelta(seconds=duration / 2)
            center = duration = None
        elif None not in (start, duration):
            self._start = start
            self._stop = start + datetime.timedelta(seconds=duration)
            start = duration = None
        elif None not in (stop, duration):
            self._stop = stop
            self._start = stop - datetime.timedelta(seconds=duration)
            stop = duration = None
        elif None not in (start, center):
            self._start = start
            self._stop = start + (center - start) / 2
            start = center = None
        elif None not in (stop, center):
            self._stop = stop
            self._start = stop - (stop - center) / 2
            stop = center = None

        if (start, stop, center, duration) != (None, None, None, None):
            raise ValueError('Cannot input more than two input arguments to a time window!')

    def __repr__(self):
        return f'TimeWindow(start={self.start}, stop={self.stop})'

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def duration(self):
        return (self.stop - self.start).total_seconds()

    @property
    def center(self):
        return self.start + datetime.timedelta(seconds=self.duration / 2)

    def __contains__(self, other):
        if isinstance(other, TimeWindow):
            return (other.start >= self.start) and (other.stop <= self.stop)
        if isinstance(other, Position):
            return self.start <= other.timestamp <= self.stop
        if isinstance(other, datetime.datetime):
            return self.start <= other <= self.stop
        raise TypeError(f'Cannot check if {other.__class__.__name__} is within a time window')


class Position:
    def __init__(self, latitude, longitude, timestamp=None):
        self._latitude = latitude
        self._longitude = longitude
        self._timestamp = timestamp

    @classmethod
    def from_degrees_minutes_seconds(cls, *args):
        if len(args) == 2:
            latitude, longitude = args
        elif len(args) == 4:
            latitude_degrees, latitude_minutes, longitude_degrees, longitude_minutes = args
            latitude = latitude_degrees + latitude_minutes / 60
            longitude = longitude_degrees + longitude_minutes / 60
        elif len(args) == 6:
            latitude_degrees, latitude_minutes, latitude_seconds, longitude_degrees, longitude_minutes, longitude_seconds = args
            latitude = latitude_degrees + latitude_minutes / 60 + latitude_seconds / 3600
            longitude = longitude_degrees + longitude_minutes / 60 + longitude_seconds / 3600
        return cls(latitude=latitude, longitude=longitude)

    def __repr__(self):
        lat = f'latitude={self.latitude}'
        lon = f', longitude={self.longitude}'
        time = f', timestamp={self.timestamp}' if self.timestamp is not None else ''
        cls = self.__class__.__name__
        return cls + '(' + lat + lon + time + ')'

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def coordinates(self):
        return self.latitude, self.longitude

    def copy(self, deep=False):
        obj = type(self).__new__(type(self))
        obj._latitude = self._latitude
        obj._longitude = self._longitude
        obj._timestamp = self._timestamp
        return obj

    def distance_to(self, other):
        # TODO: Make sure that this broadcasts properly!
        # I expect that the geodesic doesn't broadcast, so you might need to loop. Look at np.nditer or np.verctorize
        try:
            iter(other)
        except TypeError as err:
            if str(err).endswith('object is not iterable'):
                other = [other]
            else:
                raise

        distances = [
            geod.Inverse(
                self.latitude,
                self.longitude,
                pos.latitude,
                pos.longitude,
                outmask=geod.DISTANCE,
            )['s12']
            for pos in other
        ]
        if len(distances) == 1:
            return distances[0]
        return np.asarray(distances)

    def angle_between(self, first_position, second_position):
        first_azimuth = geod.Inverse(
            self.latitude, self.longitude,
            first_position.latitude, first_position.longitude,
            outmask=geod.AZIMUTH
        )['azi1']
        second_azimuth = geod.Inverse(
            self.latitude, self.longitude,
            second_position.latitude, second_position.longitude,
            outmask=geod.AZIMUTH
        )['azi1']
        angular_difference = second_azimuth - first_azimuth
        return (angular_difference + 180) % 360 - 180


class Track(abc.ABC):
    """A track of positions measured over time.

    Parameters
    ----------
    latitude : array_like
        The measured latitudes
    longitude : array_like
        The measured longitudes
    time : `TimedSequence`
        Specification of the times where the position was measured.
    """

    def copy(self, deep=False):
        obj = type(self).__new__(type(self))
        return obj

    @abc.abstractmethod
    def __len__(self):
        ...

    @property
    @abc.abstractmethod
    def timestamps(self):
        """List of timestamps as `datetime` objects for each position."""
        ...

    @property
    @abc.abstractmethod
    def track_time(self):
        """Array of time in the track relative to the start of the track, in seconds."""
        ...

    @property
    @abc.abstractmethod
    def time_window(self):
        """Time window that the track covers."""
        ...

    @property
    @abc.abstractmethod
    def latitude(self):
        """Latitudes of the track, in degrees."""
        ...

    @property
    @abc.abstractmethod
    def longitude(self):
        """Longitudes of the track, in degrees."""
        ...

    @property
    def coordinates(self):
        return np.stack([self.latitude, self.longitude], axis=0)

    @property
    @abc.abstractmethod
    def speed(self):
        """Speed in the track, in meters per second"""
        ...

    @property
    @abc.abstractmethod
    def heading(self):
        """Heading in the track, in degrees"""
        ...

    @property
    def mean(self):
        """Mean position of the track."""
        lat = np.mean(self.latitude)
        lon = np.mean(self.longitude)
        return Position(latitude=lat, longitude=lon)

    @property
    def boundaries(self):
        """Boundaries of the track.

        (lat_min, lat_max, lon_min, lon_max)
        """
        min_lat = np.min(self.latitude)
        min_lon = np.min(self.longitude)
        max_lat = np.max(self.latitude)
        max_lon = np.max(self.longitude)
        return min_lat, max_lat, min_lon, max_lon

    def distance_to(self, other):
        if isinstance(other, Track):
            raise TypeError('Cannot calculate distances between two tracks')
        if isinstance(other, Position):
            return other.distance_to(self)
        try:
            lat, lon = other
        except TypeError as err:
            if str(err).startswith('cannot unpack non-iterable'):
                raise TypeError(f'Cannot calculate distance between track and {other}')
            else:
                raise
        return Position(latitude=lat, longitude=lon).distance_to(self)

    def closest_point(self, other):
        if not isinstance(other, Position):
            try:
                lat, lon = other
            except TypeError as err:
                if str(err).startswith('cannot unpack non-iterable'):
                    raise TypeError(f'Cannot calculate distance between track and {other}')
                else:
                    raise
            other = Position(latitude=lat, longitude=lon)
        distances = other.distance_to(self)
        idx = np.argmin(distances)
        distance = distances[idx]
        position = self[idx]
        position.distance = distance
        return position

    def time_range(self, start=None, stop=None, center=None, duration=None):
        """Restrict the time range.

        This gets a window to the same time signal over a specified time period.
        The time period can be specified with any combination of two of the input
        parameters. The times can be specified either as `datetime` objects,
        or as strings on following format: `YYYYMMDDhhmmssffffff`.
        The microsecond part can be optionally omitted, and any non-digit characters
        are removed. Some examples include
        - 20220525165717
        - 2022-05-25_16-57-17
        - 2022/05/25 16:57:17.123456

        Parameters
        ----------
        start : datetime or string
            The start of the time window
        stop : datetime or string
            The end of the time window
        center : datetime or string
            The center of the time window
        duration : numeric
            The total duration of the time window, in seconds.
        """
        time_window = TimeWindow(
            start=start,
            stop=stop,
            center=center,
            duration=duration,
        )
        return self[time_window]


    @abc.abstractmethod
    def __getitem__(self, key):
        """Restrict the time range.

        This gets the same signal but restricted to a time range specified
        with a TimeWindow object.

        Parameters
        ----------
        window : `TimeWindow`
            The time window to restrict to.
        """
        ...

    def aspect_windows(self, reference_point, resolution, span, window_min_length=None, window_min_angle=None):
        """Get time windows corresponding to specific aspect angles

        Parameters
        ----------
        reference_point : Position
            The position from where the angles are calculated.
        resolution : numeric
            The spacing of the windows, in degrees.
        span : numeric or (numeric, numeric)
            The angular span of the centers of the windows, in degrees.
            A single value will be used as (-span, span).
        window_min_length : numeric, optional
            The minimum length of each window, in meters.
        window_min_angle : numeric, optional
            The minimum length of each window, seen as an angle from the reference point.
            If neither of `window_min_length` or `window_min_angle` is given, the `window_min_angle`
            defaults to `resolution`.
        """
        # TODO: Include some check that the path is reasonable?
        cpa = self.closest_point(reference_point)  # If the path if to long this will crunch a shit-ton of data...
        try:
            min_angle, max_angle = min(span), max(span)
        except TypeError:
            min_angle, max_angle = -span, span
        # pre_cpa, post_cpa = , self[cpa.timestamp:]

        if (window_min_angle, window_min_length) == (None, None):
            window_min_angle = resolution

        pre_cpa_angles = np.arange(1, np.math.ceil(-min_angle // resolution) + 1) * resolution
        post_cpa_angles = np.arange(1, np.math.ceil(max_angle // resolution) + 1) * resolution

        pre_cpa_window_centers = [cpa]
        post_cpa_window_centers = [cpa]
        for angle in pre_cpa_angles:
            for point in reversed(self[:pre_cpa_window_centers[-1].timestamp]):
                if abs(reference_point.angle_between(cpa, point)) >= angle:
                    pre_cpa_window_centers.append(point)
                    break
        for angle in post_cpa_angles:
            for point in self[post_cpa_window_centers[-1].timestamp:]:
                if abs(reference_point.angle_between(cpa, point)) >= angle:
                    post_cpa_window_centers.append(point)
                    break
        # Merge the list of window centers
        # The pre cpa list is reversed to have them in the correct order
        # Both lists have the cpa in them, so it's removed from the post cpa list
        window_centers = pre_cpa_window_centers[::-1] + post_cpa_window_centers[1:]

        windows = []
        for center in window_centers:
            meets_angle_criteria = window_min_angle is None
            meets_length_criteria = window_min_length is None
            for point in reversed(self[:center.timestamp]):
                if not meets_angle_criteria:
                    # Calculate angle and check if it's fine
                    meets_angle_criteria = abs(reference_point.angle_between(center, point)) >= window_min_angle / 2
                if not meets_length_criteria:
                    # Calculate length and check if it's fine
                    meets_length_criteria = center.distance_to(point) >= window_min_length / 2
                if meets_length_criteria and meets_angle_criteria:
                    window_start = point
                    break
            meets_angle_criteria = window_min_angle is None
            meets_length_criteria = window_min_length is None
            for point in self[center.timestamp:]:
                if not meets_angle_criteria:
                    # Calculate angle and check if it's fine
                    meets_angle_criteria = abs(reference_point.angle_between(center, point)) >= window_min_angle / 2
                if not meets_length_criteria:
                    # Calculate length and check if it's fine
                    meets_length_criteria = center.distance_to(point) >= window_min_length / 2
                if meets_length_criteria and meets_angle_criteria:
                    window_stop = point
                    break
            windows.append(TimeWindow(start=window_start.timestamp, stop=window_stop.timestamp))
        return windows


    def resample(self, sampletime, order='linear'):
        """Resample a position track.

        Parameters
        ----------
        sampletime : numerical
            The desired time between samples of the track.
        order : integer or string, default "linear"
            Sets the polynomial order of the interpolation.
            See `kind` argument of `scipy.interpolate.interp1d`
        """
        return ResampledTrack(
            sampletime=sampletime,
            time=self.track_time,
            start_time=self.time_window.start,
            order=order,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        # TODO: Move this implementation to a ResampledTrack, which takes position data and extra data as the input.
        # TODO: add this to the Blueflow class as well to make sure that any extra props get included. Check if you can make this nice in the api?

        # Handling uniqueness of samples.
        unique_times, time_indices, duplicate_counts = np.unique(self.time, return_inverse=True, return_counts=True)
        latitude = self.latitude
        longitude = self.longitude
        if unique_times.size < time_indices.size:
            # We have duplicate timestamps
            # bincount will count how often each value in `time_indices` occurs
            # i.e. how many times the same time exists in the time vector.
            # These values are weighted by the input values in latitude and longitude,
            # given as the second argument.
            # Finally the mean is calculated by dividing by the number of duplicates.
            latitude = np.bincount(time_indices, latitude) / duplicate_counts
            longitude = np.bincount(time_indices, longitude) / duplicate_counts

        # Handling subsampling of the domain
        # if start is not None:
        #     # Get the index which is just to the right of the start value, then go left one.
        #     # This is to include at one additional sample if the requested time is not actually in the times.
        #     start_idx = max(np.searchsorted(unique_times, start, 'right') - 1, 0)
        # else:
        #     start_idx = 0
        #     start = unique_times[0]

        # if stop is not None:
        #     # Get the index which is just to the left of the start value, then go right one.
        #     # This is to include at one additional sample if the requested time is not actually in the times.
        #     stop_idx = min(np.searchsorted(unique_times, stop, 'left') + 1, len(unique_times))
        # else:
        #     stop_idx = len(unique_times)
        #     stop = unique_times[-1]
        # unique_times = unique_times[start_idx:stop_idx]
        # latitude = latitude[start_idx:stop_idx]
        # longitude = longitude[start_idx:stop_idx]

        # Performing the interpolation
        n_samples = np.math.floor((unique_times[-1] - unique_times[0]) / sampletime) + 1
        time = np.arange(n_samples) * sampletime + unique_times[0]
        def interpolate(data):
            interpolator = scipy.interpolate.interp1d(
                unique_times, data,
                kind=order,
                bounds_error=False, fill_value=(data[0], data[-1])
            )
            return interpolator(time)
        latitude = interpolate(latitude)
        longitude = interpolate(longitude)

        resampled = {}
        for key in extra_data:
            resampled[key] = interpolate(getattr(self, key))
        # Store the new data
        obj = ResampledTrack(time=time, latitude=latitude, longitude=longitude, **resampled)
        return obj
        resampled._latitude = latitude
        resampled._longitude = longitude
        resampled.time = timestamps.time
        resampled.sampletime = sampletime
        return resampled


class TimestampedTrack(Track):
    def __init__(self, timestamps):
        self._timestamps = np.asarray(timestamps)

    @property
    def timestamps(self):
        return self._timestamps

    @property
    def time_window(self):
        return TimeWindow(start=self.timestamps[0], stop=self.timestamps[-1])

    @property
    def track_time(self):
        return np.asarray([
            (stamp - self.timestamps[0]).total_seconds()
            for stamp in self.timestamps
        ])

    def __len__(self):
        return self._timestamps.size

    def copy(self, deep=False):
        obj = super().copy()
        obj._timestamps = self._timestamps
        return obj

    @abc.abstractmethod
    def __getitem__(self, key):
        if isinstance(key, TimeWindow):
            key = slice(key.start, key.stop)

        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if isinstance(start, datetime.datetime):
                start = bisect.bisect_left(self._timestamps, start)
            if isinstance(stop, datetime.datetime):
                stop = bisect.bisect_right(self._timestamps, stop)
            return slice(start, stop)

        if isinstance(key, datetime.datetime):
            idx = bisect.bisect_right(self._timestamps, key)
            if idx == 0:
                return idx
            if idx == len(self):
                return idx - 1
            right_distance = (self._timestamps[idx] - key).total_seconds()
            left_distance = (key - self._timestamps[idx - 1]).total_seconds()
            if left_distance < right_distance:
                idx -= 1
            return idx

        return key


class ReferencedTrack(Track):
    def __init__(self, times, reference):
        self._times = times
        self._reference = reference

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj._times = self._times
        obj._reference = self._reference

    def __len__(self):
        return len(self._times)

    @property
    def track_time(self):
        return self._times - self._times[0]

    @property
    def timestamps(self):
        return [
            self._reference + datetime.timedelta(seconds=t)
            for t in self._times
        ]

    @property
    def time_window(self):
        return TimeWindow(
            start=self._reference + datetime.timedelta(seconds=self._times[0]),
            stop=self._reference + datetime.timedelta(seconds=self._times[-1]),
        )

    @abc.abstractmethod
    def __getitem__(self, key):
        if isinstance(key, TimeWindow):
            key = slice(key.start, key.stop)

        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if isinstance(start, datetime.datetime):
                start = (start - self._reference).total_seconds()
                start = bisect.bisect_left(self._times, start)
            if isinstance(stop, datetime.datetime):
                stop = (stop - self._reference).total_seconds()
                stop = bisect.bisect_right(self._times, stop)
            return slice(start, stop)

        if isinstance(key, datetime.datetime):
            key = (key - self._reference).total_seconds()
            idx = bisect.bisect_right(self._times, key)
            if idx == 0:
                return idx
            if idx == len(self):
                return idx - 1
            right_distance = self._times[idx] - key
            left_distance = key - self._times[idx - 1]
            if left_distance < right_distance:
                idx -= 1
            return idx

        return key


class SampledTrack(Track):
    def __init__(self, sampletime, start, num_samples):
        self._sampletime = sampletime
        self._start = start
        self._num_samples = num_samples

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj._sampletime = self._sampletime
        obj._start = self._start
        obj._num_samples = self._num_samples
        return obj

    def __len__(self):
        return self._num_samples

    @property
    def timestamps(self):
        return [
            self._start + datetime.timedelta(seconds=idx * self._sampletime)
            for idx in range(self._num_samples)
        ]

    @property
    def track_time(self):
        return np.ararnge(self._num_samples) * self._sampletime

    @property
    @abc.abstractmethod
    def time_window(self):
        return TimeWindow(
            start=self._start,
            duration=self._num_samples * self._sampletime
        )

    @abc.abstractmethod
    def __getitem__(self, key):
        if isinstance(key, TimeWindow):
            key = slice(key.start, key.stop)

        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if isinstance(start, datetime.datetime):
                start = (start - self._start).total_seconds()
                start = np.math.ceil(start / self._sampletime)
            if isinstance(stop, datetime.datetime):
                stop = (stop - self._start).total_seconds()
                stop = np.math.floor(stop / self._sampletime)
            return slice(start, stop)

        if isinstance(key, datetime.datetime):
            key = (key - self._start).total_seconds()
            idx = round(key * self._sampletime)
            return idx

        return key


class GPXTrack(TimestampedTrack):
    def __init__(self, path):
        import gpxpy
        file = open(path, 'r')
        contents = gpxpy.parse(file)
        latitudes = []
        longitudes = []
        times = []
        for point in contents.get_points_data():
            latitudes.append(point.point.latitude)
            longitudes.append(point.point.longitude)
            times.append(point.point.time)
        super().__init__(timestamps=times)
        self._latitude = np.asarray(latitudes)
        self._longitude = np.asarray(longitudes)

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def heading(self):
        raise NotImplementedError()

    @property
    def speed(self):
        raise NotImplementedError()

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj._latitude = self._latitude
        obj._longitude = self._longitude
        return obj

    def __getitem__(self, key):
        key = super().__getitem__(key)
        latitude = self.latitude[key]
        longitude = self.longitude[key]
        timestamps = self.timestamps[key]

        if not isinstance(key, slice):
            return Position(
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamps,
            )

        obj = self.copy(deep=False)
        obj._latitude = latitude
        obj._longitude = longitude
        obj._timestamps = timestamps
        return obj


class Blueflow(TimestampedTrack):
    def __init__(self, path):
        import pandas
        self.data = pandas.read_excel(path)

        super().__init__(timestamps=self.data['Timestamp [UTC]'].dt.tz_localize(dateutil.tz.UTC).dt.to_pydatetime())
        # times = df['Timestamp [UTC]'].dt.to_pydatetime()
        # times = timestamps.TimedstampedSequence(times)
        # latitudes = df['Latitude [deg]'].to_numpy()
        # longitudes = df['Longitude [deg]'].to_numpy()
        # track = Track(latitude=latitudes, longitude=longitudes, time=times)
        # track.blueflow = df

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj.data = self.data
        return obj

    @property
    def latitude(self):
        latitude = self.data['Latitude [deg]']
        try:
            return latitude.to_numpy()
        except AttributeError:
            return latitude

    @property
    def longitude(self):
        longitude = self.data['Longitude [deg]']
        try:
            return longitude.to_numpy()
        except AttributeError:
            return longitude

    @property
    def heading(self):
        heading = self.data['Heading [deg]']
        try:
            return heading.to_numpy()
        except AttributeError:
            return heading

    @property
    def speed(self):
        speed = self.data['Speed over ground [kts]'] / one_knot
        try:
            return speed.to_numpy()
        except AttributeError:
            return speed

    def __getitem__(self, key):
        key = super().__getitem__(key)
        obj = self.copy(deep=False)
        obj.data = self.data.iloc[key]
        obj._timestamps = self.timestamps[key]
        if not isinstance(key, slice):
            return Position(
                latitude=obj.latitude,
                longitude=obj.longitude,
                timestamp=obj.timestamps,
            )
        return obj


class ResampledTrack(Track):
    def __init__(self, sampletime, time, latitude, longitude, start_time=None, order='linear', **kwargs):
        self.sampletime = sampletime
        self.order = order
        self.start_time = start_time
        self._unique_times, self._time_indices, self._duplicate_counts = np.unique(time, return_inverse=True, return_counts=True)
        n_samples = np.math.floor((self._unique_times[-1] - self._unique_times[0]) / self.sampletime) + 1
        self.time = np.arange(n_samples) * self.sampletime + self._unique_times[0]

        self.latitude = self._interpolate(latitude)
        self.longitude = self._interpolate(longitude)
        self._extra_data = list(kwargs.keys())
        for key, data in kwargs.items():
            setattr(self, key, self._interpolate(data))

    def _interpolate(self, data):
        if self._unique_times.size < self._time_indices.size:
            data = np.bincount(self._time_indices, data) / self._duplicate_counts
        interpolator = scipy.interpolate.interp1d(self._unique_times, data, kind=self.order)
        return interpolator(self.time)

    def smooth(self, time_constant, smoothing_method='median'):
        return SmoothTrack(
            time_constant=time_constant,
            sampletime=self.sampletime,
            smoothing_method=smoothing_method,
            start_time=self.start_time,
            latitude=self.latitude,
            longitude=self.longitude,
            **{key: getattr(self, key) for key in self._extra_data}
        )


class SmoothTrack(Track):
    def __init__(self, time_constant, sampletime, latitude, longitude, start_time=None, smoothing_method='median', **kwargs):
        self.time_constant = time_constant
        self.sampletime = sampletime
        self.start_time = start_time
        self.smoothing_method = smoothing_method

        self.latitude = self._smooth(latitude)
        self.longitude = self._smooth(longitude)
        for key, data in kwargs.items():
            setattr(self, key, self._smooth(data))

    def _smooth(self, data):
        if self.smoothing_method.lower() == 'median':
            smoother =  self._median_filter
        elif callable(self.smoothing_method):
            smoother = self.smoothing_method
        else:
            raise ValueError(f'Unknown smoothing method {self.smoothing_method}')
        return smoother(data=data, time_constant=self.time_constant, sampletime=self.sampletime)

    @staticmethod
    def _median_filter(data, time_constant, sampletime):
        import scipy.ndimage
        kernel = round(time_constant / sampletime)
        kernel = (1,) * (np.ndim(data) - 1) + (kernel, )
        return scipy.ndimage.percentile_filter(data, 50, kernel)


# @_callable_property(Track, 'resample')
# class ResampledTrack(Track):
#     def __init__(self, track):
#         self._track = track

#     def __call__(self, sampletime, start=None, stop=None, order='linear'):
#         """Resample a position track.

#         Parameters
#         ----------
#         sampletime : numerical
#             The desired time between samples of the track.
#         start : numerical, optional
#             The time in the track where the resampling should start.
#             Default to use the entire track.
#         stop : numerical, optional
#             The time in the track where the resampling should stop.
#             Default to use the entire track.
#         order : integer or string, default "linear"
#             Sets the polynomial order of the interpolation.
#             See `kind` argument of scipy.interpolate.interp1d`
#         """
#         # Handling uniqueness of samples.
#         unique_times, time_indices, duplicate_counts = np.unique(self._track.time, return_inverse=True, return_counts=True)
#         latitude = self._track.latitude
#         longitude = self._track.longitude
#         if unique_times.size < time_indices.size:
#             # We have duplicate timestamps
#             # bincount will count how often each value in `time_indices` occurs
#             # i.e. how many times the same time exists in the time vector.
#             # These values are weighted by the input values in latitude and longitude,
#             # given as the second argument.
#             # Finally the mean is calculated by dividing by the number of duplicates.
#             latitude = np.bincount(time_indices, latitude) / duplicate_counts
#             longitude = np.bincount(time_indices, longitude) / duplicate_counts

#         # Handling subsampling of the domain
#         if start is not None:
#             # Get the index which is just to the right of the start value, then go left one.
#             # This is to include at one additional sample if the requested time is not actually in the times.
#             start_idx = max(np.searchsorted(unique_times, start, 'right') - 1, 0)
#         else:
#             start_idx = 0
#             start = unique_times[0]

#         if stop is not None:
#             # Get the index which is just to the left of the start value, then go right one.
#             # This is to include at one additional sample if the requested time is not actually in the times.
#             stop_idx = min(np.searchsorted(unique_times, stop, 'left') + 1, len(unique_times))
#         else:
#             stop_idx = len(unique_times)
#             stop = unique_times[-1]
#         unique_times = unique_times[start_idx:stop_idx]
#         latitude = latitude[start_idx:stop_idx]
#         longitude = longitude[start_idx:stop_idx]

#         # Performing the interpolation
#         n_samples = np.math.floor((stop - start) / sampletime) + 1
#         time = np.arange(n_samples) * sampletime + start
#         latitude = scipy.interpolate.interp1d(unique_times, latitude, kind=order, bounds_error=False, fill_value=(latitude[0], latitude[-1]))
#         longitude = scipy.interpolate.interp1d(unique_times, longitude, kind=order, bounds_error=False, fill_value=(longitude[0], longitude[-1]))
#         latitude = latitude(time)
#         longitude = longitude(time)

#         # Store the new data
#         self._latitude = latitude
#         self._longitude = longitude
#         self._time = time
#         self.sampletime = sampletime
#         return self


# @_callable_property(Track, 'smooth')
# class SmoothTrack(Track):
#     # This should probably only be creatable from a resampled track, to ensure that we have
#     # consistent timings. If you want to smooth data which is already sampled nicely,
#     # just "resample" it using the same sampling time?
#     def __init__(self, track):
#         self._track = track

#     @property
#     def sampletime(self):
#         try:
#             return self._track.sampletime
#         except AttributeError:
#             raise TypeError('Cannot smooth a track which has no fixed sampling time!')

#     def __call__(self, time_constant, smoothing_method='median'):
#         """Smooths a position track.

#         Parameters
#         ----------
#         time_constant : numerical
#             Controlls the strength of the smoothing. Is in units of seconds.
#         smoothing_method : string, default "median"
#             Sets the smoothing method
#         """
#         self.time_constant = time_constant
#         self.smoothing_method = smoothing_method

#         latitude = self._track.latitude
#         longitude = self._track.longitude

#         if smoothing_method.lower() == 'median':
#             kernel = round(self.time_constant / self.sampletime)
#             kernel += (kernel + 1) % 2  # Median filter kernel has to be odd!

#             smooth_latitude = scipy.signal.medfilt(latitude, kernel)
#             smooth_longitude = scipy.signal.medfilt(longitude, kernel)

#             # Recalculate the edges with a shrinking kernel instead of zero-padding
#             kernel_offset = kernel // 2 + 1
#             for idx in range(kernel // 2):
#                 smooth_latitude[idx] = np.median(latitude[:idx + kernel_offset])
#                 smooth_longitude[idx] = np.median(longitude[:idx + kernel_offset])
#                 smooth_latitude[-1 - idx] = np.median(latitude[-idx - kernel_offset:])
#                 smooth_longitude[-1 - idx] = np.median(longitude[idx - kernel_offset:])
#         else:
#             raise ValueError(f'Unknown smoothing method {smoothing_method}')

#         self._latitude = smooth_latitude
#         self._longitude = smooth_longitude
#         self._time = self._track.time
#         return self
