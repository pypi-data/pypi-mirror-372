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
from numpy.typing import NDArray
from scipy.signal import butter, fftconvolve, firwin, sosfilt
from warnings import warn

from auditory_models.helpers.utils import thirdoct, iso389_7_thresholds
from auditory_models.helpers.filterbank import BandpassFilterbank, GammatoneFilterbank


class GPSMq:
    def __init__(self, binaural: bool = True, aud_filt_range: tuple[int, int] = (7, 24),
                 mod_filt_range: tuple[int, int] = (1, 7), corr_thres: float = 0.8, decimation_factor: int = 8,
                 limits: tuple[float, float] = (-65, -100), threshold_scaling: float = 1e-10):
        """
        Init method
        :param binaural: Determines if binaural processing should be used, if True the input of process() must have
            shapes of (2, signal_length).
        :param aud_filt_range: The range of Gammatone-Filterbank center-frequencies as indices of a vector of
            frequencies in third-octave distances, starting with 63Hz and ending with 16000Hz as defined by
            IEC 61260-1:2014.
        :param mod_filt_range: The range of Modulation-Filterbank center-frequencies as exponents of 2. The default of
            (1, 7) would result in [2, 4, 8, 16, 32, 64] Hz as center-frequencies.
        :param corr_thres: Scaling value as parameter for the sigmoid function that will process the correlation matrix.
        :param decimation_factor: Factor of decimation of the lowpass filtered Hilbert envelope signals.
        :param limits: Limits in dB for the multi resolution based power processing
        :param threshold_scaling: Scaling factor for the squared hearing threshold. Default value is chosen with the
            assumption that 0 dB RMS equals 100 dB SPL.
        """
        self._sample_rate = 0
        self._binaural = binaural
        self._n_chan = self._binaural + 1
        self._aud_filt_range = aud_filt_range
        self._mod_filt_range = mod_filt_range
        self._corr_thres = corr_thres
        self._decimation_factor = decimation_factor
        self._limits = limits
        self._threshold_scaling = threshold_scaling
        self._slope = 1 / (self._limits[0] - self._limits[1])
        self._env_lp_sos = None
        self._sig_len = 0
        self._sig_len_dec = 0
        self._env_pow_lim = 10 ** -2.7

        self._decimation_order = 20 * self._decimation_factor
        self.decimation_filter = None
        self._sample_rate_dec = None
        self.gtfb = None
        self.mf_cf = np.pow(2, np.arange(*self._mod_filt_range))
        self.mfb = None
        self._iso_thres = None
        self._upper_lim = None

    def _recompute_properties(self) -> None:
        """
        When process receives a sample_rate value that is different from the previous one, recompute all dependent
        properties.
        :return: None
        """
        self._env_lp_sos = butter(1, 150, fs=self._sample_rate, output="sos")
        # cutoff frequency for decimation filter is computed with the decimation factor and an extra factor for the
        # filter to be effective at the new nyquist frequency
        cutoff = self._sample_rate / (2 * self._decimation_factor) * (5 / 6)
        self.decimation_filter = firwin(self._decimation_order + 1, cutoff, fs=self._sample_rate, window=("kaiser", 5.),
                                        pass_zero=True)
        self._sample_rate_dec = self._sample_rate / self._decimation_factor
        gt_cf = thirdoct(self._sample_rate, nfft=1024, min_freq=63, max_freq=16000)[1]
        self.gtfb = GammatoneFilterbank(self._sample_rate, cf=gt_cf[self._aud_filt_range[0]:self._aud_filt_range[1]])
        self.mfb = BandpassFilterbank(self.mf_cf, self._sample_rate_dec)
        self._iso_thres = 10 ** (iso389_7_thresholds(self.gtfb.cf) / 10)
        self._upper_lim = self._iso_thres * 10 ** (self._limits[0] / 10)
        self._iso_thres *= self._threshold_scaling

    def process(self, reference: np.ndarray, degraded: np.ndarray, sample_rate: float) -> dict:
        """
        Process method to calculate the perceptual proximity of a degraded signal to a reference signal.
        :param reference: Reference signal, if binaural it must have shape (2, signal_length)
        :param degraded: Degraded signal, if binaural it must have shape (2, signal_length)
        :param sample_rate: sample rate of both input signals in Hz
        :return: dictionary containing measurement data
            "snr_dc": SNR for the DC part
            "snr_ac": SNR for the modulation part
            "snr_ac_fix": SNR for the modulation part including weighting to reduce effects of IPDs/ITDs
            "opm": combined snr_dc and snr_ac into perceptual measure (MUSHRA scale)
            "opm_fix": combined snr_dc and snr_ac_fix into perceptual measure (MUSHRA scale)
        """
        reference = np.squeeze(reference)
        degraded = np.squeeze(degraded)
        if self._binaural:
            if reference.ndim != 2:
                raise ValueError(f"reference must have two dimensions, currently: {reference.ndim}")
            if reference.shape[0] != 2:
                raise ValueError(f"reference must have a size of 2 in first dimension, currently shape is: "
                                 f"{reference.shape}")
            if degraded.ndim != 2:
                raise ValueError(f"degraded must have two dimensions, currently: {degraded.ndim}")
            if degraded.shape[0] != 2:
                raise ValueError(f"degraded must have a size of 2 in first dimension, currently shape is: "
                                 f"{degraded.shape}")
            if reference.shape[1] != degraded.shape[1]:
                raise ValueError(f"reference and degraded must have same signal lengths, currently "
                                 f"{reference.shape[1]} and {degraded.shape[1]}.")
        else:
            if reference.ndim != 1:
                raise ValueError(f"reference must have one dimension, currently: {reference.ndim}")
            if degraded.ndim != 1:
                raise ValueError(f"degraded must have one dimension, currently: {degraded.ndim}")
            if reference.size != degraded.size:
                raise ValueError(f"reference and degraded must have same signal lengths, currently "
                                 f"{reference.size} and {degraded.size}.")
            reference = reference[np.newaxis, :]
            degraded = degraded[np.newaxis, :]

        if self._sig_len != reference.shape[reference.ndim - 1]:
            self._sig_len = reference.shape[reference.ndim - 1]
            self._sig_len_dec = round(np.ceil(self._sig_len / self._decimation_factor))

        if sample_rate != self._sample_rate:
            self._sample_rate = sample_rate
            self._recompute_properties()

        if self._sample_rate / 2 < self.gtfb.cf[-1]:
            warn(f"Given sample rate ({self._sample_rate}) does not fit Nyquist Theorem with the center-frequency of "
                 f"the highest band ({self.gtfb.cf[-1]}).")

        # Auditory filtering via Gammatone Filterbank and Hilbert Envelope
        ref_hilbert = np.zeros((self._n_chan, self.gtfb.cf.size, self._sig_len))
        dgr_hilbert = np.zeros((self._n_chan, self.gtfb.cf.size, self._sig_len))
        for ch in range(self._n_chan):
            ref_hilbert[ch, :, :] = np.abs(
                self.gtfb.process(reference[ch, :].astype(np.complex128), save_state=False)) / np.sqrt(2)
            dgr_hilbert[ch, :, :] = np.abs(
                self.gtfb.process(degraded[ch, :].astype(np.complex128), save_state=False)) / np.sqrt(2)

        # ILD cancellation
        if self._binaural:
            ref_rms = np.sqrt(np.mean(np.square(ref_hilbert), axis=2))
            dgr_rms = np.sqrt(np.mean(np.square(dgr_hilbert), axis=2))
            ref_lr_diff = np.squeeze(np.abs(np.diff(ref_rms, axis=0)))
            dgr_lr_diff = np.squeeze(np.abs(np.diff(dgr_rms, axis=0)))
            ref_dgr_l_diff = ref_rms[0, :] - dgr_rms[0, :]
            ref_dgr_r_diff = ref_rms[1, :] - dgr_rms[1, :]
            for band in range(self.gtfb.cf.size):
                if np.sign(ref_dgr_l_diff[band]) * np.sign(ref_dgr_r_diff[band]) == -1:
                    if ref_dgr_l_diff[band] > 0:
                        dgr_hilbert[0, band, :] *= ref_rms[0, band] / dgr_rms[0, band]
                    elif ref_dgr_l_diff[band] < 0:
                        ref_hilbert[0, band, :] *= dgr_rms[0, band] / ref_rms[0, band]

                    if ref_dgr_r_diff[band] > 0:
                        dgr_hilbert[1, band, :] *= ref_rms[1, band] / dgr_rms[1, band]
                    elif ref_dgr_r_diff[band] < 0:
                        ref_hilbert[1, band, :] *= dgr_rms[1, band] / ref_rms[1, band]
                else:
                    if np.abs(ref_dgr_l_diff[band]) > np.abs(ref_dgr_r_diff[band]):
                        if ref_lr_diff[band] > dgr_lr_diff[band]:
                            ref_hilbert[0, band, :] *= ref_rms[1, band] / ref_rms[0, band]
                        elif ref_lr_diff[band] < dgr_lr_diff[band]:
                            dgr_hilbert[0, band, :] *= dgr_rms[1, band] / dgr_rms[0, band]
                    elif np.abs(ref_dgr_l_diff[band]) < np.abs(ref_dgr_r_diff[band]):
                        if ref_lr_diff[band] > dgr_lr_diff[band]:
                            ref_hilbert[1, band, :] *= ref_rms[0, band] / ref_rms[1, band]
                        elif ref_lr_diff[band] < dgr_lr_diff[band]:
                            dgr_hilbert[1, band, :] *= dgr_rms[0, band] / dgr_rms[1, band]

        # apply Lowpass-Filter at 150Hz
        ref_lp = sosfilt(self._env_lp_sos, ref_hilbert, axis=2)
        dgr_lp = sosfilt(self._env_lp_sos, dgr_hilbert, axis=2)

        # decimate lowpass filtered signal
        ref_lp_dec = fftconvolve(ref_lp, self.decimation_filter[np.newaxis, np.newaxis, :],
                                 mode="same", axes=-1)[:, :, ::self._decimation_factor]
        dgr_lp_dec = fftconvolve(dgr_lp, self.decimation_filter[np.newaxis, np.newaxis, :],
                                 mode="same", axes=-1)[:, :, ::self._decimation_factor]

        # apply modulation filterbank
        ref_mod = np.zeros((self._n_chan, self.gtfb.cf.size, self.mfb.n_filters, self._sig_len_dec))
        dgr_mod = np.zeros((self._n_chan, self.gtfb.cf.size, self.mfb.n_filters, self._sig_len_dec))
        for ch in range(self._n_chan):
            for gt in range(self.gtfb.cf.size):
                ref_mod[ch, gt, :, :] = self.mfb.process(ref_lp_dec[ch, gt, :], save_state=False)
                dgr_mod[ch, gt, :, :] = self.mfb.process(dgr_lp_dec[ch, gt, :], save_state=False)

        # calculate multi-resolution-based envelope power and short-time power
        ref_epsm, ref_psm, ref_dc2mod = self.multi_resolution_based_power(ref_lp_dec, ref_mod)
        dgr_epsm, dgr_psm, dgr_dc2mod = self.multi_resolution_based_power(dgr_lp_dec, dgr_mod)

        # calculate correlation matrix
        corr_mat = np.ones((self._n_chan, self.gtfb.cf.size, self.mfb.n_filters - 1))
        for ch in range(self._n_chan):
            for aud_idx in range(self.gtfb.cf.size):
                for mf_idx in range(1, self.mfb.n_filters):
                    corr_mat[ch, aud_idx, mf_idx - 1] = np.corrcoef(
                        ref_mod[ch, aud_idx, mf_idx, round(self._sample_rate_dec / 4) - 1::],
                        dgr_mod[ch, aud_idx, mf_idx, round(self._sample_rate_dec / 4) - 1::])[0, 1]

        # psm above iso thresholds
        clipper = np.logical_and(ref_psm > self._iso_thres[np.newaxis, :, np.newaxis, np.newaxis],
                                 dgr_psm > self._iso_thres[np.newaxis, :, np.newaxis, np.newaxis])

        # calculate SNR increment and decrement
        snr_inc_epsm = np.fmax(np.fmin(dgr_epsm / (ref_epsm + 1e-30) - 1, 20), 0.) * dgr_dc2mod
        snr_inc_epsm[np.logical_not(clipper)] = 0.
        snr_inc_psm = np.fmax(np.fmin(dgr_psm / (ref_psm + 1e-30) - 1, 20), 0.)

        snr_dec_epsm = np.fmax(np.fmin(ref_epsm / (dgr_epsm + 1e-30) - 1, 20), 0.) * ref_dc2mod
        snr_dec_epsm[np.logical_not(clipper)] = 0.
        snr_dec_psm = np.fmax(np.fmin(ref_psm / (dgr_psm + 1e-30) - 1, 20), 0.)

        snr_inc_mod = np.zeros((self._n_chan, self.gtfb.cf.size, self.mfb.n_filters))
        snr_inc_stint = np.zeros(snr_inc_mod.shape)
        snr_dec_mod = np.zeros(snr_inc_mod.shape)
        snr_dec_stint = np.zeros(snr_inc_mod.shape)

        for mf_idx in range(self.mfb.n_filters):
            n_windows = round(np.ceil(self._sig_len_dec / np.floor(self._sample_rate_dec / self.mfb.cf[mf_idx])))
            snr_inc_mod[:, :, mf_idx] = np.mean(snr_inc_epsm[:, :, mf_idx, 0:n_windows], axis=-1)
            snr_inc_stint[:, :, mf_idx] = np.mean(snr_inc_psm[:, :, mf_idx, 0:n_windows], axis=-1)
            snr_dec_mod[:, :, mf_idx] = np.mean(snr_dec_epsm[:, :, mf_idx, 0:n_windows], axis=-1)
            snr_dec_stint[:, :, mf_idx] = np.mean(snr_dec_psm[:, :, mf_idx, 0:n_windows], axis=-1)
        snr_inc_mod = np.fmax(snr_inc_mod, 0.)
        snr_inc_stint = np.fmax(snr_inc_stint, 0.)
        snr_dec_mod = np.fmax(snr_dec_mod, 0.)
        snr_dec_stint = np.fmax(snr_dec_stint, 0.)
        valid_mod_freq = self.gtfb.cf[:, np.newaxis] > 4 * self.mfb.cf[np.newaxis, :]
        snr_inc_mod *= valid_mod_freq
        snr_dec_mod *= valid_mod_freq

        # combine SNR increment and decrement
        snr_dc = np.mean(np.sqrt(np.sum(np.square((snr_inc_stint[:, :, 2] + snr_dec_stint[:, :, 2]) / 2), axis=-1)))
        inc_dec_mean = (snr_inc_mod[:, :, 1::] + 10 ** (-0.7) * snr_dec_mod[:, :, 1::]) / 2
        snr_ac = np.mean(np.sqrt(np.sum(np.sum(np.square(inc_dec_mean), axis=-1), axis=-1)))

        # include weighting via correlation matrix to make model less sensitive to IPDs/ITDs
        sigmoid_corr = 1 / (1 + np.exp(-50 * (corr_mat - self._corr_thres)))
        snr_ac_fix = np.mean(np.sqrt(np.sum(np.sum(np.square(sigmoid_corr * inc_dec_mean), axis=-1), axis=-1)))

        # transform to perceptual measure (MUSHRA scale)
        opm = -4.08695250298565 * 10 * np.log10(snr_dc + snr_ac + 1e-30) + 75.6467755339438
        opm_fix = -4.15742483856597 * 10 * np.log10(snr_dc + snr_ac_fix + 1e-30) + 74.7791007678067

        return {"snr_dc": snr_dc, "snr_ac": snr_ac, "snr_ac_fix": snr_ac_fix, "opm": opm, "opm_fix": opm_fix}

    def lowpass_filterbank(self, signal: NDArray) -> NDArray:
        """
        Compute output of a lowpass filterbank using moving averages with variable window sizes depending on the
        modulation frequency.
        :param signal: Input signal, must be one-dimensional
        :return: two-dimensional matrix with filterbank output with shape (number_of_mod_filters, signal_length)
        """
        out = np.zeros((self.mfb.n_filters, self._sig_len_dec))
        window = np.ones(round(np.ceil(2 * self._sample_rate_dec / np.min(self.mfb.cf))))
        crit_mod_freq = 8.
        idx_crit = 0
        repeat = False
        for idx, mod_freq in enumerate(self.mfb.cf):
            if mod_freq <= crit_mod_freq:
                win_width = round(1.5 * self._sample_rate_dec / mod_freq)
                out[idx, :] = np.convolve(window[0:win_width] / win_width, signal, mode="full")[0:signal.size]
            elif not repeat:
                win_width = round(self._sample_rate_dec / 8)
                out[idx, :] = np.convolve(window[0:win_width] / win_width, signal, mode="full")[0:signal.size]
                idx_crit = idx
                repeat = True
            elif repeat:
                out[idx, :] = out[idx_crit, :]
        return out

    def multi_resolution_based_power(self, envelope: NDArray, modulation: NDArray) -> tuple[NDArray, NDArray, NDArray]:
        """
        Calculate the multi resolution based power from an envelope signal and a modulation signal.
        :param envelope: Lowpass filtered envelope signal for different frequency bands, must have shape
            (channels, auditory bands, signal_length)
        :param modulation: Modulation filtered signal for different frequency bands, must have shape
            (channels, auditory bands, modulation bands, signal_length)
        :return: Three arrays containing the envelope power spectrum model (EPSM), power spectrum model (PSM), and a
            correction matrix (dc2mod). Each of these arrays has shape
            (channels, auditory bands, modulation bands, new_length)
        """
        epsm = np.zeros((self._n_chan, self.gtfb.cf.size, self.mfb.n_filters,
                         round(np.ceil(self._sig_len_dec / np.floor(self._sample_rate_dec / self.mfb.cf[-1])))))
        psm = np.zeros(epsm.shape)
        dc2mod = np.ones(epsm.shape)
        modulation *= np.sqrt(2)
        for ch in range(self._n_chan):
            for aud_idx in range(self.gtfb.cf.size):
                tmp_pow = np.max((np.square(np.mean(envelope[ch, aud_idx, :])), self._iso_thres[aud_idx]))
                lpfb = self.lowpass_filterbank(envelope[ch, aud_idx, :])
                for mf_idx in range(self.mfb.n_filters):
                    samples_per_mf = round(np.floor(self._sample_rate_dec / self.mfb.cf[mf_idx]))
                    n_windows = round(np.ceil(self._sig_len_dec / samples_per_mf))
                    if tmp_pow <= self._iso_thres[aud_idx]:
                        epsm[ch, aud_idx, mf_idx, 0:n_windows] = self._env_pow_lim
                        psm[ch, aud_idx, mf_idx, 0:n_windows] = self._iso_thres[aud_idx]
                        continue
                    pow_dc_seg = lpfb[mf_idx, samples_per_mf-1::samples_per_mf] ** 2
                    if n_windows * samples_per_mf != self._sig_len_dec:
                        pow_dc_seg = np.concatenate((pow_dc_seg, [lpfb[mf_idx, -1] ** 2]))
                    for win_idx in range(n_windows):
                        ac = modulation[ch, aud_idx, mf_idx, win_idx * samples_per_mf:(win_idx + 1) * samples_per_mf]
                        if mf_idx == 0:
                            pow_ac = np.var(ac)
                        else:
                            pow_ac = np.mean(ac ** 2)
                        if pow_dc_seg[win_idx] <= self._iso_thres[aud_idx]:
                            epsm[ch, aud_idx, mf_idx, win_idx] = self._env_pow_lim
                        else:
                            epsm[ch, aud_idx, mf_idx, win_idx] = np.max((pow_ac / pow_dc_seg[win_idx],
                                                                         self._env_pow_lim))
                        psm[ch, aud_idx, mf_idx, win_idx] = np.max((pow_dc_seg[win_idx], self._iso_thres[aud_idx]))
                        if pow_dc_seg[win_idx] > self._upper_lim[aud_idx]:
                            dc2mod[ch, aud_idx, mf_idx, win_idx] = 1.
                        else:
                            dc2mod[ch, aud_idx, mf_idx, win_idx] = np.max((
                                self._slope * (10 * np.log10(pow_dc_seg[win_idx] / self._iso_thres[aud_idx] + 1e-30)),
                                0.))
        return epsm, psm, dc2mod

    def export_config(self) -> dict:
        """
        Export the parameters as dictionary.
        :return: Dictionary containing parameters
        """
        out_config = dict(
            binaural=self._binaural,
            aud_filt_range=self._aud_filt_range,
            mod_filt_range=self._mod_filt_range,
            corr_thres=self._corr_thres,
            decimation_factor=self._decimation_factor,
            limits=self._limits,
            threshold_scaling=self._threshold_scaling
        )
        return out_config
