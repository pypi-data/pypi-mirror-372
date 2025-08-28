# This file is part of auditory_models
# Copyright (C) 2025 Max Zimmermann
#
# auditory_models is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# auditory_models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with auditory_models.  If not, see <https://www.gnu.org/licenses/>.


import numpy as np
from numpy import pi, cos, exp, sqrt
from numpy.typing import ArrayLike, NDArray
from scipy.signal import butter, sosfilt
from scipy.special import factorial

from auditory_models.helpers.utils import generate_delta_impulse, hertz_to_erbscale, erb_aud, freq_erb_spaced


class FilterbankBase:
    """
    This class implements a base class for filterbank implementations.
    """
    def __init__(self, sample_rate: float, cf: ArrayLike | None):
        if np.ndim(cf) > 1:
            raise ValueError(f"cf must be one-dimensional, currently: {np.ndim(cf)}")
        self._sample_rate = sample_rate
        if cf is not None:
            self._cf = np.array(cf)
        else:
            self._cf = None
        self._coeffs = None
        self._states = None
        self.n_filters = None

    @property
    def cf(self) -> NDArray:
        """ Indicate that `cf` is a read-only variable. """
        return self._cf

    def _design_filterbank(self) -> None:
        """ Compute the filter coefficients. """
        raise NotImplementedError

    def reset_states(self) -> None:
        """ Reset all filter states to zero. """
        self._states = np.zeros(self._states.shape, dtype=self._states.dtype)

    def process(self, signal: NDArray, save_state: bool = True) -> NDArray:
        """
        Compute the filterbank output of a given signal.
        :param signal: Input signal, shape may be either 1-dim or 2-dim (n_filters, signal_length).
        :param save_state: Indicating if state should be memorized.
        :return: Output signal with shape (n_filters, signal_length)
        """
        if signal.ndim == 1:
            signal = np.repeat(signal.reshape(1, signal.size), self.n_filters, axis=0)
        elif signal.ndim == 2:
            if signal.shape[0] != self.n_filters:
                raise ValueError(f"Input signal must be of shape (number_of_filters, signal_length). The first "
                                 f"dimension does not match. Is currently {signal.shape[0]}, must be "
                                 f"{self.n_filters}")
        else:
            raise ValueError(f"Signal must have either one or two dimensions. In case of two dimensions, the first "
                             f"must have a length equal to the number of filters ({self.n_filters}).")
        if save_state:
            for i, sos_coeff in enumerate(self._coeffs):
                signal[i, :], self._states[i, :, :] = sosfilt(sos_coeff, signal[i, :], zi=self._states[i, :, :])
        else:
            for i, sos_coeff in enumerate(self._coeffs):
                signal[i, :], _ = sosfilt(sos_coeff, signal[i, :], zi=self._states[i, :, :])
        return signal

    def synthesize(self, bands: NDArray) -> NDArray:
        raise NotImplementedError


class GammatoneFilterbank(FilterbankBase):
    """
    This class implements gammatone filters and a filtering routine.

    Reference:
    [Hohmann2002]
       Hohmann, V., Frequency analysis and synthesis using a Gammatone filterbank,
       Acta Acustica, Vol 88 (2002), 433--442
    """
    def __init__(self, sample_rate: float = 44100,
                 order: int = 4,
                 normfreq: float = 1000.0,
                 freq_range: tuple[float, float] | None = None,
                 band_range: tuple[int, int] = (-12, 12),
                 density: float = 1.0,
                 cf: ArrayLike | None = None,
                 bandwidths: ArrayLike | None = None,
                 bandwidth_factor: float = 1.0, attenuation_half_bandwidth_db: float = -3,
                 desired_delay_sec: float = 0.02):
        """
        Init method
        :param sample_rate: sample rate of filterbank in Hz
        :param order: order of filters
        :param normfreq: The reference frequency for `startband` and `endband`
        :param freq_range: two values of the lowest and highest possible center-frequency in Hz, overrides
            `band_range`, first value must be lower than `norm_freq`, second value must be higher than `norm_freq`
        :param band_range: two values defining the number of filters above and below the `normfreq`, if freq_range is
            given, this value will be overridden!
        :param density: ERB density of 1 would be `erb_aud`
        :param cf: Sequence of center-frequencies in Hz, overrides automatic computation via `normfreq`, `freq_range`,
            `band_range`, and `density`
        :param bandwidths: array of bandwidths of filters, size must be equal to number of filters,
            if None given it will default to the ERB of the respective center-frequencies
        :param bandwidth_factor: if bandwidths is not specified, they will be computed via the erb_aud() of each
            center-frequency multiplied by this parameter
        :param attenuation_half_bandwidth_db: attenuation of the filters at half bandwidth in dB
        :param desired_delay_sec:
        """
        super().__init__(sample_rate, cf)
        self._order = order
        if freq_range is None:
            if len(band_range) != 2:
                raise ValueError(f"`band_range` must have a size of 2, currently: {len(band_range)}")
            startband = band_range[0]
            endband = band_range[1]
        else:
            if len(freq_range) != 2:
                raise ValueError(f"`freq_range` must have a size of 2, currently: {len(freq_range)}")
            if freq_range[0] >= normfreq or freq_range[1] <= normfreq:
                raise ValueError("`freq_range` values must be lower/higher than `norm_freq`! Currently `freq_range` = "
                                 f"{freq_range}, `norm_freq` = {normfreq}")
            startband = round(np.fix(hertz_to_erbscale(freq_range[0]) - hertz_to_erbscale(normfreq)))
            endband = round(np.ceil(hertz_to_erbscale(freq_range[1]) - hertz_to_erbscale(normfreq)))

        if self._cf is None:
            self._cf = freq_erb_spaced(startband, endband, normfreq, density)
        else:
            self._cf = np.array(cf, dtype=np.float64)
        self.n_filters = self._cf.size
        self._bandwidths = bandwidths
        self._use_erb = False
        if self._bandwidths is None:
            self._use_erb = True
            self._bandwidths = bandwidth_factor * erb_aud(self._cf)
        self._attenuation_half_bandwidth_db = attenuation_half_bandwidth_db
        self._states = np.zeros((self.n_filters, self._order, 2), dtype=np.complex128)
        self._design_filterbank()

        self._desired_delay_samples = int(self._sample_rate * desired_delay_sec)
        self._max_indices, self._slopes = self.estimate_max_indices_and_slopes()
        self._delay_samples = self._desired_delay_samples - self._max_indices
        self._delay_memory = np.zeros((len(self._cf), np.max(self._delay_samples)))
        self._phase_factors = np.abs(self._slopes) * 1j / self._slopes
        self._gains = np.ones(len(self._cf))

    def _design_filterbank(self) -> None:
        """ Returns filter coefficients of a gammatone filter [Hohmann2002]. """
        if self._use_erb:
            # [Hohmann2002] eq. (14)
            a_gamma = (pi * factorial(2 * self._order - 2) *
                       2 ** -(2 * self._order - 2) /
                       factorial(self._order - 1) ** 2)
            b = self._bandwidths / a_gamma
            lambda_ = np.exp(-2 * pi * b / self._sample_rate)
        else:
            # [Hohmann2002] eq. (12)
            phi = pi * self._bandwidths / self._sample_rate
            alpha = 10 ** (0.1 * self._attenuation_half_bandwidth_db / self._order)
            p = (-2 + 2 * alpha * cos(phi)) / (1 - alpha)
            lambda_ = -p / 2 - sqrt(p * p / 4 - 1)
        beta = 2 * pi * self._cf / self._sample_rate
        coef = lambda_ * exp(1j * beta)
        factor = 2 * (1 - np.abs(coef)) ** self._order
        self._coeffs = np.zeros((self.n_filters, self._order, 6), dtype=np.complex128)
        for idx, c in enumerate(-coef):
            self._coeffs[idx, :, :] = np.repeat([[1., 0., 0., 1., c, 0.]], self._order, axis=0)
        self._coeffs[:, 0, 0] = factor

    # def synthesize(self, bands: NDArray) -> NDArray:
    #     return np.array(list(self.delay([b*g for b, g in zip(bands, self._gains)]))).sum(axis=0)

    def delay(self, bands):
        for i, band in enumerate(bands):
            if self._delay_samples[i] == 0:
                yield np.real(band) * self._phase_factors[i]
            else:
                yield np.concatenate((self._delay_memory[i, :self._delay_samples[i]],
                                      np.real(band[:-self._delay_samples[i]])), axis=0)
                self._delay_memory[i, :self._delay_samples[i]] = np.real(band[-self._delay_samples[i]:])

    def estimate_max_indices_and_slopes(self):
        sig = generate_delta_impulse(self._desired_delay_samples, dtype=np.complex128)
        bands = self.process(sig, save_state=False)
        ibandmax = np.argmax(np.abs(bands[:self._desired_delay_samples]), axis=-1)
        slopes = [b[i+1] - b[i-1] for (b, i) in zip(bands, ibandmax)]
        return np.array(ibandmax), np.array(slopes)


class BandpassFilterbank(FilterbankBase):
    """
    Implements a bandpass filterbank from given center-frequencies with octave width for each band. There is also the
    option to add a lowpass filter at 1Hz to include the DC-component.
    """
    def __init__(self, cf: ArrayLike, sample_rate: float, order: int = 2, dc_lowpass: bool = True):
        """
        Init method
        :param cf: Array of center-frequencies for filters in Hz
        :param sample_rate: Sampling rate of filterbank in Hz
        :param order: Order of bandpass filters
        :param dc_lowpass: Indicates if an additional band for the DC via a lowpass at 1 Hz should be computed
        """
        super().__init__(sample_rate, cf)
        self._cf = np.array(cf)
        self._sample_rate = sample_rate
        if order % 2 != 0:
            raise ValueError(f"order must be an even integer, currently: {order}")
        self._order = order
        self._dc_lp = dc_lowpass
        self.n_filters = self._cf.size + self._dc_lp
        self._states = np.zeros((self.n_filters, round(self._order / 2), 2))
        self._coeffs = np.zeros((self.n_filters, round(self._order / 2), 6))
        self._design_filterbank()

    def _design_filterbank(self) -> None:
        """ Compute the filter coefficients """
        if self._dc_lp:
            self._coeffs[0, :, :] = butter(self._order, 1, output="sos", fs=self._sample_rate)
        fhigh = self._cf / 2 + np.sqrt(np.square(self._cf / 2) + np.square(self._cf))
        flow = np.square(self._cf) / fhigh
        for idx, (low, high) in enumerate(zip(flow, fhigh)):
            self._coeffs[idx + self._dc_lp, :, :] = butter(round(self._order / 2), [low, high], btype="bandpass",
                                                           output="sos", fs=self._sample_rate)
        if self._dc_lp:
            self._cf = np.concatenate(([1], self._cf))
