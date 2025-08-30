from typing import Any, Tuple

import numpy as np
import numpy.typing as npt


def tbavg(f: npt.NDArray[Any], data: npt.NDArray[Any], range: Tuple[float, float] = (
        6.3, 63000)) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    """Calculate the terzband average over the selected frequency range.

    Args:
        f: Corresponding frequency vector.
        data: Data to be averaged.
        range: Lower and upper frequency limits.
    Returns:
        Frequeqncy and data vector for the averaged results.
    """
    tbs_all = np.array([1, 1.25, 1.6, 2.0, 2.5, 3.15, 4, 5, 6.3, 8,
                        10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80,
                        100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
                        1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                        10000, 12500, 16000, 20000, 25000, 31500, 40000, 50000, 63000, 80000,
                        100e3, 125e3, 160e3, 200e3, 250e3, 315e3, 400e3, 500e3, 630e3, 800e3,
                        100e4, 125e4, 160e4, 200e4, 250e4, 315e4, 400e4, 500e4, 630e4, 800e4,
                        10000000])

    # select tbs for range
    itbs = np.where((tbs_all >= range[0]) & (tbs_all <= range[1]))
    tbs = tbs_all[itbs]

    data_avg = []
    f_avg = []
    # tb average
    for tb in tbs:
        lower = tb / (2**(1 / 6))
        upper = tb * (2**(1 / 6))
        ilower = np.argmin(np.abs(f - lower))
        icenter = np.argmin(np.abs(f - tb))
        iupper = np.argmin(np.abs(f - upper))

        data_avg.append(np.mean(data[ilower:iupper]))
        f_avg.append(f[icenter])
    return np.array(
        f_avg, dtype=np.float32), np.array(
        data_avg, dtype=np.float32)


def obavg(f: npt.NDArray[Any], data: npt.NDArray[Any], range: Tuple[float, float] = (
        6.3, 63000)) -> Tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    """Calculate the octaveband average over the selected frequency range.

    Args:
        f: Corresponding frequency vector.
        data: Data to be averaged.
        range: Lower and upper frequency limits.
    Returns:
        Frequeqncy and data vector for the averaged results.
    """

    obs_all = np.array([1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])

    # select tbs for range
    iobs = np.where((obs_all >= range[0]) & (obs_all <= range[1]))
    obs = obs_all[iobs]

    data_avg = []
    f_avg = []
    # tb average
    for ob in obs:
        lower = ob / (2**(1 / 6))
        upper = ob * (2**(1 / 6))
        ilower = np.argmin(np.abs(f - lower))
        icenter = np.argmin(np.abs(f - ob))
        iupper = np.argmin(np.abs(f - upper))

        data_avg.append(np.mean(data[ilower:iupper]))
        f_avg.append(f[icenter])
    return np.array(
        f_avg, dtype=np.float32), np.array(
        data_avg, dtype=np.float32)
