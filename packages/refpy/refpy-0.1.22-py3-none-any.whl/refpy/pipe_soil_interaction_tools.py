"""
This module provides classes and functions for calculating the capacity of soils using various
models for a given pipe and soil configuration.

**Features:**

- The `PSI` class implements soil capacity calculations for different pipe and soil properties,
  supporting vectorized and model-based approaches.
- Designed for use in subsea pipeline and riser engineering, but general enough for any
  pipe-soil interaction analysis.
- All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

"""

import numpy as np

class PSI: # pylint: disable=too-many-arguments
    """
    Class for calculating the capacity of soils using various models
    for a given pipe and soil configuration.

    Parameters
    ----------
    diameter : float, optional
        Diameter of the pipe.
    surface_roughness : str, optional
        Surface roughness of the pipe ('Smooth' or 'Rough').
    density : float, optional
        Density of the soil.
    surcharge_on_seabed : float, optional
        Stress or surcharge at the elevation of the seabed.
    burial_depth : float, optional
        Depth of burial.
    """
    def __init__(
            self,
            *,
            total_outer_diameter=0.0,
            surface_roughness=None,
            density=0.0,
            surcharge_on_seabed=0.0,
            burial_depth=0.0
        ):
        """
        Initialize a PipeSoilInteraction object with pipe and soil properties.
        """
        self.total_outer_diameter =  np.asarray(total_outer_diameter, dtype = float)
        self.surface_roughness =  np.asarray(surface_roughness, dtype = object)
        self.density =  np.asarray(density, dtype = float)
        self.surcharge_on_seabed =  np.asarray(surcharge_on_seabed, dtype = float)
        self.burial_depth =  np.asarray(burial_depth, dtype = float)

    def downward_undrained_model1(self): # pylint: disable=too-many-locals
        """
        Calculate the vertical bearing capacity of soil using the downward undrained model.

        Returns
        -------
        depth_arrays : np.ndarray
            Array of depth arrays for each total_outer_diameter value.
        vertical_bearing_capacity_arrays : np.ndarray
            Array of vertical bearing capacity arrays for each total_outer_diameter value.
        Examples
        --------
        >>> psi = PSI(
        ...     total_outer_diameter=[0.2731],
        ...     surface_roughness=['Smooth'],
        ...     density=[1000.0],
        ...     surcharge_on_seabed=[100],
        ...     burial_depth=[1.0]
        ... )
        >>> psi.downward_undrained_model1()
        (array([[0.   , 0.005, ... 0.995, 1.   ]]),
         array([[   0.        ,  920.50185636, ... 7141.92857341, 7163.61163085]]))
        """
        depth_arrays = []
        vertical_bearing_capacity_arrays = []

        for i, outer_diameter in enumerate(self.total_outer_diameter):
            # Access corresponding values for other attributes using the index `i`
            surface_roughness = self.surface_roughness[i]
            density = self.density[i]
            surcharge_on_seabed = self.surcharge_on_seabed[i]
            burial_depth = self.burial_depth[i]

            # Generate depth array
            depth = np.linspace(0.005, 1, 200)

            # Calculate width using vectorized operations
            width = np.where(
                depth < outer_diameter / 2,
                2 * np.sqrt(np.maximum(outer_diameter * depth - depth ** 2, 0)),
                outer_diameter
            )

            # Calculate undrained shear strength using vectorized operations
            undrained_shear_strength = np.where(
                depth < outer_diameter / 2 * (1 - np.sqrt(2) / 2.),
                0.0,
                depth + outer_diameter / 2 * (np.sqrt(2) - 1) - width / 2
            )

            initial_shear_strength = surcharge_on_seabed + density * undrained_shear_strength
            friction_factor = np.divide(np.multiply(density, width), initial_shear_strength)
            friction_factor_reference = np.linspace(0, 16, 17)

            if surface_roughness == 'Smooth':
                friction_factor_values = np.array(
                    [1.00, 1.12, 1.19, 1.24, 1.28, 1.31, 1.34, 1.36, 1.38,
                     1.39, 1.40, 1.41, 1.42, 1.43, 1.44, 1.445, 1.45]
                )
            else:
                friction_factor_values = np.array(
                    [1.00, 1.23, 1.36, 1.44, 1.50, 1.55, 1.59, 1.61, 1.64,
                     1.66, 1.67, 1.69, 1.70, 1.71, 1.72, 1.730, 1.74]
                )

            interpolated_friction_factor = np.interp(
                friction_factor, friction_factor_reference, friction_factor_values
            )

            vertical_bearing_capacity = interpolated_friction_factor * (
                5.14 * initial_shear_strength + density * width / 4 + density * 9.807 * burial_depth
            ) * width

            average_shear_strength_1 = (surcharge_on_seabed + initial_shear_strength) / 2.0
            average_shear_strength_2 = vertical_bearing_capacity / width / 5.14

            depth_correction_factor = 0.3 * average_shear_strength_1 / average_shear_strength_2 * \
                np.arctan2(undrained_shear_strength, width)

            bearing_capacity_modifier = np.where(
                depth < outer_diameter / 2,
                np.arcsin(width / outer_diameter) * outer_diameter ** 2 / 4 +
                width * outer_diameter / 4 * np.cos(np.arcsin(width / outer_diameter)),
                np.pi * outer_diameter ** 2 / 8 +
                outer_diameter * (depth - outer_diameter / 2)
            )

            vertical_bearing_capacity = (
                vertical_bearing_capacity * (1 + depth_correction_factor) 
                + density * 9.807 * bearing_capacity_modifier
            )

            # Append depth and vertical_bearing_capacity arrays for this outer_diameter
            depth_arrays.append(np.append(0, depth))
            vertical_bearing_capacity_arrays.append(np.append(0, vertical_bearing_capacity))

        # Convert lists to NumPy arrays
        depth_arrays = np.array(depth_arrays)
        vertical_bearing_capacity_arrays = np.array(vertical_bearing_capacity_arrays)

        return depth_arrays, vertical_bearing_capacity_arrays
