"""Storage and reading of recorded acoustic signals."""
import datetime
import numpy as np
from . import positional, signals
import os
import re
import soundfile
import abc


# def _manage_identitymapped_data(identifiers, data, preprocessor=lambda x: x):
#     try:
#         data = {str(key): preprocessor(val) for key, val in data.items()}
#     except AttributeError as err:
#         if str(err).endswith("object has no attribute 'items'"):
#             data = {key: preprocessor(data) for key in identifiers}
#         else:
#             raise
#     else:
#         data = {key: preprocessor(data[key]) for key in identifiers}
#     return data


class Recording(abc.ABC):
    def __init__(self, identifiers=None):
        self.identifiers = identifiers

    @property
    def identifiers(self):
        ids = self._identifiers
        if len(ids) == 0:
            return None
        if len(ids) == 1:
            return ids[0]
        return ids

    @identifiers.setter
    def identifiers(self, identifiers):
        if identifiers is None or isinstance(identifiers, str):
            identifiers = [identifiers]
        else:
            try:
                identifiers = [str(identifier) for identifier in identifiers]
            except TypeError as err:
                if str(err).endswith('object is not iterable'):
                    # identifiers = str(identifiers)
                    identifiers = [identifiers]
                else:
                    raise
                identifiers = [str(identifier) for identifier in identifiers]
        self._identifiers = identifiers

    class _identfier_data_mapper:
        def __init__(self, preprocessor):
            self.name = preprocessor.__name__
            self.preprocessor = preprocessor

        def __get__(self, owner, owner_class=None):
            data = getattr(owner, '_' + self.name)
            if not isinstance(owner.identifiers, list):
                data, = data.values()
            return data

        def __set__(self, owner, data):
            try:
                # Multiple data
                data = {str(key): self.preprocessor(owner, val) for key, val in data.items()}
                multiple_data = True
            except AttributeError as err:
                if str(err).endswith("object has no attribute 'items'"):
                    data = self.preprocessor(owner, data)
                    multiple_data = False
                else:
                    raise

            if isinstance(owner.identifiers, list):
                if multiple_data:
                    data = {key: data[key] for key in owner.identifiers}
                else:
                    data = {key: data for key in owner.identifiers}
            else:
                if multiple_data:
                    data = data[owner.identifiers]
                data = {owner.identifiers: data}
            #     try:
            #         # Multiple data, multiple identifiers
            #         data = {str(key): self.preprocessor(owner, val) for key, val in data.items()}
            #     except AttributeError as err:
            #         if str(err).endswith("object has no attribute 'items'"):
            #             # Singnle data, multiple identifiers
            #             data = {key: self.preprocessor(owner, data) for key in owner.identifiers}
            #         else:
            #             raise
            #     else:
            #         data = {key: data[key] for key in owner.identifiers}
            # else:
            #     try:
            #         # Multiple data, multiple identifiers
            #         data = {str(key): self.preprocessor(owner, val) for key, val in data.items()}

            setattr(owner, '_' + self.name, data)
    # @identifiers.setter
    # def identifiers(self, identifiers):
    #     if identifiers is None or isinstance(identifiers, str):
    #         identifiers = [identifiers]
    #     else:
    #         try:
    #             iter(identifiers)
    #         except TypeError as err:
    #             if str(err).endswith('object is not iterable'):
    #                 identifiers = [identifiers]
    #         identifiers = [str(identifier) for identifier in identifiers]
    #     self._identifiers = identifiers

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
        time_window = positional.TimeWindow(
            start=start,
            stop=stop,
            center=center,
            duration=duration,
        )
        return self[time_window]

    def copy(self, deep=False):
        obj = type(self).__new__(type(self))
        obj._identifiers = self._identifiers
        return obj

    @abc.abstractmethod
    def __getitem__(self, window):
        """Restrict the time range.

        This gets the same signal but restricted to a time range specified
        with a TimeWindow object.

        Parameters
        ----------
        window : `timestamps.TimeWindow`
            The time window to restrict to.
        """
        ...

    @property
    @abc.abstractmethod
    def signal(self):
        """Get the actual time signal in the appropriate time window."""
        ...
# class Signal:
#     # I'm not sure this will be a good interface. Many of the recordings we work with are
#     # too long to fit in memory, so we will never be able to just load it into a numpy array.
#     # This means that we most of the time have to use the `time_range` method to get the
#     # data from disk? Perhaps the `time_range` method returns a simple numpy array?
#     def __init__(self, signal, samplerate, start_time):
#         self.signal = signal
#         self.samplerate = samplerate
#         self.times = timestamps.SampledSequence(
#             samplerate=samplerate,
#             start_time=start_time,
#             num_samples=signal.shape[-1]
#         )

#     @property
#     def metadata(self):
#         return dict(
#             samplerate=self.times.samplerate,
#             start_time=self.times.start_time,
#         )

#     def time_range(self, start, stop):
#         """Get a subset of the hydrophone data.

#         Parameters
#         ----------
#         start : datetime or numeric
#             A datetime will be used and referenced to the measurement start.
#             Other numeric values will be interpreted as seconds from the start
#             of the measurement.
#         stop : datetime or numeric
#             A datetime will be used and referenced to the measurement start.
#             Other numeric values will be interpreted as seconds from the start
#             of the measurement.
#         """
#         start_idx, stop_idx = self.times.time_range(start, stop)

#         signal = self.signal[..., start_idx:stop_idx]
#         metadata = self.metadata
#         metadata['start_time'] = start
#         return type(self)(signal=signal, **self.metadata)


class Hydrophone(Recording):
    def __init__(
        self,
        position=None,
        depth=None,
        calibration=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.position = position
        self.depth = depth
        self.calibration = calibration

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj._position = self._position
        obj._depth = self._depth
        obj._calibration = self._calibration
        return obj

    # @property
    # def depth(self):
    #     return self._depth

    # @depth.setter
    # def depth(self, value):
    #     def parse(depth):
    #         return float(depth) if depth is not None else None
    #     self._depth = _manage_identitymapped_data(value, self.identifiers, parse)

    # @property
    # def calibration(self):
    #     return self._calibration

    # @calibration.setter
    # def calibration(self, value):
    #     def parse(calibration):
    #         return float(calibration) if calibration is not None else None
    #     self._calibration = _manage_identitymapped_data(value, self.identifiers, parse)

    # @property
    # def position(self):
    #     return self._position

    # @depth.setter
    # def depth(self, value):
    #     def parse(depth):
    #         return float(depth) if depth is not None else None
    #     value = _manage_identitymapped_data(value, self.identifiers, parse)

    @Recording._identfier_data_mapper
    def depth(self, value):
        return float(value) if value is not None else None

    @Recording._identfier_data_mapper
    def calibration(self, value):
        return float(value) if value is not None else None

    @Recording._identfier_data_mapper
    def position(self, value):
        if isinstance(value, positional.Position):
            return value
        elif value is not None:
            try:
                longitude, latitude = value
            except ValueError:
                raise ValueError(f'Cannot unpack position data {value} into longitude and latitude!')
            return positional.Position(longitude=longitude, latitude=latitude)

    # @property
    # def position(self):
    #     """The position of the Hydrophone, as a `Position` object."""
    #     return self._position

    # @position.setter
    # def position(self, value):
    #     if isinstance(value, positional.Position):
    #         self._position = value
    #     elif value is not None:
    #         try:
    #             longitude, latitude = value
    #         except ValueError:
    #             raise ValueError(f'Cannot unpack position data {value} into longitude and latitude!')
    #         self._position = positional.Position(longitude=longitude, latitude=latitude)
    #     else:
    #         self._position = None

    # def spectrogram(self, *args, **kwargs):
    #     return Spectrogram.from_timesignal(
    #         signal=self.signal,
    #         samplerate=self.samplerate,
    #         start_time=self.start_time,
    #         **args, **kwargs
    #     )


# class Spectrogram(Signal):
#     # TODO: remove this code
#     # I'm starting to doubt that it's a good idea to have this class.
#     # For long recordings, it will be neccessary to calculate psd/bandlevels in
#     # chunks anyhow, since the entire spectrogram won't fit in memory.
#     # This indicated that we might be better off making functions/classes for each
#     # of the actual outputs that we want to have as the end result, and only use
#     # spectrograms as a visualization tool?
#     @classmethod
#     def from_timesignal(
#         cls,
#         signal,
#         samplerate,
#         start_time,
#         window_duration=None,
#         window='hann',
#         overlap=0.5,
#     ):
#         window_samples = round(window_duration * samplerate)
#         overlap_samples = round(window_duration * overlap * samplerate)
#         f, t, Sxx = scipy.signal.spectrogram(
#             x=signal,
#             fs=samplerate,
#             window=window,
#             nperseg=window_samples,
#             noverlap=overlap_samples,
#         )
#         self = cls.__new__(cls)
#         self.__init__(
#             signal=Sxx,
#             samplerate=samplerate / (window_samples - overlap_samples),
#             frequencies=f,
#             start_time=start_time + timestamps.datetime.timedelta(seconds=t[0])
#         )

#     def __init__(
#         self,
#         signal,
#         samplerate,
#         frequencies,
#         start_time,
#     ):
#         super().__init__(signal=signal, samplerate=samplerate, start_time=start_time)
#         self.times = timestamps.SampledSequence(samplerate=samplerate, start_time=start_time, num_samples=signal.shape[-1])
#         self.frequencies = frequencies

#     @property
#     def metadata(self):
#         return super().metadata | dict(
#             frequencies=self.frequencies,
#         )

    # def time_range(self, start, stop):
    #     start_idx, stop_idx = self.times.time_range(start, stop)
    #     obj = type(self).__new__(type(self))
    #     obj.frequencies = self.frequencies
    #     obj.times = timestamps.ReferencedSequence(self.times.time[start_idx:stop_idx], self.times._reference)
    #     obj.power_spectral_density = self.power_spectral_density[:, start_idx:stop_idx]
    #     return obj
class SoundTrap(Hydrophone):
    @Recording._identfier_data_mapper
    def files(self, list_of_files):
        if list_of_files is None or len(list_of_files) == 0:
            list_of_files = []
        return list_of_files

    # files = _identity_data()
    #  The file starts are taken from the timestamps in the filename, which is quantized to 1s.
    allowable_interrupt = 1
    # Check files in a folder, parse the unit id and timestamps from the filenames
    # Get position and depth from user input
    # Don't read the files, it's too much data to load at once.
    # Use the `time_window` method to read the appropriate part of the files

    def __init__(self, folder, identifiers=None, timezone='UTC', time_offset=None, **kwargs):
        """Read a folder with SoundTrap data.

        Parameters
        ----------
        folder : str
            Path to the folder with the data.
        calibrations : dict or numeric
            A dict with the calibration values of the SoundTraps.
            If a single value is given, it will be used for all read data.
            Give as a value in dB re. 1/μPa, e.g. -188.5
        depth : dict or numeric
            A dict with the depths of the SoundTraps, in meters.
            If a single value is given, it will be used for all read data.
        identifiers : int, str, list
            The serial numbers of the Hydrophones, optional filter for only reading a subset of the data.
            Can be given as an integer, a string, or as a list of ints or strings.
        """
        self.identifiers = identifiers
        self.timezone = timezone
        tz = positional.dateutil.tz.gettz(self.timezone)
        serial_numbers = self.identifiers
        if serial_numbers is None:
            pattern = r'\d{4}'
        elif isinstance(serial_numbers, str):
            pattern = serial_numbers
        else:
            try:
                iter(serial_numbers)
            except TypeError as err:
                if str(err).endswith('object is not iterable'):
                    serial_numbers = [serial_numbers]
                else:
                    raise
            pattern = '|'.join(map(str, serial_numbers))

        self.folder = folder
        pattern = '(' + pattern + r')\.(\d{12}).wav'

        self._identifiers = []
        self._files = {}

        if time_offset is None:
            def time_offset(serial_number, timestamp):
                return 0
        elif isinstance(time_offset, dict):
            time_offset_dict = time_offset
            def time_offset(serial_number, timestamp):
                try:
                    return time_offset_dict[serial_number]
                except KeyError:
                    pass
                try:
                    return time_offset_dict[serial_number + '_' + timestamp]
                except KeyError:
                    pass
                try:
                    return time_offset_dict[(serial_number, timestamp)]
                except KeyError:
                    pass
                if int(serial_number) != serial_number:
                    return time_offset(int(serial_number), timestamp)
                raise KeyError(f'Could not find time offset for serial number {serial_number} and timestamp {timestamp}')

        for file in sorted(os.listdir(self.folder)):
            if match := re.match(pattern, file):
                sn, time = match.groups()
                if sn not in self._identifiers:
                    self._identifiers.append(sn)
                    self._files[sn] = []
                info = soundfile.info(os.path.join(self.folder, file))
                info.start_time = datetime.datetime.strptime(time, r'%y%m%d%H%M%S').replace(tzinfo=tz) + datetime.timedelta(seconds=time_offset(sn, time))
                info.stop_time = info.start_time + datetime.timedelta(seconds=info.duration)
                self._files[sn].append(info)
                if info.samplerate != self.samplerate:
                    raise ValueError('Cannot handle multiple samplerates in one soundtrap object')

        start_time = max([files[0].start_time for files in self._files.values()])
        stop_time = min([files[-1].stop_time for files in self._files.values()])
        self.time_window = self._raw_time_window = positional.TimeWindow(start=start_time, stop=stop_time)

        # if len(self._identifiers) == 1:
        #     self._identifiers = self._identifiers[0]
        # elif len(self._identifiers) == 0:
        #     raise ValueError(f'No recordings found that match serial number filter {serial_numbers}')

        super().__init__(identifiers=self.identifiers, **kwargs)

        # try:
        #     self.calibrations = {int(key): float(val) for key, val in calibrations.items()}
        # except AttributeError as err:
        #     if str(err).endswith("object has no attribute 'items'"):
        #         self.calibrations = {key: float(calibrations) for key in self.serial_numbers}
        #     else:
        #         raise

        # try:
        #     self.calibrations = {int(key): float(val) for key, val in calibrations.items()}
        # except AttributeError as err:
        #     if str(err).endswith("object has no attribute 'items'"):
        #         self.calibrations = {key: float(calibrations) for key in self.serial_numbers}
        #     else:
        #         raise

    @property
    def samplerate(self):
        return self._files[self._identifiers[0]][0].samplerate

    def copy(self, deep=False):
        obj = super().copy(deep=deep)
        obj.folder = self.folder
        obj._files = self._files
        obj.time_window = self.time_window
        obj._raw_time_window = self._raw_time_window
        return obj

    def __getitem__(self, window):
        if window.start < self._raw_time_window.start:
            raise ValueError(f'Cannot select data starting at {window.start} from recording starting at {self._raw_time_window.start}')
        if window.stop > self._raw_time_window.stop:
            raise ValueError(f'Cannot select data until {window.stop} from recording ending at {self._raw_time_window.stop}')
        obj = self.copy()
        obj.time_window = window
        return obj

    @property
    def signal(self):
        read_signals = {}
        samples_to_read = round((self.time_window.stop - self.time_window.start).total_seconds() * self.samplerate)
        for sn in self._identifiers:
            files = self._files[sn]
            for info in reversed(files):
                if info.start_time <= self.time_window.start:
                    break
            else:
                raise ValueError(f'Cannot read data starting from {self.time_window.start}, earliest file start is {info.start_time}')

            if self.time_window.stop <= info.stop_time:
                # The requested data exists within one file.
                # Read the data from file and add it to the signal array.
                ...
                start_idx = np.math.floor((self.time_window.start - info.start_time).total_seconds() * self.samplerate)
                stop_idx = start_idx + samples_to_read
                read_signals[sn] = soundfile.read(info.name, start=start_idx, stop=stop_idx, dtype='float32')[0]
                continue  # Go to the next serial number

            # The requested data spans multiple files
            files_to_read = []
            for info in files[files.index(info):]:
                files_to_read.append(info)
                if info.stop_time >= self.time_window.stop:
                    break
            else:
                raise ValueError(f'Cannot read data extending to {self.time_window.stop}, last file ends at {info.stop_time}')

            # Check that the file boundaries are good
            for early, late in zip(files_to_read[:-1], files_to_read[1:]):
                interrupt = (late.start_time - early.stop_time).total_seconds()
                if interrupt > self.allowed_interrupt:
                    raise ValueError(
                        f'Data is not continuous, missing {interrupt} seconds between files '
                        f'ending at {early.stop_time} and starting at {late.start_time}\n'
                        f'{early.name}\n{late.name}'
                    )

            read_chunks = []

            start_idx = (self.time_window.start - files_to_read[0].start_time).total_seconds() * self.samplerate
            chunk = soundfile.read(files_to_read[0].name, start=start_idx, dtype='float32')[0]
            read_chunks.append(chunk)
            samples_to_read -= chunk.size
            for file in files_to_read[1:-1]:
                chunk = soundfile.read(file.name, dtype='float32')
                read_chunks.append(chunk)
                samples_to_read -= chunk.size
            chunk = soundfile.read(files_to_read[-1].name, stop=samples_to_read, dtype='float32')
            read_chunks.append(chunk)
            samples_to_read -= chunk.size
            assert samples_to_read == 0

            read_signals[sn] = np.concatenate(read_chunks, axis=0)
            # Ready to read from the collected files and store in the signal array

        read_signals = np.stack([read_signals[sn] for sn in self._identifiers], axis=0).squeeze()
        calibrations = [self.calibration[sn] for sn in self._identifiers]
        if None not in calibrations:
            return signals.Pressure.from_raw_and_calibration(
                read_signals,
                calibrations,
                samplerate=self.samplerate,
                start_time=self.time_window.start,
            )
        else:
            return signals.Signal(
                read_signals,
                samplerate=self.samplerate,
                start_time=self.time_window.start
            )


class ZarrRecording(Hydrophone):
    def __init__(self, folder):
        self.folder = folder
        self.files = []

        for file in os.listdir(self.folder):
