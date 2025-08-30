from typing import List, Tuple

import numpy as np
from braket.timings.time_series import TimeSeries


def rabi_pulse(
    rabi_pulse_area: float, omega_max: float, omega_slew_rate_max: float
) -> Tuple[List[float], List[float]]:
    """Get a time series for Rabi frequency with specified Rabi phase, maximum amplitude
    and maximum slew rate

        Args:
            rabi_pulse_area (float): Total area under the Rabi frequency time series
            omega_max (float): The maximum amplitude
            omega_slew_rate_max (float): The maximum slew rate

        Returns:
            Tuple[List[float], List[float]]: A tuple containing the time points and
            values
                of the time series for the time dependent Rabi frequency

        Notes: By Rabi phase, it means the integral of the amplitude of a time-dependent
            Rabi frequency, int_0^TOmega(t)dt, where T is the duration.
    """

    phase_threshold = omega_max**2 / omega_slew_rate_max
    if rabi_pulse_area <= phase_threshold:
        t_ramp = np.sqrt(rabi_pulse_area / omega_slew_rate_max)
        t_plateau = 0
    else:
        t_ramp = omega_max / omega_slew_rate_max
        t_plateau = (rabi_pulse_area / omega_max) - t_ramp
    t_pules = 2 * t_ramp + t_plateau
    time_points = [0, t_ramp, t_ramp + t_plateau, t_pules]
    amplitude_values = [
        0,
        t_ramp * omega_slew_rate_max,
        t_ramp * omega_slew_rate_max,
        0,
    ]

    return time_points, amplitude_values


def constant_time_series(
    other_time_series: TimeSeries, constant: float = 0.0
) -> TimeSeries:
    """Obtain a constant time series with the same time points as the given time series

    Args:
        other_time_series (TimeSeries): The given time series

    Returns:
        TimeSeries: A constant time series with the same time points as the given time
        series
    """
    ts = TimeSeries()
    for t in other_time_series.times():
        ts.put(t, constant)
    return ts
