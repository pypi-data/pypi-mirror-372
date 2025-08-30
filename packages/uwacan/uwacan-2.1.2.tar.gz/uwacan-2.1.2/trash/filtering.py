import numpy as np
import scipy.signal
from . import timestamps
from . import signals


class NthOctavebandFilterBank:
    def __init__(self, frequency_range, bands_per_octave=3, filter_order=8):
        self.frequency_range = frequency_range
        self.bands_per_octave = bands_per_octave
        self.filter_order = filter_order

    def __call__(self, signal):
        if isinstance(signal, signals.Spectrogram):
            powers = self.power_filters(signal.frequencies).dot(signal.signal) / signal.frequencies[1]
            return signals.Signal(
                signal=powers,
                samplerate=signal.times.samplerate,
                start_time=signal.times.start_time,
            )
        else:
            raise TypeError(f'Cannot filter data of input type {type(signal)}')

    @property
    def center_frequencies(self):
        lowest_band, highest_band = self.frequency_range
        lowest_band_index = np.round(self.bands_per_octave * np.log2(lowest_band / 1e3))
        highest_band_index = np.round(self.bands_per_octave * np.log2(highest_band / 1e3))
        octaves = np.arange(lowest_band_index, highest_band_index + 1) / self.bands_per_octave
        return 1e3 * 2 ** octaves

    def power_filters(self, frequencies):
        centers = self.center_frequencies[:, None]
        bandwidths = centers * (2**(0.5 / self.bands_per_octave) - 2**(-0.5 / self.bands_per_octave))
        filters = 1 / (
            1
            + ((frequencies**2 - centers**2) / (frequencies * bandwidths))
            ** (2 * self.filter_order)
        )
        return filters
