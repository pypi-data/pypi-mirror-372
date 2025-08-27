'''
This module provides the core class and functions for representing and calculating the main
geometric and material properties of pipeline sections.

**Features:**

- The `Pipe` class encapsulates the geometry and material characteristics of a pipeline section,
  supporting both scalar and array-based calculations for batch processing.
- Methods for computing inner/outer diameters, areas, steel and coating cross-sections, stiffness,
  and moments of inertia.
- Designed for use in subsea pipeline and riser engineering, but general enough for any pipeline
  property calculations.

All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />
'''

import numpy as np
class Pipe: # pylint: disable=too-many-arguments
    """
    Class representing a pipeline section with geometric and material properties.
    Supports both scalar and array inputs for calculations.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        Outer diameter of the pipe (m). Default is 0.
    wall_thickness : float or array-like, optional
        Wall thickness of the pipe (m). Default is 0.
    coating_thickness : float or array-like, optional
        Coating wall thickness (m). Default is 0.
    corrosion_allowance : float or array-like, optional
        Corrosion allowance (m). Default is 0.
    youngs_modulus : float or array-like, optional
        Young's modulus of the material (Pa). Default is 0.
    """
    def __init__(
            self,
            *,
            outer_diameter=0.0,
            wall_thickness=0.0,
            coating_thickness=0.0,
            corrosion_allowance=0.0,
            youngs_modulus=0.0
        ):
        """
        Initialize a Pipe object with geometric and material properties.
        """
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.wall_thickness = np.asarray(wall_thickness, dtype = float)
        self.coating_thickness = np.asarray(coating_thickness, dtype = float)
        self.corrosion_allowance = np.asarray(corrosion_allowance, dtype = float)
        self.youngs_modulus = np.asarray(youngs_modulus, dtype = float)

    def wall_thickness_corroded(self):
        """
        Calculate the corroded wall thickness.

        Returns
        -------
        corroded_wall_thickness : np.ndarray
            Corroded wall thickness of the pipe.

        Examples
        --------
        >>> wall_thickness = [0.0127, 0.0159]
        >>> corrosion_allowance = [0.003, 0.003]
        >>> pipe = Pipe(
        ...     wall_thickness=wall_thickness,
        ...     corrosion_allowance=corrosion_allowance
        ... )
        >>> pipe.wall_thickness_corroded()
        array([0.0097, 0.0129])
        """
        return self.wall_thickness - self.corrosion_allowance

    def inner_diameter(self):
        """
        Calculate the pipe inner diameter.

        Returns
        -------
        inner_diameter : np.ndarray
            Inner diameter of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.inner_diameter()
        array([0.2477, 0.2921])
        """
        return self.outer_diameter - 2.0 * self.wall_thickness

    def inner_area(self):
        """
        Calculate the pipe inner area.

        Returns
        -------
        inner_area : np.ndarray
            Inner area of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.inner_area()
        array([0.04818833, 0.06701206])
        """
        return np.pi / 4.0 * self.inner_diameter() ** 2

    def outer_area(self):
        """
        Calculate the pipe outer area.

        Returns
        -------
        outer_area : np.ndarray
            Outer area of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter
        ... )
        >>> pipe.outer_area()
        array([0.05857783, 0.08239707])
        """
        return np.pi / 4.0 * self.outer_diameter ** 2

    def steel_area(self):
        """
        Calculate the steel cross-sectional area.

        Returns
        -------
        steel_area : np.ndarray
            Steel cross-sectional area.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.steel_area()
        array([0.0103895 , 0.01538501])
        """
        return self.outer_area() - self.inner_area()

    def total_outer_diameter(self):
        """
        Calculate the total outer diameter of steel and coating.

        Returns
        -------
        total_outer_diameter : np.ndarray
            Total outer diameter of steel and coating.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thickness = [0.003, 0.003]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thickness=coating_thickness
        ... )
        >>> pipe.total_outer_diameter()
        array([0.2791, 0.3299])
        """
        return self.outer_diameter + 2.0 * self.coating_thickness

    def total_outer_area(self):
        """
        Calculate the outer area of steel and coating.

        Returns
        -------
        total_outer_area : np.ndarray
            Outer area of steel and coating.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thickness = [0.003, 0.003]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thickness=coating_thickness
        ... )
        >>> pipe.total_outer_area()
        array([0.06118001, 0.08547803])
        """
        return np.pi / 4.0 * self.total_outer_diameter() ** 2

    def coating_area(self):
        """
        Calculate the coating cross-sectional area.

        Returns
        -------
        coating_area : np.ndarray
            Coating cross-sectional area.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thickness = [0.003, 0.003]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thickness=coating_thickness
        ... )
        >>> pipe.coating_area()
        array([0.00260218, 0.00308096])
        """
        return self.total_outer_area() - self.outer_area()

    def axial_stiffness(self):
        """
        Calculate the axial stiffness.

        Returns
        -------
        axial_stiffness : np.ndarray
            Axial stiffness of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     youngs_modulus=youngs_modulus
        ... )
        >>> pipe.axial_stiffness()
        array([2.15062613e+09, 3.18469656e+09])
        """
        return self.youngs_modulus * self.steel_area()

    def area_moment_inertia(self):
        """
        Calculate the area moment inertia.

        Returns
        -------
        area_moment_inertia : np.ndarray
            Area moment inertia.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.area_moment_inertia()
        array([8.82710601e-05, 1.82921605e-04])
        """
        return np.pi / 64.0 * (self.outer_diameter ** 4 - self.inner_diameter() ** 4)

    def bending_stiffness(self):
        """
        Calculate the bending stiffness.

        Returns
        -------
        bending_stiffness : np.ndarray
            Bending stiffness.


        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     youngs_modulus=youngs_modulus
        ... )
        >>> pipe.bending_stiffness()
        array([18272109.437121..., 37864772.21769765])
        """
        return self.youngs_modulus * self.area_moment_inertia()
