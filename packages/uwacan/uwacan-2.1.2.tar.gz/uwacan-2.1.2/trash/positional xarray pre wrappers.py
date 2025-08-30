"""Handles positional tracks.

This manages logs over positions of measurement objects via e.g. GPS.
Some of the operations include smoothing data, calculating distances,
and reading log files.
"""

import numpy as np
from geographiclib.geodesic import Geodesic
import pendulum
import xarray as xr
import os
import re
geod = Geodesic.WGS84

one_knot = 1.94384
"""One m/s in knots, i.e., this has the units of knots/(m/s).
Multiply with this value to go from m/s to knots,
divide by this value to go from knots to m/s."""


def nm_to_m(nm):
    """Convert nautical miles to meters"""
    return nm * 1852


def m_to_nm(m):
    """Convert meters to nautical miles"""
    return m / 1852


def mps_to_knots(mps):
    """Convert meters per secont to knots"""
    return mps * (3600 / 1852)


def knots_to_mps(knots):
    """Convert knots to meters per second"""
    return knots * (1852 / 3600)


def knots_to_kmph(knots):
    """Convert knots to kilometers per hour"""
    return knots * 1.852


def kmph_to_knots(kmph):
    """Convert kilometers per hour to knots"""
    return kmph / 1.852


def local_mercator_to_wgs84(easting, northing, reference_latitude, reference_longitude):
    r"""Convert local mercator coordinates into wgs84 coordinates.

    Conventions here are :math:`\lambda` as the longitude and :math:`\varphi` as the latitude,
    :math:`x` is easting and :math:`y` is northing.

    .. math::

        \lambda &= \lambda_0 + \frac{x}{R} \\
        \varphi &= 2\arctan\left[\exp \left(\frac{y + y_0}{R}\right)\right] - \frac{\pi}{2}

    The northing offset :math:`y_0` is computed by converting the reference point into
    a mercator projection with the `wgs84_to_local_mercator` function, using (0, 0) as
    the reference coordinates.
    """
    WGS84_semiaxis_radius = 6378137.0
    mercator_scale_factor = 0.9996
    radius = WGS84_semiaxis_radius * mercator_scale_factor

    ref_east, ref_north = wgs84_to_local_mercator(reference_latitude, reference_longitude, 0, 0)
    longitude = reference_longitude + np.degrees(easting / radius)
    latitude = 2 * np.arctan(np.exp((northing + ref_north) / radius)) - np.pi / 2
    latitude = np.degrees(latitude)
    return latitude, longitude


def wgs84_to_local_mercator(latitude, longitude, reference_latitude, reference_longitude):
    r"""Convert wgs84 coordinates into a local mercator projection.

    Conventions here are :math:`\lambda` as the longitude and :math:`\varphi` as the latitude,
    :math:`x` is easting and :math:`y` is northing.

    .. math::
        x &= R(\lambda -\lambda _{0})\\
        y &= R\ln \left[\tan \left(\frac{\pi}{4} + \frac{\varphi - \varphi_0}{2}\right)\right]
    """
    WGS84_semiaxis_radius = 6378137.0
    mercator_scale_factor = 0.9996
    radius = WGS84_semiaxis_radius * mercator_scale_factor
    local_longitude = np.radians(longitude - reference_longitude)
    local_latitude = np.radians(latitude - reference_latitude)
    easting = radius * local_longitude
    northing = radius * np.log(np.tan(np.pi / 4 + local_latitude / 2))
    # northing = radius * np.log(np.tan(np.pi / 4 + np.radians(latitude) / 2))
    # reference_northing = radius * np.log(np.tan(np.pi / 4 + np.radians(reference_latitude) / 2))
    return easting, northing


def time_to_np(input):
    if isinstance(input, np.datetime64):
        return input
    if not isinstance(input, pendulum.DateTime):
        input = time_to_datetime(input)
    return np.datetime64(input.in_tz('UTC').naive())


def time_to_datetime(input, fmt=None, tz="UTC"):
    """Converts datetimes to the same internal format.

    This function takes a few types of input and tries to convert
    the input to a pendulum.DateTime.
    - Any datetime-like input will be converted directly.
    - np.datetime64 and Unix timestamps are treated similarly.
    - Strings are parsed with `fmt` if given, otherwise a few different common formats are tried.

    Parameters
    ----------
    input : datetime-like, string, or numeric.
        The input data specifying the time.
    fmt : string, optional
        Optional format detailing how to parse input strings. See `pendulum.from_format`.
    tz : string, default "UTC"
        The timezone of the input time for parsing, and the output time zone.
        Unix timestamps have no timezone, and np.datetime64 only supports UTC.

    Returns
    -------
    time : pendulum.DateTime
        The converted time.
    """
    try:
        return pendulum.instance(input, tz=tz)
    except AttributeError as err:
        if "object has no attribute 'tzinfo'" in str(err):
            pass
        else:
            raise

    if isinstance(input, xr.DataArray):
        if input.size == 1:
            input = input.values
        else:
            raise ValueError('Cannot convert multiple values at once.')

    if fmt is not None:
        return pendulum.from_format(input, fmt=fmt, tz=tz)

    if isinstance(input, np.datetime64):
        if tz != "UTC":
            raise ValueError("Numpy datetime64 values should always be stored in UTC")
        input = input.astype('timedelta64') / np.timedelta64(1, 's')  # Gets the time as a timestamp, will parse nicely below.

    try:
        return pendulum.from_timestamp(input, tz=tz)
    except TypeError as err:
        if 'object cannot be interpreted as an integer' in str(err):
            pass
        else:
            raise
    return pendulum.parse(input, tz=tz)


class TimeWindow:
    def __init__(self, start=None, stop=None, center=None, duration=None, extend=None):
        if start is not None:
            start = time_to_datetime(start)
        if stop is not None:
            stop = time_to_datetime(stop)
        if center is not None:
            center = time_to_datetime(center)

        if None not in (start, stop):
            _start = start
            _stop = stop
            start = stop = None
        elif None not in (center, duration):
            _start = center - pendulum.duration(seconds=duration / 2)
            _stop = center + pendulum.duration(seconds=duration / 2)
            center = duration = None
        elif None not in (start, duration):
            _start = start
            _stop = start + pendulum.duration(seconds=duration)
            start = duration = None
        elif None not in (stop, duration):
            _stop = stop
            _start = stop - pendulum.duration(seconds=duration)
            stop = duration = None
        elif None not in (start, center):
            _start = start
            _stop = start + (center - start) / 2
            start = center = None
        elif None not in (stop, center):
            _stop = stop
            _start = stop - (stop - center) / 2
            stop = center = None
        else:
            raise TypeError('Needs two of the input arguments to determine time window.')

        if (start, stop, center, duration) != (None, None, None, None):
            raise TypeError('Cannot input more than two input arguments to a time window!')

        if extend is not None:
            _start = _start.subtract(seconds=extend)
            _stop = _stop.add(seconds=extend)

        self._window = pendulum.interval(_start, _stop)

    def subwindow(self, time=None, /, *, start=None, stop=None, center=None, duration=None, extend=None):
        if time is None:
            # Period specified with keyword arguments, convert to period.
            if (start, stop, center, duration).count(None) == 3:
                # Only one argument which has to be start or stop, fill the other from self.
                if start is not None:
                    window = type(self)(start=start, stop=self.stop, extend=extend)
                elif stop is not None:
                    window = type(self)(start=self.start, stop=stop, extend=extend)
                else:
                    raise TypeError('Cannot create subwindow from arguments')
            elif duration is not None and True in (start, stop, center):
                if start is True:
                    window = type(self)(start=self.start, duration=duration, extend=extend)
                elif stop is True:
                    window = type(self)(stop=self.stop, duration=duration, extend=extend)
                elif center is True:
                    window = type(self)(center=self.center, duration=duration, extend=extend)
                else:
                    raise TypeError('Cannot create subwindow from arguments')
            else:
                # The same types explicit arguments as the normal constructor
                window = type(self)(start=start, stop=stop, center=center, duration=duration, extend=extend)
        elif isinstance(time, type(self)):
            window = time
        elif isinstance(time, pendulum.Interval):
            window = type(self)(start=time.start, stop=time.end, extend=extend)
        elif isinstance(time, xr.Dataset):
            window = type(self)(start=time.time.min(), stop=time.time.max(), extend=extend)
        else:
            # It's not a period, so it shold be a single datetime. Parse or convert, check valitidy.
            time = time_to_datetime(time)
            if time not in self:
                raise ValueError("Received time outside of contained window")
            return time

        if window not in self:
            raise ValueError("Requested subwindow is outside contained time window")
        return window

    def __repr__(self):
        return f'TimeWindow(start={self.start}, stop={self.stop})'

    @property
    def start(self):
        return self._window.start

    @property
    def stop(self):
        return self._window.end

    @property
    def center(self):
        return self.start.add(seconds=self._window.total_seconds() / 2)

    @property
    def duration(self):
        return self._window.total_seconds()

    def __contains__(self, other):
        if isinstance(other, type(self)):
            other = other._window
        if isinstance(other, pendulum.Interval):
            return other.start in self._window and other.end in self._window
        return other in self._window


class Position:
    @staticmethod
    def parse_coordinates(*args, **kwargs):
        try:
            return kwargs['latitude'], kwargs['longitude']
        except KeyError:
            pass

        if len(args) == 1:
            arg = args[0]
            try:
                return arg.latitude, arg.longitude
            except AttributeError:
                pass
            try:
                return arg['latitude'], arg['longitude']
            except (KeyError, TypeError):
                pass
            if isinstance(arg, str):
                matches = re.match(
                    r"""((?P<latdeg>[+\-\d.]+)°?)?((?P<latmin>[\d.]+)')?((?P<latsec>[\d.]+)")?(?P<lathemi>[NS])?"""
                    r"""[,]?"""
                    r"""((?P<londeg>[+\-\d.]+)°?)?((?P<lonmin>[\d.]+)')?((?P<lonsec>[\d.]+)")?(?P<lonhemi>[EW])?""",
                    re.sub(r"\s", "", arg)
                ).groupdict()
                if not matches["latdeg"] or not matches["londeg"]:
                    raise ValueError(f"Cannot parse coordinate string '{arg}'")

                digits_to_parse = len(re.sub(r"\D", "", arg))
                digits_parsed = 0
                latitude = float(matches["latdeg"])
                lat_sign = 1 if latitude >= 0 else -1
                digits_parsed += len(re.sub(r"\D", "", matches["latdeg"]))
                longitude = float(matches["londeg"])
                lon_sign = 1 if longitude >= 0 else -1
                digits_parsed += len(re.sub(r"\D", "", matches["londeg"]))

                if matches["latmin"]:
                    latitude += lat_sign * float(matches["latmin"]) / 60
                    digits_parsed += len(re.sub(r"\D", "", matches["latmin"]))
                if matches["lonmin"]:
                    longitude += lon_sign * float(matches["lonmin"]) / 60
                    digits_parsed += len(re.sub(r"\D", "", matches["lonmin"]))

                if matches["latsec"]:
                    latitude += lat_sign * float(matches["latsec"]) / 3600
                    digits_parsed += len(re.sub(r"\D", "", matches["latsec"]))
                if matches["lonsec"]:
                    longitude += lon_sign * float(matches["lonsec"]) / 3600
                    digits_parsed += len(re.sub(r"\D", "", matches["lonsec"]))

                if not digits_parsed == digits_to_parse:
                    raise ValueError(f"Could not parse coordinate string '{arg}', used only {digits_parsed} of {digits_to_parse} digits")

                if matches["lathemi"] == "S":
                    latitude = -abs(latitude)
                if matches["lonhemi"] == "W":
                    longitude = -abs(longitude)

                return latitude, longitude

            else:
                # We should never have just a single argument, try unpacking.
                *args, = arg

        if len(args) == 2:
            latitude, longitude = args
            return latitude, longitude
        elif len(args) == 4:
            (
                latitude_degrees, latitude_minutes,
                longitude_degrees, longitude_minutes
             ) = args
            latitude = latitude_degrees + latitude_minutes / 60
            longitude = longitude_degrees + longitude_minutes / 60
            return latitude, longitude
        elif len(args) == 6:
            (
                latitude_degrees, latitude_minutes, latitude_seconds,
                longitude_degrees, longitude_minutes, longitude_seconds
             ) = args
            latitude = latitude_degrees + latitude_minutes / 60 + latitude_seconds / 3600
            longitude = longitude_degrees + longitude_minutes / 60 + longitude_seconds / 3600
            return latitude, longitude
        else:
            raise TypeError(f"Undefined number of arguments for Position. {len(args)} was given, expects 2, 4, or 6.")

    def __init__(self, *args, **kwargs):
        # if len(args) == 1 and isinstance(args[0], type(self)):
            # return args[0]
        latitude, longitude = self.parse_coordinates(*args, **kwargs)
        self.coordinates = xr.Dataset(data_vars=dict(latitude=latitude, longitude=longitude))

    @property
    def latitude(self):
        return self.coordinates['latitude']

    @property
    def longitude(self):
        return self.coordinates['longitude']

    def __repr__(self):
        return f"{type(self).__name__}({self.latitude.item():.4f}, {self.longitude.item():.4f})"

    @classmethod
    def from_local_mercator(cls, easting, northing, reference_coordinate, **kwargs):
        r"""Convert local mercator coordinates into wgs84 coordinates.

        Conventions here are :math:`\lambda` as the longitude and :math:`\varphi` as the latitude,
        :math:`x` is easting and :math:`y` is northing.

        .. math::

            \lambda &= \lambda_0 + \frac{x}{R} \\
            \varphi &= 2\arctan\left[\exp \left(\frac{y + y_0}{R}\right)\right] - \frac{\pi}{2}

        The northing offset :math:`y_0` is computed by converting the reference point into
        a mercator projection with the `wgs84_to_local_mercator` function, using (0, 0) as
        the reference coordinates.
        """
        reference_coordinate = Position(reference_coordinate)
        lat, lon = local_mercator_to_wgs84(
            easting, northing,
            reference_coordinate.latitude, reference_coordinate.longitude
        )
        return cls(latitude=lat, longitude=lon, **kwargs)

    def to_local_mercator(self, reference_coordinate):
        r"""Convert wgs84 coordinates into a local mercator projection.

        Conventions here are :math:`\lambda` as the longitude and :math:`\varphi` as the latitude,
        :math:`x` is easting and :math:`y` is northing.

        .. math::
            x &= R(\lambda -\lambda _{0})\\
            y &= R\ln \left[\tan \left(\frac{\pi}{4} + \frac{\varphi - \varphi_0}{2}\right)\right]
        """
        reference_coordinate = Position(reference_coordinate)
        easting, northing = wgs84_to_local_mercator(
            self.latitude, self.longitude,
            reference_coordinate.latitude, reference_coordinate.longitude
        )
        return easting, northing

    def local_length_scale(self):
        """How many nautical miles one longitude minute is

        This gives the apparent length scale for the x-axis in
        mercator projections, i.e., cos(latitude).
        The scaleratio for an x-axis should be set to this value,
        if equal length x- and y-axes are desired, e.g.,
        ```
        xaxis=dict(
            title_text='Longitude',
            constrain='domain',
            scaleanchor='y',
            scaleratio=pos.local_length_scale(),
        ),
        yaxis=dict(
            title_text='Latitude',
            constrain='domain',
        ),
        ```
        """
        return np.cos(np.radians(self.latitude.item()))


class BoundingBox:
    def __init__(self, west, south, east, north):
        self.west = west
        self.south = south
        self.east = east
        self.north = north

    def __repr__(self):
        return f"{type(self).__name__}({self.west}, {self.south}, {self.east}, {self.north})"

    @property
    def north_west(self):
        return Position(self.north, self.west)

    @property
    def north_east(self):
        return Position(self.north, self.east)

    @property
    def south_west(self):
        return Position(self.south, self.west)

    @property
    def south_east(self):
        return Position(self.south, self.east)

    @property
    def center(self):
        return Position(latitude=(self.north + self.south) / 2, longitude=(self.west + self.east) / 2)

    def __contains__(self, position):
        position = Position(position)
        if (self.west <= position.longitude <= self.east) and (self.south <= position.latitude <= self.north):
            return True

    def overlaps(self, other):
        return (
                other.north_west in self
                or other.north_east in self
                or other.south_west in self
                or other.south_east in self
                or self.north_west in other
                or self.north_east in other
                or self.south_west in other
                or self.south_east in other
            )

    def to_geojson(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [self.west, self.south],  # Lower-left corner
                    [self.east, self.south],  # Lower-right corner
                    [self.east, self.north],  # Upper-right corner
                    [self.west, self.north],  # Upper-left corner
                    [self.west, self.south],  # Closing the polygon by repeating the first point
                ]]
            }
        }

    def zoom_level(self, pixels=800):
        center = self.center
        westing, northing = self.north_west.to_local_mercator(center)
        easting, southing = self.south_east.to_local_mercator(center)
        extent = max((northing - southing) / center.local_length_scale(), (easting - westing))
        # This has something to do with the size of a tile in pixels (256),
        # the length of the equator (40_000_000), and then some manual scaling
        # to fix the remainder of issues. Worked nice in plotly 5.18, calling mapbox.
        zoom = np.log2(40_000_000 * pixels / 256 / extent).item() - 1.2
        return zoom


class Line(Position):
    @classmethod
    def stack_positions(cls, positions, dim='point', **kwargs):
        """Stacks multiple positions into a line"""
        coordinates = [Position(pos).coordinates for pos in positions]
        coordinates = xr.concat(coordinates, dim=dim)
        return cls(coordinates, **kwargs)

    @classmethod
    def concatenate(cls, lines, dim=None, nan_between_lines=False, **kwargs):
        """Concatenates multiple lines

        If the lines are not connected, it is useful to set `nan_between_lines=True`, which puts
        a nan element between each line. This makes most plotting libraries split the lines in
        visualizations.
        """
        first_line_coords = lines[0].coordinates
        if dim is None:
            if len(first_line_coords.dims) != 1:
                raise ValueError("Cannot guess concatenation dimensions for multi-dimensional line.")
            dim = next(iter(first_line_coords.dims))

        if nan_between_lines:
            nan_data = xr.full_like(first_line_coords.isel({dim: 0}), np.nan).expand_dims(dim)
            lines = sum([[line.coordinates, nan_data] for line in lines], [])
        coordinates = xr.concat(lines, dim=dim)
        return cls(coordinates, **kwargs)

    def __init__(self, *args, dim=None, **kwargs):
        latitude, longitude = self.parse_coordinates(*args, **kwargs)
        if not isinstance(latitude, xr.DataArray):
            latitude = xr.DataArray(latitude, dims=dim)
        if not isinstance(longitude, xr.DataArray):
            longitude = xr.DataArray(longitude, dims=dim)
        self.coordinates = xr.Dataset(data_vars=dict(latitude=latitude, longitude=longitude))

    def __repr__(self):
        return f"{type(self).__name__} with {self.coordinates.latitude.size} points"

    @property
    def bounding_box(self):
        try:
            return self._bounding_box
        except AttributeError:
            pass
        west = self.longitude.min().item()
        east = self.longitude.max().item()
        north = self.latitude.max().item()
        south = self.latitude.min().item()
        self._bounding_box = BoundingBox(west=west, south=south, east=east, north=north)
        return self._bounding_box


class Track(Line):
    def __init__(self, data):
        self.data = data

    @property
    def coordinates(self):
        return self.data[["latitude", "longitude"]]

    @property
    def time(self):
        return self.data["time"]



def position(*args, **kwargs):
    """Stacks latitude and longitude in a xr.Dataset

    This function supports multiple variants of calling signature:

    `position(dataset)`
        This returns a dataset with at least `latitude` and `longitude`
        The input dataset can be any object with latitude and longitude properties.
    `position(latitude=lat, longitude=lon)`
    `position(lat, lon)`
        These uses latitude and longitude in degrees with decimals.
        E.g., (57.6931022, 11.974318) -> 57.6931022°N 11.974318°E
        This format can be used as either positional or keyword arguments.
    `position(lat, lat_min, lon, lon_min)`
        This uses degrees and decimal minutes format for the coordinates.
        E.g., (57, 41.586132, 11, 58.45908) -> 57° 41.58613200'N 11° 58.45908000'E
    `position(lat, lat_min, lat_sec, lon, lon_min, lon_sec)`
        This uses degrees and minutes, decimal seconds format for the coordinates.
        E.g., (57, 41, 35.17, 11, 58, 27.54) -> 57° 41' 35.17"N 11° 58' 27.54"E
    `position(..., t)`
    `position(..., time=t)`
        A last optional positional or keyword argument can be used to supply a time
        for the position as well.
    """
    if len(args) == 1:
        arg = args[0]
        args = tuple()
        if isinstance(arg, xr.Dataset):
            if 'latitude' not in arg or 'longitude' not in arg:
                raise ValueError('latitude and longitude apparently not in position dataset')
            return arg
        else:
            if hasattr(arg, 'latitude') and hasattr(arg, 'latitude'):
                if hasattr(arg, 'time'):
                    args = (arg.latitude, arg.longitude, arg.time)
                else:
                    args = (arg.latitude, arg.longitude)
            else:
                # We should never have just a single argument, try unpacking.
                *args, = arg

    latitude = kwargs.pop('latitude', None)
    longitude = kwargs.pop('longitude', None)
    time = kwargs.pop('time', None)

    if len(args) % 2:
        if time is not None:
            raise TypeError("position got multiple values for argument 'time'")
        *args, time = args

    if len(args) != 0:
        if latitude is not None:
            raise TypeError("position got multiple values for argument 'latitude'")
        if longitude is not None:
            raise TypeError("position got multiple values for argument 'longitude'")

        if len(args) == 2:
            latitude, longitude = args
        elif len(args) == 4:
            (
                latitude_degrees, latitude_minutes,
                longitude_degrees, longitude_minutes
             ) = args
            latitude = latitude_degrees + latitude_minutes / 60
            longitude = longitude_degrees + longitude_minutes / 60
        elif len(args) == 6:
            (
                latitude_degrees, latitude_minutes, latitude_seconds,
                longitude_degrees, longitude_minutes, longitude_seconds
             ) = args
            latitude = latitude_degrees + latitude_minutes / 60 + latitude_seconds / 3600
            longitude = longitude_degrees + longitude_minutes / 60 + longitude_seconds / 3600
        else:
            raise TypeError(f"Undefined number of non-time arguments for position {len(args)} was given, expects 2, 4, or 6.")

    dataset = xr.Dataset({'latitude': latitude, 'longitude': longitude})
    if time is not None:
        # TODO: convert the time into a numpy datetime!
        dataset['time'] = time
    return dataset


def format_coordinates(*args, format='minutes', precision=None, **kwargs):
    pos = position(*args, **kwargs)
    latitude = np.atleast_1d(pos.latitude.values)
    longitude = np.atleast_1d(pos.longitude.values)
    def ns(lat):
        return 'N' if lat > 0 else 'S'
    def ew(lon):
        return 'E' if lon > 0 else 'W'

    if format.lower()[:3] == 'deg':
        if precision is None:
            precision = 6

        def format(lat, lon):
            lat = f"{abs(lat):.{precision}f}°{ns(lat)}"
            lon = f"{abs(lon):.{precision}f}°{ew(lon)}"
            return lat + " " + lon

    elif format.lower()[:3] == 'min':
        if precision is None:
            precision = 4

        def format(lat, lon):
            latdeg, latmin = np.divmod(abs(lat) * 60, 60)
            londeg, lonmin = np.divmod(abs(lon) * 60, 60)
            lat = f"{abs(latdeg):.0f}°{latmin:.{precision}f}'{ns(lat)}"
            lon = f"{abs(londeg):.0f}°{lonmin:.{precision}f}'{ew(lon)}"
            return lat + " " + lon
    elif format.lower()[:3] == 'sec':
        format = 'sec'
        if precision is None:
            precision = 2

        def format(lat, lon):
            latdeg, latmin = np.divmod(abs(lat) * 60, 60)
            londeg, lonmin = np.divmod(abs(lon) * 60, 60)
            latmin, latsec = np.divmod(latmin * 60, 60)
            lonmin, lonsec = np.divmod(lonmin * 60, 60)
            lat = f"""{abs(latdeg):.0f}°{latmin:.0f}'{latsec:.{precision}f}"{ns(lat)}"""
            lon = f"""{abs(londeg):.0f}°{latmin:.0f}'{lonsec:.{precision}f}"{ew(lon)}"""
            return lat + " " + lon

    formatted = [
        format(lat, lon)
        for lat, lon in zip(latitude, longitude)
    ]
    if len(formatted) == 1:
        return formatted[0]
    return formatted


def distance_between(first, second):
    """Calculate the distance between two coordinates."""
    def func(lat_1, lon_1, lat_2, lon_2):
        return geod.Inverse(lat_1, lon_1, lat_2, lon_2, outmask=geod.DISTANCE)['s12']
    return xr.apply_ufunc(
        func,
        first.latitude, first.longitude,
        second.latitude, second.longitude,
        vectorize=True,
        join='inner',
    )


def wrap_angle(angle):
    '''Wrap an angle to (-180, 180].'''
    return 180 - np.mod(180 - angle, 360)


def bearing_to(first, second):
    """Calculate the heading from one coordinate to another."""
    def func(lat_1, lon_1, lat_2, lon_2):
        return geod.Inverse(lat_1, lon_1, lat_2, lon_2, outmask=geod.AZIMUTH)['azi1']
    return xr.apply_ufunc(
        func,
        first.latitude, first.longitude,
        second.latitude, second.longitude,
        vectorize=True,
        join='inner',
    )


def average_heading(heading, resolution=None):
    complex_heading = np.exp(1j * np.radians(heading))
    heading = wrap_angle(np.degrees(np.angle(complex_heading.mean())))
    if resolution is None:
        return heading

    if not isinstance(resolution, str):
        return wrap_angle(np.round(heading / 360 * resolution) * 360 / resolution)

    resolution = resolution.lower()
    if '4' in resolution or 'four' in resolution:
        resolution = 4
    elif '8' in resolution or 'eight' in resolution:
        resolution = 8
    elif '16' in resolution or 'sixteen' in resolution:
        resolution = 16
    else:
        raise ValueError(f"Unknown resolution specifier '{resolution}'")

    names = [
        (-180., 'south'),
        (-90., 'west'),
        (0., 'north'),
        (90., 'east'),
        (180., 'south'),
    ]

    if resolution >= 8:
        names.extend([
            (-135., 'southwest'),
            (-45., 'northwest'),
            (45., 'northeast'),
            (135., 'southeast'),
        ])
    if resolution >= 16:
        names.extend([
            (-157.5, 'south-southwest'),
            (-112.5, 'west-southwest'),
            (-67.5, 'west-northwest'),
            (-22.5, 'north-northwest'),
            (22.5, 'north-northeast'),
            (67.5, 'east-northeast'),
            (112.5, 'east-southeast'),
            (157.5, 'south-southeast'),
        ])
    name = min([(abs(deg - heading), name) for deg, name in names], key=lambda x: x[0])[1]
    return name.capitalize()


def angle_between(center, first, second):
    """Calculate the angle between two coordinates, as seen from a center vertex."""
    first_heading = bearing_to(center, first)
    second_heading = bearing_to(center, second)
    return wrap_angle(second_heading - first_heading)


def shift_position(pos, distance, bearing):
    def func(lat, lon, head, dist):
        out = geod.Direct(lat, lon, head, dist, outmask=geod.LATITUDE | geod.LONGITUDE)
        return out['lat2'], out['lon2']
    lat, lon = xr.apply_ufunc(
        func,
        pos.latitude,
        pos.longitude,
        bearing,
        distance,
        vectorize=True,
        output_core_dims=[[], []]
    )
    return position(lat, lon)


def calculate_course(positions, inplace=False):
    interior_course = bearing_to(positions.shift(time=1).dropna('time'), positions.shift(time=-1).dropna('time'))
    first_course = bearing_to(positions.isel(time=0), positions.isel(time=1)).assign_coords(time=positions.time[0])
    last_course = bearing_to(positions.isel(time=-2), positions.isel(time=-1)).assign_coords(time=positions.time[-1])
    course = xr.concat([first_course, interior_course, last_course], dim='time')
    if inplace:
        positions['course'] = course
        return positions
    return course


def calculate_speed(positions, inplace=False, knots=False):
    distance_delta = distance_between(positions.shift(time=1).dropna('time'), positions.shift(time=-1).dropna('time'))
    time_delta = (positions.time.shift(time=-1).dropna('time') - positions.time.shift(time=1).dropna('time')) / np.timedelta64(1, 's')
    interior_speed = distance_delta / time_delta

    first_distance = distance_between(positions.isel(time=0), positions.isel(time=1))
    first_time = (positions.time[1] - positions.time[0]) / np.timedelta64(1, 's')
    first_speed = (first_distance / first_time).assign_coords(time=positions.time[0])

    last_distance = distance_between(positions.isel(time=-2), positions.isel(time=-1))
    last_time = (positions.time[-1] - positions.time[-2]) / np.timedelta64(1, 's')
    last_speed = (last_distance / last_time).assign_coords(time=positions.time[-1])
    speed = xr.concat([first_speed, interior_speed, last_speed], dim='time')

    if knots:
        speed = speed * one_knot
        speed.attrs['unit'] = 'knots'
    else:
        speed.attrs['unit'] = 'm/s'

    if inplace:
        positions['speed'] = speed
        return positions
    return speed


def circle_at(center, radius, n_points=72):
    angles = np.linspace(0, 360, n_points + 1)
    # positions = []
    latitudes = np.zeros(angles.size)
    longitudes = np.zeros(angles.size)
    for idx, angle in angles:
        out = geod.Direct(center.latitude, center.longitude, angle, radius)
        latitudes[idx] = out['lat2']
        longitudes[idx] = out['lon2']
    return position(latitude=latitudes, longitude=longitudes)


def closest_point(reference, track):
    distances = distance_between(reference, track)
    return track.assign(distance=distances).isel(distances.argmin(...))


def aspect_segments(
    reference,
    track,
    angles,
    segment_min_length=None,
    segment_min_angle=None,
    segment_min_duration=None,
):
    """Get time segments corresponding to specific aspect angles.

    Parameters
    ----------
    track : xarray.Dataset w. latitude and longitude
        Track from which to analyze the segments.
    angles : array_like
        The aspect angles to find. This is a value in degrees relative to the closest point to
        the track from the reference point.
    segment_min_length : numeric, optional
        The minimum length of each segment, in meters.
    segment_min_angle : numeric, optional
        The minimum length of each segment, seen as an angle from the reference point.
    segment_min_duration : numeric, optional
        The minimum duration of each window, in seconds.
    """
    track = track[['latitude', 'longitude']]  # Speeds up some computations since we're not managing unnecessary data
    cpa = closest_point(reference, track)  # If the path if to long this will crunch a shit-ton of data...

    try:
        iter(angles)
    except TypeError:
        single_segment = True
        angles = [angles]
    else:
        single_segment = False

    angles = np.sort(angles)
    track = track.assign(aspect_angle=angle_between(reference, cpa, track))
    if track.aspect_angle[0] > track.aspect_angle[-1]:
        # We want the angles to be negative before cpa and positive after
        track['aspect_angle'] *= -1

    angles = xr.DataArray(angles, coords={'segment': angles})
    center_indices = abs(angles - track.aspect_angle).argmin('time')
    segment_centers = track.isel(time=center_indices)

    # Run a check that we get the windows we want. A sane way might be to check that the
    # first and last windows are closer to their targets than the next window.
    if angles.size > 1:
        actual_first_angle = track.aspect_angle.sel(time=segment_centers.isel(segment=0).time)
        if abs(actual_first_angle - angles.isel(segment=0)) > abs(actual_first_angle - angles.isel(segment=1)):
            raise ValueError(f'Could not find window centered at {angles.isel(segment=0)}⁰, found at most {actual_first_angle}⁰.')
        actual_last_angle = track.aspect_angle.sel(time=segment_centers.isel(segment=-1).time)
        if abs(actual_last_angle - angles.isel(segment=-1)) > abs(actual_first_angle - angles.isel(segment=-2)):
            raise ValueError(f'Could not find window centered at {angles.isel(segment=-1)}⁰, found at most {actual_last_angle}⁰.')

    segments = []
    for angle, segment_center in segment_centers.groupby('segment', squeeze=False):
        segment_center = segment_center.squeeze()
        # Finding the start of the window
        # The inner loops here are somewhat slow, likely due to indexing into the xr.Dataset all the time
        # At the time of writing (2023-12-14), there seems to be no way to iterate over a dataset in reverse order.
        # The `groupby` method can be used to iterate forwards, which solves finding the end of the segment,
        # but calling `track.sel(time=slice(t, None, -1)).groupby('time')` still iterates in the forward order.
        center_idx = int(np.abs(track.time - segment_center.time).argmin())
        start_idx = center_idx
        if segment_min_angle:
            while abs(segment_center.aspect_angle - track.isel(time=start_idx).aspect_angle) < segment_min_angle / 2:
                start_idx -= 1
                if start_idx < 0:
                    raise ValueError(f'Start of window at {angle}⁰ not found in track. Not sufficiently high angles from window center.')
        if segment_min_duration:
            while abs(segment_center.time - track.time.isel(time=start_idx)) / np.timedelta64(1, 's') < segment_min_duration / 2:
                start_idx -= 1
                if start_idx < 0:
                    raise ValueError(f'Start of window at {angle}⁰ not found in track. Not sufficient time from window center.')
        if segment_min_length:
            while distance_between(segment_center, track.isel(time=start_idx)) < segment_min_length / 2:
                start_idx -= 1
                if start_idx < 0:
                    raise ValueError(f'Start of window at {angle}⁰ not found in track. Not sufficient distance from window center.')
        # Finding the end of the window
        stop_idx = center_idx
        if segment_min_angle:
            while abs(segment_center.aspect_angle - track.isel(time=stop_idx).aspect_angle) < segment_min_angle / 2:
                stop_idx += 1
                if stop_idx == track.sizes['time']:
                    raise ValueError(f'End of window at {angle}⁰ not found in track. Not sufficiently high angles from window center.')
        if segment_min_duration:
            while abs(segment_center.time - track.time.isel(time=stop_idx)) / np.timedelta64(1, 's') < segment_min_duration / 2:
                stop_idx += 1
                if stop_idx == track.sizes['time']:
                    raise ValueError(f'End of window at {angle}⁰ not found in track. Not sufficient time from window center.')
        if segment_min_length:
            while distance_between(segment_center, track.isel(time=stop_idx)) < segment_min_length / 2:
                stop_idx += 1
                if stop_idx == track.sizes['time']:
                    raise ValueError(f'End of window at {angle}⁰ not found in track. Not sufficient distance from window center.')

        # Creating the window and saving some attributes
        if start_idx == stop_idx:
            segments.append(segment_center.assign(length=0, angle_span=0, duration=0).reset_coords('time'))
        else:
            segment_start, segment_stop = track.isel(time=start_idx), track.isel(time=stop_idx)
            segments.append(
                xr.concat([segment_start, segment_center, segment_stop], dim='time')
                .assign_coords(edge=('time', ['start', 'center', 'stop']))
                .swap_dims(time='edge')
                .assign(
                    length=distance_between(segment_start, segment_stop),
                    angle_span=segment_stop.aspect_angle - segment_start.aspect_angle,
                    duration=(segment_stop.time - segment_start.time) / np.timedelta64(1, 's'),
                )
                .reset_coords('time')
            )

    if single_segment:
        return segments[0]
    return xr.concat(segments, dim='segment')


def blueflow(path, renames=None):
    import pandas
    ext = os.path.splitext(path)[1]
    if ext == '.xlsx':
        data = pandas.read_excel(path)
    elif ext == '.csv':
        data = pandas.read_csv(path)
    else:
        raise ValueError(f"Unknown fileformat for blueflow file '{path}'. Only xlsx and csv supported.")
    data = data.to_xarray()
    names = {}
    exp = r'([^\(\)\[\]]*) [\[\(]([^\(\)\[\]]*)[\]\)]'
    for key in list(data):
        name, unit = re.match(exp, key).groups()
        names[key] = name.strip()
        data[key].attrs['unit'] = unit
    data = data.rename(names)

    renames = {
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Timestamp': 'time',
        'Time': 'time',
        'Tidpunkt': 'time',
        'Latitud': 'latitude',
        'Longitud': 'longitude',
    } | (renames or {})

    renames = {key: value for key, value in renames.items() if key in data}
    data = data.rename(renames).set_coords('time').swap_dims(index='time').drop('index')
    if not np.issubdtype(data.time.dtype, np.datetime64):
        data['time'] = xr.apply_ufunc(np.datetime64, data.time, vectorize=True, keep_attrs=True)
    return data


def correct_gps_offset(positions, heading, forwards=0, portwards=0, to_bow=0, to_stern=0, to_port=0, to_starboard=0, inplace=False):
    """Correct positions with respect to ship heading.

    The positions will be shifted in the `heading` direction by `forwards + (to_bow - to_stern) / 2`,
    and towards "port" `heading - 90` by `portwards + (to_port - to_starboard) / 2`.
    Typical usage is to give the receiver position using the `to_x` arguments, and the desired
    acoustic reference location with the `forwards` and `portwards` arguments.
    Inserting correct values for all the `to_x` arguments will center the position on the ship middle, so that
    the `forwards` and `portwards` arguments are relative to the ship center. Alternatively, leave the `to_x` arguments
    as the default 0 and only give the desired `forwards` and `portwards` arguments.

    Parameters
    ----------
    positions : xarray.Dataset w. latitude and longitude
        The positions to modify
    heading : array like
        The headings of the ship. Must be compatible with the positions Dataset
    forwards : numeric, default 0
        How much forwards to shift the positions, in meters
    portwards : numeric, default 0
        How much to port side to shift the positions, in meters
    to_bow : numeric, default 0
        The distance to the bow from the receiver, in meters
    to_stern : numeric, default 0
        The distance to the stern from the receiver, in meters
    to_port : numeric, default 0
        The distance to the port side from the receiver, in meters
    to_starboard : numeric, default 0
        The distance to the starboard side from the receiver, in meters
    inplace : boolean, default False
        If this is true, the corrected positions will be assigned the the input position dataset,
        which is returned. If false, a new dataset with only latitude and longitude is returned.
    """
    forwards = forwards + (to_bow - to_stern) / 2
    portwards = portwards + (to_port - to_starboard) / 2
    front_back_fixed = shift_position(positions, forwards, heading)
    sideways_fixed = shift_position(front_back_fixed, portwards, heading - 90)
    if inplace:
        if isinstance(positions, xr.Dataset):
            positions['latitude'] = sideways_fixed.latitude
            positions['longitude'] = sideways_fixed.longitude
        else:
            positions.latitude = sideways_fixed.latitude
            positions.longitude = sideways_fixed.longitude
        return positions
    else:
        return sideways_fixed
