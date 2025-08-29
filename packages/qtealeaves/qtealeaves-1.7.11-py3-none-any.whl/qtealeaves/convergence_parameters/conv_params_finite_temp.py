# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Convergence parameters for systems at finite temperature defining the grid
for imaginary time evolution.
"""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

import numpy as np

from .conv_params import TNConvergenceParameters

__all__ = ["TNConvergenceParametersFiniteT"]


class TNConvergenceParametersFiniteT(TNConvergenceParameters):
    """
    Convergence parameters for finite temperature.
    Based on the input temperature grid, the time grid for
    imaginary time evolution is created. The largest value of
    time step is limited with the input `dt_max`.

    Parameters
    ----------
    t_grid : list or np.ndarray
        Temperature grid, we want to take measurements for each
        point in the grid. The temperature grid must be sorted in
        descending order.
    statics_method : int, optional
        Only imaginary time evolution methods are enabled, i.e.,
        3 (two-tensor), 4 (single-tensor link-expansion), or
        5 (single-tensor).
        Default to 4 (single-tensor link-expansion)
    dt_max : float, optional
        Maximal time step for imaginary time evolution.
        Default is 0.1.
    measure_obs_every_n_iter : int, optional
        The measurements are done every `measure_obs_every_n_iter`
        iterations. The target tempertures will fall on multiples of
        `measure_obs_every_n_iter`
        Default is 20.
    k_b : float, optional
        Value for Boltzmann constant.
    **kwargs : other :py:class:`TNConvergenceParameters` parameters

    Attributes
    ----------
    self.sim_params['imag_evo_dt'] : np.ndarray
        Time step grid.
    self.measure_obs_every_n_iter : int
        See Parameters above.
    self.n_grid : np.ndarray of int
        The number of iterations/`measure_obs_every_n_iter`
        needed to reach each of the temperatures from
        `t_grid`, starting from the infinite temperature.
    """

    def __init__(
        self,
        t_grid,
        statics_method=4,
        dt_max=0.1,
        measure_obs_every_n_iter=20,
        k_b=1,
        **kwargs,
    ):
        if np.any(np.array(t_grid[:-1]) < np.array(t_grid[1:])):
            raise ValueError(
                "The input temperature grid must be sorted in descending order."
            )

        if isinstance(statics_method, int):
            if statics_method not in [3, 4, 5]:
                raise ValueError(
                    f"Statics method must be imaginary time, but {statics_method}."
                )
        else:
            if any((method not in [3, 4, 5]) for method in statics_method):
                raise ValueError(
                    f"Statics method must be imaginary time, but {statics_method}."
                )

        self.k_b = k_b

        # initialize the array n_grid which represents the
        # number of iterations/measure_obs_every_n_iter
        # needed to reach each of the temperatures from t_grid
        n_grid = np.zeros(len(t_grid), dtype=int)

        # initialize dt_grid for time steps in imaginary time evolution
        # measurments fall on every measure_obs_every_n_iter-th step
        dt_grid = np.zeros(measure_obs_every_n_iter * len(t_grid))

        # calculate time step dt_nn such that the next
        # measurement falls on the next target temperature

        # the first temperature in a grid is treated outside
        # the loop
        dt_nn = 1 / (2 * k_b * t_grid[0] * measure_obs_every_n_iter)
        num = 1

        # if this time step is smaller than the given dt_max,
        # accept it and store it in dt_grid
        if dt_nn <= dt_max:
            dt_grid[:measure_obs_every_n_iter] = dt_nn
            start = measure_obs_every_n_iter
            n_step = measure_obs_every_n_iter * dt_nn
            n_grid[0] = 0

        # in case the dt_nn is bigger than dt_max,
        # we add another measure_obs_every_n_iter iterations
        # to reach the next target temperature, meaning that
        # the target temperature will not fall on the next
        # measurement, but at the one after it
        # we iterate this procedure until we reach dt_nn < dt_max
        else:
            dt_new = dt_nn
            while dt_new > dt_max:
                num += 1
                dt_new = dt_nn / num
            dt_grid = np.pad(dt_grid, (0, (num - 1) * measure_obs_every_n_iter))
            dt_grid[: measure_obs_every_n_iter * num] = dt_new
            start = measure_obs_every_n_iter * num
            # n_step is the cummulated imaginary time passed until
            # the certain measurement
            n_step = measure_obs_every_n_iter * dt_new * num
            n_grid[0] = num - 1
            num = 1

        # the same procedure as above, looped over the entire
        # temperature grid
        for nn in range(1, len(t_grid)):
            dt_nn = 1 / measure_obs_every_n_iter * (1 / (2 * k_b * t_grid[nn]) - n_step)
            if dt_nn <= dt_max:
                dt_grid[start : start + measure_obs_every_n_iter] = dt_nn
                start += measure_obs_every_n_iter
                n_step += measure_obs_every_n_iter * dt_nn
                n_grid[nn] += n_grid[nn - 1] + 1

            else:
                dt_new = dt_nn
                while dt_new > dt_max:
                    num += 1
                    dt_new = dt_nn / num
                dt_grid = np.pad(
                    dt_grid,
                    (0, (num - 1) * measure_obs_every_n_iter),
                    constant_values=0,
                )
                dt_grid[start : start + measure_obs_every_n_iter * num] = dt_new
                start += measure_obs_every_n_iter * num
                n_step += measure_obs_every_n_iter * dt_new * num
                n_grid[nn] += n_grid[nn - 1] + num
                num = 1

        self.n_grid = n_grid
        max_iter = int((self.n_grid[-1] + 1) * measure_obs_every_n_iter)
        super().__init__(
            measure_obs_every_n_iter=measure_obs_every_n_iter,
            statics_method=statics_method,
            imag_evo_dt=dt_grid,
            max_iter=max_iter,
            **kwargs,
        )

    @property
    def temperature(self):
        """
        Returns the grid of temperatures at which the measurements
        are made.
        To check if the grid corresponds to the
        input temperature grid, use self.temperature[self.n_grid].
        """
        dt_grid = self.sim_params["imag_evo_dt"]

        temp = np.zeros(int(len(dt_grid) / self.measure_obs_every_n_iter))
        n_step = 0

        # the loop goes through all the measured points and extracts the
        # temperature at each of them
        for ii in range(0, int(len(dt_grid) / self.measure_obs_every_n_iter)):
            temp[ii] = 1 / (
                2
                * self.k_b
                * (
                    dt_grid[self.measure_obs_every_n_iter * ii]
                    * self.measure_obs_every_n_iter
                    + n_step
                )
            )
            n_step += (
                self.measure_obs_every_n_iter
                * dt_grid[self.measure_obs_every_n_iter * ii]
            )

        return temp
