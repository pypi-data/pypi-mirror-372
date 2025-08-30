'''
This module provides classes and functions for calculating DNV pipeline limit states and material
properties.

**Features:**

- The `DNVGeneral` class implements calculations for temperature derating, yield and tensile
  strength, and characteristic material burst strength, supporting both scalar and array-based
  inputs.
- The `DNVLimitStates` class extends `DNVGeneral` and provides burst pressure calculations for
  pipelines according to DNV standards.
- Designed for use in subsea pipeline and riser engineering, but general enough for any DNV-based
  pipeline property calculations.
All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np

class DNVGeneral: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Base class for DNV pipeline limit state calculations. Provides methods for temperature
    derating, yield and tensile strength, and characteristic material burst strength,
    supporting both scalar and array-based inputs.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        The outer diameter of the pipeline.
    corroded_wall_thickness : float or array-like, optional
        The corroded wall thickness of the pipeline.
    material : float or array-like, optional
        Material types: 1 for 'CMn' or '13CR', 2 for '22Cr' or '25CR'.
    smys : float or array-like, optional
        Specified minimum yield strengths.
    smts : float or array-like, optional
        Specified minimum tensile strengths.
    temperature : float or array-like, optional
        Temperatures for calculations.
    material_strength_factor : float or array-like, optional
        Material strength factor.

    Notes
    -----
    All calculations are vectorized using NumPy for efficiency and flexibility.
    """

    def __init__(
            self,
            *,
            outer_diameter=0.0,
            corroded_wall_thickness=0.0,
            material=None,
            smys=0.0,
            smts=0.0,
            temperature=0.0,
            material_strength_factor=0.0
        ):
        """
        Initialize with material, strength, and geometric properties.
        """
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.corroded_wall_thickness = np.asarray(corroded_wall_thickness, dtype = float)
        self.material = np.asarray(material, dtype = float)
        self.smys = np.asarray(smys, dtype = float)
        self.smts = np.asarray(smts, dtype = float)
        self.temperature = np.asarray(temperature, dtype = float)
        self.material_strength_factor = np.asarray(material_strength_factor, dtype = float)

    def temperature_derating_stress(self):
        """
        Calculate the temperature derating stress of a material.

        Returns
        -------
        temperature_derated_stress : np.ndarray
            The derating stress values for the given materials and temperatures.

        Raises
        ------
        ValueError
            If a material is not supported.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> dnv = DNVGeneral(
        ...     material=materials, 
        ...     temperature=temperatures
        ... )
        >>> dnv.temperature_derating_stress()
        array([18000000., 34000000., 70000000., 95000000.])
        """
        derating_array = np.empty(0)
        for mat, temp in zip(self.material, self.temperature):
            if mat == 1:
                derating_value = np.interp(temp,
                                           [50.0, 100.0, 200.0],
                                           [0.0, 30.0E+06, 70.0E+06])
            elif mat == 2:
                derating_value = np.interp(temp,
                                           [20.0, 50.0, 100.0, 200.0],
                                           [0.0, 40.0E+06, 90.0E+06, 140.0E+06])
            else:
                raise ValueError('Material not supported')
            derating_array = np.append(derating_array, derating_value)
        return derating_array

    def yield_stress(self):
        """
        Calculate the yield stress of a material.

        Returns
        -------
        yield_stress : np.ndarray
            The yield stress values of the materials at the given temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smys=smys,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.yield_stress()
        array([4.1472e+08, 3.9936e+08, 4.6080e+08, 4.3680e+08])
        """
        derating_value = self.temperature_derating_stress()
        return (self.smys - derating_value) * self.material_strength_factor

    def tensile_strength(self):
        """
        Calculate the tensile strength of a material.

        Returns
        -------
        tensile_strength : np.ndarray
            The tensile strength values of the materials at the given
            temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smts = np.array([485.0E+06, 485.0E+06, 590.0E+06, 590.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.tensile_strength()
        array([4.4832e+08, 4.3296e+08, 4.9920e+08, 4.7520e+08])
        """
        derating_value = self.temperature_derating_stress()
        return (self.smts - derating_value) * self.material_strength_factor

    def characteristic_material_burst_strength(self):
        """
        Calculate the characteristic material burst strength.

        Returns
        -------
        characteristic_burst_strength : np.ndarray
            The characteristic material burst strength values at the given
            temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> smts = np.array([600.0E+06, 600.0E+06, 700.0E+06, 700.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smys=smys,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.characteristic_material_burst_strength()
        array([4.1472e+08, 3.9936e+08, 4.6080e+08, 4.3680e+08])
        """
        yield_stress_value = self.yield_stress()
        tensile_strength_value = self.tensile_strength()
        return np.minimum(yield_stress_value, tensile_strength_value / 1.15)


class DNVLimitStates(DNVGeneral):
    """
    Class for DNV pipeline burst pressure limit state calculations.

    Extends `DNVGeneral` to provide burst pressure calculations for corroded pipelines
    according to DNV standards, using material, geometric, and strength properties.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        The outer diameter of the pipeline.
    corroded_wall_thickness : float or array-like, optional
        The corroded wall thickness of the pipeline.
    material : float or array-like, optional
        Material types: 1 for 'CMn' or '13CR', 2 for '22Cr' or '25CR'.
    smys : float or array-like, optional
        Specified minimum yield strengths.
    smts : float or array-like, optional
        Specified minimum tensile strengths.
    temperature : float or array-like, optional
        Temperatures for calculations.
    material_strength_factor : float or array-like, optional
        Material strength factor.

    Notes
    -----
    All parameters are passed to the parent class `DNVGeneral`.
    """

    def burst_pressure(self):
        """
        Calculate the burst pressure of a pipeline.

        Returns
        -------
        burst_pressure : np.ndarray
            The burst pressure values of the pipeline.

        Raises
        ------
        ValueError
            If a material is not supported.

        Examples
        --------
        >>> outer_diameter = np.array([0.2731, 0.3239, 0.2731, 0.3239])
        >>> corroded_wall_thickness = np.array([0.0097, 0.0129, 0.0097, 0.0129])
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> smts = np.array([600.0E+06, 600.0E+06, 700.0E+06, 700.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVLimitStates(
        ...     outer_diameter=outer_diameter,
        ...     corroded_wall_thickness=corroded_wall_thickness,
        ...     material=materials,
        ...     smys=smys,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.burst_pressure()
        array([35270393.70222808, 38255444.18258572, 39189326.33580898, 41841892.07470313])
        """
        fcb = self.characteristic_material_burst_strength()
        return (
            (2.0 * self.corroded_wall_thickness)
            / (self.outer_diameter - self.corroded_wall_thickness)
            * fcb * 2.0 / np.sqrt(3.0)
        )
