#ruff: noqa
import uwacan
import numpy as np


class DummyRecording(uwacan.recordings.FileRecording):
    class RecordedFile(uwacan.recordings.FileRecording.RecordedFile):
        filepath = "dummy"
        def __init__(self, start_time, duration, samplerate, ref_time):
            self.filepath = f"{start_time}.dummy"
            self._start_time = start_time
            self._duration = duration
            self._samplerate = samplerate
            self.ref_time = ref_time

        @property
        def start_time(self):
            return self._start_time

        @property
        def stop_time(self):
            return self.start_time.add(seconds=self.duration)

        @property
        def duration(self):
            return self._duration

        @property
        def num_channels(self):
            return 1

        @property
        def num_samples(self):
            return int(self.duration * self.samplerate)

        @property
        def samplerate(self):
            return self._samplerate

        def read_data(self, start_idx=None, stop_idx=None):
            if start_idx is None:
                start_idx = 0
            if stop_idx is None:
                stop_idx = int(self.samplerate * self.duration)
            if start_idx < 0:
                raise ValueError("Cannot read file from before it started")
            if stop_idx > self.num_samples:
                raise ValueError("Cannot read file from after it ended")
            return np.arange(start_idx, stop_idx) / self.samplerate + (self.start_time - self.ref_time).total_seconds()

        def read_info(self):
            self._samplerate = self.__samplerate
            self._stop_time = self._start_time.add(seconds=self.__duration)

    @classmethod
    def make_dummy_recording(cls, num_files, file_duration, samplerate, ref_time="now", gaps=0):
        ref_time = uwacan._core.time_to_datetime(ref_time)
        files = [
            cls.RecordedFile(
                start_time=ref_time.add(seconds=idx * (file_duration + gaps)),
                duration=file_duration,
                samplerate=samplerate,
                ref_time=ref_time
            )
            for idx in range(num_files)
        ]
        return cls(files)

    def time_data(self):
        return uwacan.TimeData(self.raw_data(), start_time=self.time_window.start, samplerate=self.samplerate)
