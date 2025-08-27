'''
This module provides classes and functions for lateral buckling calculations and friction factor
distribution fitting for subsea pipelines.

**Features:**

- The `LBDistributions` class implements lognormal distribution fitting for geotechnical friction
  factors, supporting low, best, and high estimates (LE, BE, HE) and multiple fit types.
- Designed for use in pipeline lateral buckling reliability analysis and geotechnical parameter
  estimation.
- All calculations are vectorized using NumPy and leverage SciPy for statistical fitting.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np
from scipy.stats import lognorm
from scipy.optimize import minimize

class LBDistributions: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling calculations, including friction factor distribution fitting.

    Parameters
    ----------
    friction_factor_le : float, optional
        Low estimate (LE) friction factor, representing the 5th percentile.
    friction_factor_be : float, optional
        Best estimate (BE) friction factor, representing the 50th percentile.
    friction_factor_he : float, optional
        High estimate (HE) friction factor, representing the 95th percentile.
    friction_factor_fit_type : str, optional
        Type of fit to perform: 'LE_BE_HE', 'LE_BE', or 'BE_HE'.
    """
    def __init__(
            self,
            *,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Initialize with geotechnical friction factor estimates and fit type.
        """
        self.friction_factor_le = np.asarray(friction_factor_le, dtype = float)
        self.friction_factor_be = np.asarray(friction_factor_be, dtype = float)
        self.friction_factor_he = np.asarray(friction_factor_he, dtype = float)
        self.friction_factor_fit_type = np.asarray(friction_factor_fit_type, dtype = object)

    def friction_distribution(self):
        """
        Compute the parameters of the lognormal friction factor distribution (axial or lateral)
        by minimizing the root mean square error (RMSE) between geotechnical estimates and
        back-calculated friction factors from the lognormal distribution.

        Returns
        -------
        mean_friction : np.ndarray
            Array of mean values of the lognormal friction factor distribution.
        std_friction : np.ndarray
            Array of standard deviation values of the lognormal friction factor distribution.
        location_param : np.ndarray
            Array of location parameters of the lognormal friction factor distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal friction factor distribution.
        le_fit : np.ndarray
            Array of fitted LE values.
        be_fit : np.ndarray
            Array of fitted BE values.
        he_fit : np.ndarray
            Array of fitted HE values.
        rmse : np.ndarray
            Array of RMSE values for the best fit type.
        Notes
        -----
        The function calculates the parameters of the lognormal friction factor distribution
        based on LE at 5th percentile, BE at 50th percentile, and HE at 95th percentile

        Examples
        --------
        >>> lb = LBDistributions(
        ...     friction_factor_le=[0.5],
        ...     friction_factor_be=[1.0],
        ...     friction_factor_he=[1.5],
        ...     friction_factor_fit_type=['LE_BE_HE']
        ... )
        >>> lb.friction_distribution()
        (array([0.9684083]), array([0.30043236]), array([-0.07804666]), array([0.3031342]), array([0.56177265]), array([0.92492127]), array([1.52282131]), array([0.05765844]))
        """
        # Initialize lists to store results
        mean_friction_list = []
        std_friction_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        rmse_list = []

        # Define the objective function
        def objective(
                params,
                friction_factor_le,
                friction_factor_be,
                friction_factor_he,
                friction_factor_fit_type
            ):
            location_param, scale_param = params
            if friction_factor_fit_type == 'LE_BE_HE':
                le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
                error = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2
                     + (he_fit - friction_factor_he)**2) / 3.0
                )
            elif friction_factor_fit_type == 'LE_BE':
                le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                error = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
                )
            elif friction_factor_fit_type == 'BE_HE':
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
                error = np.sqrt(
                    ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
                )
            else:
                error = np.nan
            return error

        # Loop through the friction factor arrays
        for _, (
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ) in enumerate(
            zip(
                self.friction_factor_le,
                self.friction_factor_be,
                self.friction_factor_he,
                self.friction_factor_fit_type
            )
        ):
            initial_location = np.mean(
                [np.log(friction_factor_le),
                 np.log(friction_factor_be),
                 np.log(friction_factor_he)]
            )
            initial_scale = np.std(
                [np.log(friction_factor_le),
                 np.log(friction_factor_be),
                 np.log(friction_factor_he)],
                ddof=1
            )
            initial_guess = [initial_location, initial_scale]

            # Use minimize to find the parameters that minimize RMSE
            result = minimize(
                objective,
                initial_guess,
                args=(
                    friction_factor_le,
                    friction_factor_be,
                    friction_factor_he,
                    friction_factor_fit_type
                ),
                method='Nelder-Mead'
            )
            location_param, scale_param = result.x

            # Calculate lognormal parameters based on the optimized lognormal distribution
            mean_friction = np.exp(location_param + scale_param**2 / 2)
            std_friction = np.sqrt((np.exp(scale_param**2) - 1) * \
                                   np.exp(2 * location_param + scale_param**2))

            # Calculate the fitted values
            le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
            be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
            he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)

            # Calculate RMSE
            if friction_factor_fit_type == 'LE_BE_HE':
                rmse = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2 +\
                                (he_fit - friction_factor_he)**2) / 3.0
                )
            elif friction_factor_fit_type == 'LE_BE':
                rmse = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
                )
            elif friction_factor_fit_type == 'BE_HE':
                rmse = np.sqrt(
                    ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
                )
            else:
                rmse = np.nan

            # Append results for this iteration
            mean_friction_list.append(mean_friction)
            std_friction_list.append(std_friction)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            rmse_list.append(rmse)

        # Convert lists to NumPy arrays
        mean_friction = np.array(mean_friction_list)
        std_friction = np.array(std_friction_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        rmse = np.array(rmse_list)

        return (
            mean_friction,
            std_friction,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            rmse
        )
