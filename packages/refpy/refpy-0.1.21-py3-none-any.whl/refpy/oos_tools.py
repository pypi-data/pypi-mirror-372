# pylint: disable=too-many-lines
'''
This module provides classes and functions for processing and analyzing Out-Of-Straightness (OOS)
pipeline survey and route data.

**Features:**

- Designed for use in subsea pipeline, but general enough for any OOS survey
  data processing and analysis tasks.
- The `OOSAnonymisation` class processes OOS survey and route data, providing methods for
  cleaning, sectioning, coordinate normalization, and anonymization of pipeline survey datasets.
- The `OOSDespiker` class implements rolling window sigma-clipping despiking for OOS survey data,
  removing outliers while preserving data alignment and group structure.
- The `FFTSmoother` and `GaussianSmoother` class implements group-wise signal processing and
  smoothing (FFT, Gaussian, etc.) for OOS survey data, supporting robust, efficient, and
  reproducible analysis.

All calculations are vectorized using NumPy and SciPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />
'''

import numpy as np
from scipy.optimize import leastsq
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import welch
from scipy.ndimage import generic_filter

class OOSAnonymisation: # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-locals, too-few-public-methods
    """
    Processor for Out-Of-Straightness (OOS) pipeline survey and route data.
    Provides methods for cleaning, sectioning, and coordinate normalization.
    All input arrays (parameters) are converted to NumPy arrays and stored as
    attributes. Additional attributes are initialized as NumPy arrays and will
    be populated by processing methods.

    Parameters
    ----------
    route_development : np.ndarray
        Development identifiers for each route section.
    route_pipeline_group : np.ndarray
        Pipeline group identifiers for each route section.
    route_pipeline : np.ndarray
        Pipeline identifiers for each route section.
    route_kp_from : np.ndarray
        Start KP (kilometer point) for each route section.
    route_kp_to : np.ndarray
        End KP (kilometer point) for each route section.
    route_pipeline_section_type : np.ndarray
        Section type (e.g., 'Straight', 'Curve', etc.) for each route section.
    route_curve_radius : np.ndarray
        Design curve radius for each route section.
    survey_development : np.ndarray
        Development identifiers for each survey point.
    survey_type : np.ndarray
        Survey type for each survey point.
    survey_pipeline_group : np.ndarray
        Pipeline group identifiers for each survey point.
    survey_pipeline : np.ndarray
        Pipeline identifiers for each survey point.
    survey_kp : np.ndarray
        KP (kilometer point) for each survey point.
    survey_easting : np.ndarray
        Easting coordinate for each survey point.
    survey_northing : np.ndarray
        Northing coordinate for each survey point.
    """
    def __init__(
            self,
            *,
            route_development,
            route_pipeline_group,
            route_pipeline,
            route_kp_from,
            route_kp_to,
            route_pipeline_section_type,
            route_curve_radius,
            survey_development,
            survey_type,
            survey_pipeline_group,
            survey_pipeline,
            survey_kp,
            survey_easting,
            survey_northing
        ):
        """
        Initialize an OOSAnonymisation object with route and survey data.
        """
        # Initialise parameter arrays for the route data
        self.route_development = np.asarray(route_development, dtype=object)
        self.route_pipeline_group = np.asarray(route_pipeline_group, dtype=object)
        self.route_pipeline = np.asarray(route_pipeline, dtype=object)
        self.route_kp_from = np.asarray(route_kp_from, dtype=float)
        self.route_kp_to = np.asarray(route_kp_to, dtype=float)
        self.route_pipeline_section_type = np.asarray(route_pipeline_section_type, dtype=object)
        self.route_curve_radius = np.asarray(route_curve_radius, dtype=float)
        # Initialise parameter arrays for the survey data
        self.survey_development = np.asarray(survey_development, dtype=object)
        self.survey_type = np.asarray(survey_type, dtype=object)
        self.survey_pipeline_group = np.asarray(survey_pipeline_group, dtype=object)
        self.survey_pipeline = np.asarray(survey_pipeline, dtype=object)
        self.survey_kp = np.asarray(survey_kp, dtype=float)
        self.survey_easting = np.asarray(survey_easting, dtype=float)
        self.survey_northing = np.asarray(survey_northing, dtype=float)
        # Initialise returns arrays for the survey data, section grouped
        self.survey_section_type = np.full(
            self.survey_kp.shape[0], '', dtype=object
        )
        self.survey_section_no = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_section_kp_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_section_easting_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_section_northing_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_feature = np.full(
            self.survey_kp.shape[0], '', dtype=object
        )
        self.survey_design_route_curve_radius = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_actual_route_curve_radius = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        # Initialise returns arrays for the survey data, pipeline group grouped
        self.survey_group_section_no = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_group_section_type = np.full(
            self.survey_kp.shape[0], '', dtype=object
        )
        self.survey_group_section_kp_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_group_section_easting_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )
        self.survey_group_section_northing_mod = np.full(
            self.survey_kp.shape[0], np.nan, dtype=float
        )

    def process(self, anonymise: bool = False):
        """
        Run the OOS processing pipeline.

        Parameters
        ----------
        anonymise : bool, default False
            If True, runs the full anonymisation pipeline (with cleaning and grouping).
            If False, runs only the basic section processing.
        """
        self._add_pipeline_section()
        self._add_feature_labels()
        self._add_design_route_curve_radius()
        self._add_actual_route_curve_radius()
        self._transform_pipeline_section_coordinates()
        if anonymise:
            self._trim_feature_kps()
            self._trim_straight_section_ends()
            self._add_pipeline_group_section()
            self._transform_pipeline_group_section_coordinates()

    def _add_pipeline_section(self):
        """
        Add section type ('Straight' or 'Curve') and section number to each survey point.

        For each survey point, determines if it falls within a non-straight route section (based on
        matching pipeline group, pipeline, and KP range) and adds 'Curve' or 'Straight' to
        self.survey_section_type. Then, adds a unique section number (self.survey_section_no) to
        each continuous section of the same type within each (pipeline group, pipeline, survey type)
        group.

        Updates
        -------
        self.survey_section_type : np.ndarray
            Section type ('Straight' or 'Curve') for each survey point.
        self.survey_section_no : np.ndarray
            Section number for each survey point, incremented for each new section.

        Returns
        -------
        None
        """
        # Build mask for non-straight route sections
        mask = ~np.isin(self.route_pipeline_section_type, ['LBMD', 'PWMD', 'ILT', 'Straight'])
        # Indices of route sections that are not straight
        idxs = np.where(mask)[0]
        mask_curve = np.full(self.survey_kp.shape[0], False)
        for i in idxs:
            cond = (
                (self.survey_development == self.route_development[i]) &
                (self.survey_pipeline_group == self.route_pipeline_group[i]) &
                (self.survey_pipeline == self.route_pipeline[i]) &
                (self.survey_kp >= self.route_kp_from[i]) &
                (self.survey_kp <= self.route_kp_to[i])
            )
            mask_curve = mask_curve | cond
        # Create or update section type array
        section_type = np.full(self.survey_kp.shape[0], 'Straight', dtype=object)
        section_type[mask_curve] = 'Curve'
        self.survey_section_type = section_type

        # Add Section No for each continuous section
        group_keys = [
            self.survey_development, self.survey_type,
            self.survey_pipeline_group, self.survey_pipeline
        ]
        section_no = np.zeros(self.survey_kp.shape[0], dtype=int)
        prev_keys = None
        prev_type = None
        current_section = 0
        for i in range(self.survey_kp.shape[0]):
            keys = tuple(key[i] for key in group_keys)
            curr_type = section_type[i]
            if keys != prev_keys:
                current_section = 1
            elif curr_type != prev_type:
                current_section += 1
            section_no[i] = current_section
            prev_keys = keys
            prev_type = curr_type
        self.survey_section_no = section_no

    def _add_feature_labels(self):
        """
        Adds a new attribute 'survey_feature' to the survey points.
        For each feature (PWMD, LBMD, ILT) in the route, finds the closest survey point
        (matching development, pipeline group, pipeline) in KP and adds the feature name
        at that position.
        All other survey points have an empty string.
        """
        feature_types = ['PWMD', 'LBMD', 'ILT']
        for i, section_type in enumerate(self.route_pipeline_section_type):
            if section_type in feature_types:
                dev = self.route_development[i]
                group = self.route_pipeline_group[i]
                pipe = self.route_pipeline[i]
                kp = self.route_kp_from[i]
                # Find matching survey points
                mask = (
                    (self.survey_development == dev) &
                    (self.survey_pipeline_group == group) &
                    (self.survey_pipeline == pipe)
                )
                if not np.any(mask):
                    continue
                kp_survey = self.survey_kp[mask]
                idx_in_mask = np.argmin(np.abs(kp_survey - kp))
                idx = np.where(mask)[0][idx_in_mask]
                # Only assign if not last index, or if kp matches exactly
                if idx_in_mask != len(kp_survey) - 1 or np.isclose(kp, kp_survey[idx_in_mask]):
                    self.survey_feature[idx] = section_type

    def _add_design_route_curve_radius(self):
        """
        Add the 'Design Route Curve Radius' from route data to each survey point where the
        section type is 'Curve'.

        For each survey point with section type 'Curve', finds the matching route section (by
        development, pipeline group, pipeline, and KP within [KP From, KP To]) and adds
        the corresponding route curve radius to self.survey_design_route_curve_radius.

        Updates
        -------
        self.survey_design_route_curve_radius : np.ndarray
            Design route curve radii for each survey point (NaN for non-curve points).

        Returns
        -------
        None
        """
        mask_curve = self.survey_section_type == 'Curve'
        for i, _ in enumerate(self.route_development):
            cond = (
                (self.survey_development == self.route_development[i]) &
                (self.survey_pipeline_group == self.route_pipeline_group[i]) &
                (self.survey_pipeline == self.route_pipeline[i]) &
                (self.survey_kp >= self.route_kp_from[i]) &
                (self.survey_kp <= self.route_kp_to[i]) &
                mask_curve
            )
            self.survey_design_route_curve_radius[cond] = self.route_curve_radius[i]

    def _add_actual_route_curve_radius(self):
        """
        Fit a circle to each group of survey points where the section type is 'Curve' and add
        the fitted radius.

        For each group of survey points (grouped by development, pipeline group, pipeline, survey
        type, and section number) where all points are of type 'Curve' and there are more than 3
        points, fit a circle to the (easting, northing) coordinates and add the resulting radius
        to self.survey_actual_route_curve_radius for those points. Non-curve points or groups with
        insufficient points remain NaN.

        Updates
        -------
        self.survey_actual_route_curve_radius : np.ndarray
            Fitted curve radii for each survey point (NaN for non-curve points or insufficient
            data).

        Returns
        -------
        None
        """
        def calc_radius(x, y, xc, yc):
            return np.sqrt((x - xc) ** 2 + (y - yc) ** 2)
        def fit_circle(x, y):
            x_m = np.mean(x)
            y_m = np.mean(y)
            def f(c):
                radius_i = calc_radius(x, y, *c)
                return radius_i - radius_i.mean()
            center_estimate = x_m, y_m
            center, _ = leastsq(f, center_estimate)
            xc, yc = center
            radius_i = calc_radius(x, y, xc, yc)
            radius = radius_i.mean()
            return radius
        # Group by (development, survey_type, survey_pipeline_group,
        # survey_pipeline, survey_section_no)
        group_tuples = list(zip(
            self.survey_development,
            self.survey_type,
            self.survey_pipeline_group,
            self.survey_pipeline,
            self.survey_section_no
        ))
        unique_groups = set(group_tuples)
        for group in unique_groups:
            mask = (
                (self.survey_development == group[0]) &
                (self.survey_type == group[1]) &
                (self.survey_pipeline_group == group[2]) &
                (self.survey_pipeline == group[3]) &
                (self.survey_section_no == group[4])
            )
            if np.all(self.survey_section_type[mask] == 'Curve') and np.sum(mask) > 3:
                x = self.survey_easting[mask]
                y = self.survey_northing[mask]
                radius = fit_circle(x, y)
                self.survey_actual_route_curve_radius[mask] = radius

    def _transform_pipeline_section_coordinates(self):
        """
        Compute and add section-modified coordinates and KP for each pipeline section.

        For each group of survey points (grouped by development, pipeline group, pipeline,
        survey type, and section number):
        - Shift Easting/Northing so the section starts at (0,0)
        - Rotate the section so it ends at (d, 0) (horizontal line)
        - Compute a section-modified KP (distance along the section, starting at 0)
        The results are stored in self.survey_section_easting_mod,
        self.survey_section_northing_mod, and self.survey_section_kp_mod for each survey point.

        Updates
        -------
        self.survey_section_easting_mod : np.ndarray
            Section-modified easting coordinates for each survey point.
        self.survey_section_northing_mod : np.ndarray
            Section-modified northing coordinates for each survey point.
        self.survey_section_kp_mod : np.ndarray
            Section-modified KP (distance along section, starting at 0) for each survey point.

        Returns
        -------
        None
        """

        group_tuples = list(zip(
            self.survey_development,
            self.survey_type,
            self.survey_pipeline_group,
            self.survey_pipeline,
            self.survey_section_no
        ))
        unique_groups = set(group_tuples)
        for group in unique_groups:
            mask = (
                (self.survey_development == group[0]) &
                (self.survey_type == group[1]) &
                (self.survey_pipeline_group == group[2]) &
                (self.survey_pipeline == group[3]) &
                (self.survey_section_no == group[4])
            )
            idx = np.where(mask)[0]
            if len(idx) == 0:
                continue
            x = self.survey_easting[idx]
            y = self.survey_northing[idx]
            x0, y0 = x[0], y[0]
            x_shift = x - x0
            y_shift = y - y0
            dx = x_shift[-1]
            dy = y_shift[-1]
            theta = -np.arctan2(dy, dx)
            x_mod = x_shift * np.cos(theta) - y_shift * np.sin(theta)
            y_mod = x_shift * np.sin(theta) + y_shift * np.cos(theta)
            kp_mod = np.append(0, np.cumsum(np.diff(self.survey_kp[idx])))
            self.survey_section_easting_mod[idx] = x_mod
            self.survey_section_northing_mod[idx] = y_mod
            self.survey_section_kp_mod[idx] = kp_mod

    def _trim_feature_kps(self):
        """
        Remove survey points where KP is within ±0.2 km of any KP From in the route data for
        matching development, pipeline group, and pipeline.

        Applies a mask to all survey arrays, shortening them in place. This is typically used to
        remove points near mitigation features (e.g., LBMD, PWMD, ILT) from the survey data.

        Updates
        -------
        All survey arrays are filtered in place, reducing their length.

        Returns
        -------
        None
        """
        mitigation_mask = np.isin(self.route_pipeline_section_type, ['LBMD', 'PWMD', 'ILT'])
        keep_mask = np.ones(self.survey_kp.shape[0], dtype=bool)
        for i in np.where(mitigation_mask)[0]:
            cond = (
                (self.survey_development == self.route_development[i]) &
                (self.survey_pipeline_group == self.route_pipeline_group[i]) &
                (self.survey_pipeline == self.route_pipeline[i]) &
                (np.abs(self.survey_kp - self.route_kp_from[i]) <= 0.2)
            )
            keep_mask = keep_mask & ~cond
        # Apply mask to all survey arrays
        self.survey_development = self.survey_development[keep_mask]
        self.survey_type = self.survey_type[keep_mask]
        self.survey_pipeline_group = self.survey_pipeline_group[keep_mask]
        self.survey_pipeline = self.survey_pipeline[keep_mask]
        self.survey_kp = self.survey_kp[keep_mask]
        self.survey_easting = self.survey_easting[keep_mask]
        self.survey_northing = self.survey_northing[keep_mask]
        self.survey_section_type = self.survey_section_type[keep_mask]
        self.survey_section_no = self.survey_section_no[keep_mask]
        self.survey_section_kp_mod = self.survey_section_kp_mod[keep_mask]
        self.survey_section_easting_mod = self.survey_section_easting_mod[keep_mask]
        self.survey_section_northing_mod = self.survey_section_northing_mod[keep_mask]
        self.survey_design_route_curve_radius = self.survey_design_route_curve_radius[keep_mask]
        self.survey_actual_route_curve_radius = self.survey_actual_route_curve_radius[keep_mask]
        self.survey_feature = self.survey_feature[keep_mask]

    def _trim_straight_section_ends(self):
        """
        Trim 50 meters from both ends of all Straight sections, but only when the section changes
        from Curve to Straight or from Straight to Curve.

        Applies a mask to all survey arrays, shortening them in place. Only points at the ends of
        straight sections adjacent to curves are removed.

        Updates
        -------
        All survey arrays are filtered in place, reducing their length.

        Returns
        -------
        None
        """
        n = self.survey_kp.shape[0]
        keep_mask = np.ones(n, dtype=bool)
        # Group by (Development, Pipeline Group, Pipeline, Survey Type, Section No)
        group_tuples = list(zip(
            self.survey_development,
            self.survey_type,
            self.survey_pipeline_group,
            self.survey_pipeline,
            self.survey_section_no
        ))
        unique_groups = set(group_tuples)
        for group in unique_groups:
            mask = (
                (self.survey_development == group[0]) &
                (self.survey_type == group[1]) &
                (self.survey_pipeline_group == group[2]) &
                (self.survey_pipeline == group[3]) &
                (self.survey_section_no == group[4])
            )
            idx = np.where(mask)[0]
            if len(idx) == 0:
                continue
            if not np.all(self.survey_section_type[idx] == 'Straight'):
                continue
            # Find previous and next section types
            prev_idx = idx[0] - 1 if idx[0] > 0 else None
            next_idx = idx[-1] + 1 if idx[-1] < n - 1 else None
            prev_type = self.survey_section_type[prev_idx] if prev_idx is not None else None
            next_type = self.survey_section_type[next_idx] if next_idx is not None else None
            # Only trim if adjacent to a Curve
            if prev_type == 'Curve':
                kp0 = self.survey_kp[idx].min()
                trim_mask = (self.survey_kp[idx] - kp0) < 0.05
                keep_mask[idx[trim_mask]] = False
            if next_type == 'Curve':
                kp1 = self.survey_kp[idx].max()
                trim_mask = (kp1 - self.survey_kp[idx]) < 0.05
                keep_mask[idx[trim_mask]] = False
        # Apply mask to all survey arrays
        self.survey_development = self.survey_development[keep_mask]
        self.survey_type = self.survey_type[keep_mask]
        self.survey_pipeline_group = self.survey_pipeline_group[keep_mask]
        self.survey_pipeline = self.survey_pipeline[keep_mask]
        self.survey_kp = self.survey_kp[keep_mask]
        self.survey_easting = self.survey_easting[keep_mask]
        self.survey_northing = self.survey_northing[keep_mask]
        self.survey_section_type = self.survey_section_type[keep_mask]
        self.survey_section_no = self.survey_section_no[keep_mask]
        self.survey_section_kp_mod = self.survey_section_kp_mod[keep_mask]
        self.survey_section_easting_mod = self.survey_section_easting_mod[keep_mask]
        self.survey_section_northing_mod = self.survey_section_northing_mod[keep_mask]
        self.survey_design_route_curve_radius = self.survey_design_route_curve_radius[keep_mask]
        self.survey_actual_route_curve_radius = self.survey_actual_route_curve_radius[keep_mask]
        self.survey_feature = self.survey_feature[keep_mask]

    def _add_pipeline_group_section(self):
        """
        Adds group-level section type ('Straight' or 'Curve') and section number to each survey
        point.

        For each survey point, adds the group section type (same as section type) and a unique
        group section number within each (development, pipeline group, survey type) group. The
        section number increments for each new continuous section of the same type.

        Updates
        -------
        self.survey_group_section_type : np.ndarray
            Group section type for each survey point.
        self.survey_group_section_no : np.ndarray
            Group section number for each survey point.

        Returns
        -------
        None
        """
        # Add group section number
        current_section = 0
        group_keys1 = [self.survey_development, self.survey_type, self.survey_pipeline_group]
        group_keys2 = group_keys1 + [self.survey_pipeline, self.survey_section_no]
        prev_keys1 = None
        prev_keys2 = None
        prev_kp = None
        # Group no. loop
        n = self.survey_kp.shape[0]
        group_section_no = np.zeros(n, dtype=int)
        for i in range(n):
            keys1 = tuple(key[i] for key in group_keys1)
            keys2 = tuple(key[i] for key in group_keys2)
            curr_kp = self.survey_kp[i]
            if keys1 != prev_keys1:
                current_section = 1  # Reset to 1 when group_keys changes
            elif keys2 != prev_keys2:
                current_section += 1  # Increase if section type changes
            elif prev_kp is not None and curr_kp - prev_kp > 0.350: # +/-200m removed at features
                current_section += 1
            group_section_no[i] = current_section
            prev_keys1 = keys1
            prev_keys2 = keys2
            prev_kp = curr_kp
        self.survey_group_section_no = group_section_no
        self.survey_group_section_type = self.survey_section_type.copy()

    def _transform_pipeline_group_section_coordinates(self): # pylint: disable=too-many-statements
        """
        Compute and add group section-modified coordinates and KP for each pipeline group
        section.

        For each group of survey points (grouped by development, pipeline group, survey type,
        group section type, and group section number):
        - Shift Easting/Northing so the section starts at (0,0)
        - Rotate the section so it ends at (d, 0) (horizontal line)
        - Compute a group section-modified KP (distance along the section, starting at 0)
        The results are stored in self.survey_group_section_easting_mod,
        self.survey_group_section_northing_mod, and self.survey_group_section_kp_mod for each
        survey point.

        Updates
        -------
        self.survey_group_section_easting_mod : np.ndarray
            Group section-modified easting coordinates for each survey point.
        self.survey_group_section_northing_mod : np.ndarray
            Group section-modified northing coordinates for each survey point.
        self.survey_group_section_kp_mod : np.ndarray
            Group section-modified KP (distance along section, in km) for each survey point.

        Returns
        -------
        None
        """
        n = self.survey_kp.shape[0]
        self.survey_group_section_easting_mod = np.full(n, np.nan, dtype=float)
        self.survey_group_section_northing_mod = np.full(n, np.nan, dtype=float)
        self.survey_group_section_kp_mod = np.full(n, np.nan, dtype=float)
        # Group by (Development, Pipeline Group, Survey Type, Group Section Type)
        group_tuples = list(zip(
            self.survey_development,
            self.survey_type,
            self.survey_pipeline_group,
            self.survey_group_section_type
        ))
        unique_groups = set(group_tuples)
        for group in unique_groups:
            mask = (
                (self.survey_development == group[0]) &
                (self.survey_type == group[1]) &
                (self.survey_pipeline_group == group[2]) &
                (self.survey_group_section_type == group[3])
            )
            idx = np.where(mask)[0]

            # Sort idx by group section no to ensure correct order
            section_nos = self.survey_group_section_no[idx]
            unique_section_nos = np.unique(section_nos)
            shift_x = 0.0
            shift_y = 0.0
            for index, sec_no in enumerate(unique_section_nos):
                sec_mask = idx[section_nos == sec_no]
                x = self.survey_section_easting_mod[sec_mask]
                y = self.survey_section_northing_mod[sec_mask]

                # Compute average slope (angle) for the first 20 and last 20 points
                n_points = len(x)
                n_avg = min(20, n_points // 2)  # Use up to 20, but not more than half the section

                # If not the first section, align to average direction between last N points of
                # previous section and first N of current using robust vector method
                if index == 0:
                    theta = 0.0
                else:
                    # Last n_avg points of previous section
                    x_prev = x_prev_all[-prev_n_avg:]
                    y_prev = y_prev_all[-prev_n_avg:]
                    # First n_avg points of current section
                    x_curr = x[:n_avg]
                    y_curr = y[:n_avg]
                    # Best linear fit for previous section
                    if (
                        len(x_prev) < 2 or
                        np.any(np.isnan(x_prev)) or np.any(np.isnan(y_prev)) or
                        np.any(np.isinf(x_prev)) or np.any(np.isinf(y_prev)) or
                        np.all(x_prev == x_prev[0])
                    ):
                        # Fallback: set coeffs_prev to [0, 0] or skip this section
                        coeffs_prev = [0, 0]
                    else:
                        coeffs_prev = np.polyfit(x_prev, y_prev, 1)
                    slope_prev = coeffs_prev[0]
                    v1 = np.array([1.0, slope_prev])  # direction vector from slope
                    v1_u = v1 / np.linalg.norm(v1)
                    # Best linear fit for current section
                    if (
                        len(x_curr) < 2 or
                        np.any(np.isnan(x_curr)) or np.any(np.isnan(y_curr)) or
                        np.any(np.isinf(x_curr)) or np.any(np.isinf(y_curr)) or
                        np.all(x_curr == x_curr[0])
                    ):
                        coeffs_curr = [0, 0]
                    else:
                        coeffs_curr = np.polyfit(x_curr, y_curr, 1)
                    slope_curr = coeffs_curr[0]
                    v2 = np.array([1.0, slope_curr])
                    v2_u = v2 / np.linalg.norm(v2)
                    # Angle between the two vectors
                    dot = np.dot(v1_u, v2_u)
                    det = v1_u[0]*v2_u[1] - v1_u[1]*v2_u[0]
                    theta = -np.arctan2(det, dot)
                # Previous section
                prev_n_avg = n_avg
                # Shift to origin (0,0)
                x_to_origin = x - x[0]
                y_to_origin = y - y[0]
                # Apply rotation
                x_rot = x_to_origin * np.cos(theta) - y_to_origin * np.sin(theta)
                y_rot = x_to_origin * np.sin(theta) + y_to_origin * np.cos(theta)
                # Save previous
                x_prev_all = x_rot
                y_prev_all = y_rot
                # Apply shift for continuity
                x_mod = x_rot + shift_x
                y_mod = y_rot + shift_y
                # Define variables
                kp_mod = np.insert(np.cumsum(np.diff(self.survey_kp[sec_mask])), 0, 0)
                self.survey_group_section_easting_mod[sec_mask] = x_mod
                self.survey_group_section_northing_mod[sec_mask] = y_mod
                self.survey_group_section_kp_mod[sec_mask] = kp_mod
                # Prepare shift for next section: last point of this section
                shift_x = x_mod[-1]
                shift_y = y_mod[-1]

        # Align all sections to the x-axis
        for group in unique_groups:
            mask = (
                (self.survey_development == group[0]) &
                (self.survey_type == group[1]) &
                (self.survey_pipeline_group == group[2]) &
                (self.survey_group_section_type == group[3])
            )
            idx = np.where(mask)[0]

            # Use the group section modified coordinates
            x = self.survey_group_section_easting_mod[idx]
            y = self.survey_group_section_northing_mod[idx]

            # Compute angle to rotate so last point is on the x-axis
            dx = x[-2] - x[1]
            dy = y[-2] - y[1]
            theta = -np.arctan2(dy, dx)

            # Shift so the second point is at the origin
            x_shift = x - x[1]
            y_shift = y - y[1]

            # Rotate all points
            x_aligned = x_shift * np.cos(theta) - y_shift * np.sin(theta) + x[1]
            y_aligned = x_shift * np.sin(theta) + y_shift * np.cos(theta)

            # Store the aligned coordinates back
            self.survey_group_section_easting_mod[idx] = x_aligned
            self.survey_group_section_northing_mod[idx] = y_aligned

            # Ensure the max magnitude of northing is positive
            max_north = np.max(self.survey_group_section_northing_mod[idx])
            min_north = np.min(self.survey_group_section_northing_mod[idx])
            if abs(max_north) < abs(min_north):
                # Flip the sign of northing
                self.survey_group_section_northing_mod[idx] = (
                    -self.survey_group_section_northing_mod[idx]
                )

    def get_route_development(self):
        """
        Get development identifiers for each route section.

        Returns
        -------
        np.ndarray
            Development identifiers for each route section.
        """
        return self.route_development

    def get_route_pipeline_group(self):
        """
        Get pipeline group identifiers for each route section.

        Returns
        -------
        np.ndarray
            Pipeline group identifiers for each route section.
        """
        return self.route_pipeline_group

    def get_route_pipeline(self):
        """
        Get pipeline identifiers for each route section.

        Returns
        -------
        np.ndarray
            Pipeline identifiers for each route section.
        """
        return self.route_pipeline

    def get_route_kp_from(self):
        """
        Get start KP (kilometer point) for each route section.

        Returns
        -------
        np.ndarray
            Start KP (kilometer point) for each route section.
        """
        return self.route_kp_from

    def get_route_kp_to(self):
        """
        Get end KP (kilometer point) for each route section.

        Returns
        -------
        np.ndarray
            End KP (kilometer point) for each route section.
        """
        return self.route_kp_to

    def get_route_pipeline_section_type(self):
        """
        Get section type (e.g., 'Straight', 'Curve', etc.) for each route section.

        Returns
        -------
        np.ndarray
            Section type for each route section.
        """
        return self.route_pipeline_section_type

    def get_route_curve_radius(self):
        """
        Get design curve radius for each route section.

        Returns
        -------
        np.ndarray
            Design curve radius for each route section.
        """
        return self.route_curve_radius

    def get_survey_development(self):
        """
        Get development identifiers for each survey point.

        Returns
        -------
        np.ndarray
            Development identifiers for each survey point.
        """
        return self.survey_development

    def get_survey_type(self):
        """
        Get survey type for each survey point.

        Returns
        -------
        np.ndarray
            Survey type for each survey point.
        """
        return self.survey_type

    def get_survey_pipeline_group(self):
        """
        Get pipeline group identifiers for each survey point.

        Returns
        -------
        np.ndarray
            Pipeline group identifiers for each survey point.
        """
        return self.survey_pipeline_group

    def get_survey_pipeline(self):
        """
        Get pipeline identifiers for each survey point.

        Returns
        -------
        np.ndarray
            Pipeline identifiers for each survey point.
        """
        return self.survey_pipeline

    def get_survey_kp(self):
        """
        Get KP (kilometer point) for each survey point.

        Returns
        -------
        np.ndarray
            KP (kilometer point) for each survey point.
        """
        return self.survey_kp

    def get_survey_easting(self):
        """
        Get easting coordinate for each survey point.

        Returns
        -------
        np.ndarray
            Easting coordinate for each survey point.
        """
        return self.survey_easting

    def get_survey_northing(self):
        """
        Get northing coordinate for each survey point.

        Returns
        -------
        np.ndarray
            Northing coordinate for each survey point.
        """
        return self.survey_northing

    def get_survey_section_type(self):
        """
        Get section type ('Straight', 'Curve', etc.) for each survey point.

        Returns
        -------
        np.ndarray
            Section type for each survey point.
        """
        return self.survey_section_type

    def get_survey_section_no(self):
        """
        Get section number for each survey point.

        Returns
        -------
        np.ndarray
            Section number for each survey point.
        """
        return self.survey_section_no

    def get_survey_section_kp_mod(self):
        """
        Get section-modified KP for each survey point.

        Returns
        -------
        np.ndarray
            Section-modified KP for each survey point.
        """
        return self.survey_section_kp_mod

    def get_survey_section_easting_mod(self):
        """
        Get section-modified easting coordinates for each survey point.

        Returns
        -------
        np.ndarray
            Section-modified easting coordinates for each survey point.
        """
        return self.survey_section_easting_mod

    def get_survey_section_northing_mod(self):
        """
        Get section-modified northing coordinates for each survey point.

        Returns
        -------
        np.ndarray
            Section-modified northing coordinates for each survey point.
        """
        return self.survey_section_northing_mod

    def get_survey_feature(self):
        """
        Get feature label (e.g., 'PWMD', 'LBMD', 'ILT') for each survey point.

        Returns
        -------
        np.ndarray
            Feature label for each survey point.
        """
        return self.survey_feature

    def get_survey_design_route_curve_radius(self):
        """
        Get design route curve radius for each survey point.

        Returns
        -------
        np.ndarray
            Design route curve radius for each survey point.
        """
        return self.survey_design_route_curve_radius

    def get_survey_actual_route_curve_radius(self):
        """
        Get fitted curve radius for each survey point.

        Returns
        -------
        np.ndarray
            Fitted curve radius for each survey point.
        """
        return self.survey_actual_route_curve_radius

    def get_survey_group_section_no(self):
        """
        Get group section number for each survey point.

        Returns
        -------
        np.ndarray
            Group section number for each survey point.
        """
        return self.survey_group_section_no

    def get_survey_group_section_type(self):
        """
        Get group section type for each survey point.

        Returns
        -------
        np.ndarray
            Group section type for each survey point.
        """
        return self.survey_group_section_type

    def get_survey_group_section_kp_mod(self):
        """
        Get group section-modified KP for each survey point.

        Returns
        -------
        np.ndarray
            Group section-modified KP for each survey point.
        """
        return self.survey_group_section_kp_mod

    def get_survey_group_section_easting_mod(self):
        """
        Get group section-modified easting coordinates for each survey point.

        Returns
        -------
        np.ndarray
            Group section-modified easting coordinates for each survey point.
        """
        return self.survey_group_section_easting_mod

    def get_survey_group_section_northing_mod(self):
        """
        Get group section-modified northing coordinates for each survey point.

        Returns
        -------
        np.ndarray
            Group section-modified northing coordinates for each survey point.
        """
        return self.survey_group_section_northing_mod

class OOSDespiker: # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-locals
    """
    This class identifies and removes outlier values from survey data using a rolling window
    sigma-clipping algorithm. Outliers are replaced with NaN, preserving the original data
    alignment and group structure.

    Parameters
    ----------
    development : array-like, optional
        Development identifier for each survey point. If not provided, a default value is used.
    survey_type : array-like, optional
        Survey type for each survey point. If not provided, a default value is used.
    pipeline_group : array-like, optional
        Pipeline group for each survey point. If not provided, a default value is used.
    group_section_type : array-like, optional
        Group section type for each survey point. If not provided, a default value is used.
    x : array-like
        Coordinates associated with the signal for each survey point.
        These can be either easting values or arc lengths, depending on context.
    y : array-like
        Signal values for each survey point.
        These can be either northing values or curvatures, depending on context.
    window : int, optional
        Size of the rolling window for sigma-clipping (default: 11).
    sigma : float, optional
        Sigma threshold for outlier detection (default: 3.0).
    """
    def __init__(
            self,
            *,
            development=None,
            survey_type=None,
            pipeline_group=None,
            group_section_type=None,
            y,
            window=11,
            sigma=3.0
        ):
        """
        Initialize an OOSAnonymisation object with route and survey data.
        """
        # Convert to arrays
        self.y = np.asarray(y)
        self.window = window
        self.sigma = sigma
        if development is None:
            self.development = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.development = np.asarray(development, dtype=object)
        if survey_type is None:
            self.survey_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.survey_type = np.asarray(survey_type, dtype=object)
        if pipeline_group is None:
            self.pipeline_group = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.pipeline_group = np.asarray(pipeline_group, dtype=object)
        if group_section_type is None:
            self.group_section_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.group_section_type = np.asarray(group_section_type, dtype=object)
        # Initialize group-related attributes
        self.group_tuples = list(zip(
            self.development,
            self.survey_type,
            self.pipeline_group,
            self.group_section_type,
        ))
        self.unique_groups = sorted(set(self.group_tuples), key=self.group_tuples.index)
        # Call the processing function
        self._process()

    def _process(self):
        """
        Despike outliers in using a rolling window sigma-clipping algorithm.
        Outliers are replaced with NaN.
        """
        def sigma_clip_filter_mean(values):
            center = values[len(values) // 2]
            win_mean = np.nanmean(values)
            win_std = np.nanstd(values)
            if win_std == 0 or np.isnan(win_std):
                return center
            if abs(center - win_mean) > self.sigma * win_std:
                return win_mean
            return center

        def sigma_clip_filter_nan(values):
            center = values[len(values) // 2]
            win_mean = np.nanmean(values)
            win_std = np.nanstd(values)
            if win_std == 0 or np.isnan(win_std):
                return center
            if abs(center - win_mean) > self.sigma * win_std:
                return np.nan
            return center

        # Initialise despiked arrays
        self.y_despike_mean = np.full_like(self.y, np.nan, dtype=float)
        self.y_despike_nan = np.full_like(self.y, np.nan, dtype=float)

        for group in self.unique_groups:

            # Create mask for current group
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )

            # Get indices and values for the current group
            idx = np.where(mask)[0]
            y_g = self.y[idx]
            if len(y_g) < self.window:
                self.y_despike_mean[idx] = y_g
                continue

            # Apply sigma clipping filter using a rolling window
            y_g_despiked_mean = generic_filter(
                y_g, sigma_clip_filter_mean, size=self.window, mode='nearest'
            )
            y_g_despiked_nan = generic_filter(
                y_g, sigma_clip_filter_nan, size=self.window, mode='nearest'
            )
            self.y_despike_mean[idx] = y_g_despiked_mean
            self.y_despike_nan[idx] = y_g_despiked_nan

    def get_y_despike_mean(self):
        """
        Get the despiked y values (i.e., northings or curvatures) for each survey point.

        Returns
        -------
        np.ndarray
            Despiked y values for each survey point.
        """
        return self.y_despike_mean

    def get_y_despike_nan(self):
        """
        Get the despiked y values (i.e., northings or curvatures) for each survey point.

        Returns
        -------
        np.ndarray
            Despiked y values for each survey point.
        """
        return self.y_despike_nan

class OOSCurvature: # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-locals
    """
    Computes geometric curvature, arc length, and tangent angle for grouped pipeline survey data.

    This class calculates the arc length, tangent angle, and curvature of the pipeline defined by
    easting and northing coordinates, for each group section. The results are aligned with the
    original data and are useful for geometric analysis and further signal processing.

    Parameters
    ----------
    development : array-like, optional
        Development identifier for each survey point. If not provided, a default value is used.
    survey_type : array-like, optional
        Survey type for each survey point. If not provided, a default value is used.
    pipeline_group : array-like, optional
        Pipeline group for each survey point. If not provided, a default value is used.
    group_section_type : array-like, optional
        Group section type for each survey point. If not provided, a default value is used.
    x : array-like
        These can be either eastings or anonymised eastings, depending on context.
    y : array-like
        These can be either northings or anonymised northings, depending on context.
    """
    def __init__(
            self,
            *,
            development=None,
            survey_type=None,
            pipeline_group=None,
            group_section_type=None,
            x,
            y
        ):
        """
        Initialize an OOSAnonymisation object with route and survey data.
        """
        # Convert to arrays
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        if development is None:
            self.development = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.development = np.asarray(development, dtype=object)
        if survey_type is None:
            self.survey_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.survey_type = np.asarray(survey_type, dtype=object)
        if pipeline_group is None:
            self.pipeline_group = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.pipeline_group = np.asarray(pipeline_group, dtype=object)
        if group_section_type is None:
            self.group_section_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.group_section_type = np.asarray(group_section_type, dtype=object)
        # Initialize group-related attributes
        self.group_tuples = list(zip(
            self.development,
            self.survey_type,
            self.pipeline_group,
            self.group_section_type,
        ))
        self.unique_groups = sorted(set(self.group_tuples), key=self.group_tuples.index)        # Initialize attributes
        self.arc_length = np.full(self.x.shape[0], np.nan, dtype=float)
        self.angle = np.full(self.x.shape[0], np.nan, dtype=float)
        self.curvature = np.full(self.x.shape[0], np.nan, dtype=float)
        # Call the processing function
        self._process()

    def _process(self):
        """
        Calculate the arc length, angle and curvature of the pipeline defined by easting and
        northing coordinates, for each group section. The result is aligned with the original
        data. Central differences are used within the central points, and forward and backward
        differences are used at the first and last point of each group.

        It also calculates the arc length and angle.
        """
        # Re-initialise arc length and curvature array
        self.arc_length = np.full(self.x.shape[0], np.nan, dtype=float)
        self.angle = np.full(self.x.shape[0], np.nan, dtype=float)
        self.curvature = np.full(self.x.shape[0], np.nan, dtype=float)
        # Create group tuples
        group_tuples = list(zip(
            self.development,
            self.survey_type,
            self.pipeline_group,
            self.group_section_type
        ))
        unique_groups = set(group_tuples)
        # Iterate over each unique group
        for group in unique_groups:
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )
            idx = np.where(mask)[0]
            # Coordinate vector
            if len(idx) < 3:
                continue  # Not enough points to compute curvature
            x = self.x[idx]
            y = self.y[idx]
            coords = np.column_stack((x ,y))

            # Remove consecutive duplicate points
            diffs = np.diff(coords, axis=0)
            nonzero = np.any(diffs != 0, axis=1)
            keep = np.insert(nonzero, 0, True)  # Always keep the first point

            coords_dedup = coords[keep]
            x_dedup = coords_dedup[:, 0]
            n = len(x_dedup)

            curvature_full_dedup = np.full(n, np.nan, dtype=float)
            angle_full_dedup = np.full(n, np.nan, dtype=float)
            arc_length_full_dedup = np.full(n, np.nan, dtype=float)

            if n < 3:
                # Not enough points after deduplication
                curvature_full = np.full(len(idx), np.nan, dtype=float)
                angle_full = np.full(len(idx), np.nan, dtype=float)
                arc_length_full = np.full(len(idx), np.nan, dtype=float)
                self.arc_length[idx] = arc_length_full
                self.angle[idx] = angle_full
                self.curvature[idx] = curvature_full
                continue

            # Forward difference for the first point
            v1_f = coords_dedup[1] - coords_dedup[0]
            v2_f = coords_dedup[2] - coords_dedup[1]
            norm_v1_f = np.linalg.norm(v1_f)
            norm_v2_f = np.linalg.norm(v2_f)
            ds_f = norm_v1_f
            tan1_f = v1_f / norm_v1_f if norm_v1_f != 0 else np.zeros_like(v1_f)
            tan2_f = v2_f / norm_v2_f if norm_v2_f != 0 else np.zeros_like(v2_f)
            cross_f = tan1_f[0] * tan2_f[1] - tan1_f[1] * tan2_f[0]
            arc_length_full_dedup[0] = 0.0 # ds_f
            angle_full_dedup[0] = 0.0 # np.arctan2(v1_f[1], v1_f[0])
            curvature_full_dedup[0] = 0.0 # cross_f / ds_f if ds_f != 0 else 0.0

            # Central differences for internal points
            p_prev = coords_dedup[:-2]
            p_curr = coords_dedup[1:-1]
            p_next = coords_dedup[2:]
            v1 = p_curr - p_prev
            v2 = p_next - p_curr
            norm_v1 = np.linalg.norm(v1, axis=1)
            norm_v2 = np.linalg.norm(v2, axis=1)
            with np.errstate(divide='ignore', invalid='ignore'):
                tan1 = np.divide(v1, norm_v1[:, None],
                                 out=np.zeros_like(v1), where=norm_v1[:, None] != 0)
                tan2 = np.divide(v2, norm_v2[:, None],
                                 out=np.zeros_like(v2), where=norm_v2[:, None] != 0)
                ds = 0.5 * (norm_v1 + norm_v2)
                cross = tan1[:, 0] * tan2[:, 1] - tan1[:, 1] * tan2[:, 0]
                curvature = np.divide(cross, ds, out=np.zeros_like(cross), where=ds != 0)
            arc_length_full_dedup[1:-1] = ds
            angle_full_dedup[1:-1] = np.arctan2(v2[:, 1], v2[:, 0])
            curvature_full_dedup[1:-1] = curvature

            # Backward difference for the last point
            v1_b = coords_dedup[-2] - coords_dedup[-3]
            v2_b = coords_dedup[-1] - coords_dedup[-2]
            norm_v1_b = np.linalg.norm(v1_b)
            norm_v2_b = np.linalg.norm(v2_b)
            ds_b = norm_v2_b
            tan1_b = v1_b / norm_v1_b if norm_v1_b != 0 else np.zeros_like(v1_b)
            tan2_b = v2_b / norm_v2_b if norm_v2_b != 0 else np.zeros_like(v2_b)
            cross_b = tan1_b[0] * tan2_b[1] - tan1_b[1] * tan2_b[0]
            arc_length_full_dedup[-1] = 0.0 # ds_b
            angle_full_dedup[-1] = 0.0 # np.arctan2(v2_b[1], v2_b[0])
            curvature_full_dedup[-1] = 0.0 # cross_b / ds_b if ds_b != 0 else 0.0

            # Cumulative arc length
            arc_length_cumsum = np.cumsum(arc_length_full_dedup)

            # Map de-duplicated results back to original indices
            curvature_full = np.full(len(idx), np.nan, dtype=float)
            angle_full = np.full(len(idx), np.nan, dtype=float)
            arc_length_full = np.full(len(idx), np.nan, dtype=float)
            orig_idx_dedup = np.where(keep)[0]
            curvature_full[orig_idx_dedup] = curvature_full_dedup
            angle_full[orig_idx_dedup] = angle_full_dedup
            arc_length_full[orig_idx_dedup] = arc_length_cumsum

            # Update survey group attributes
            self.arc_length[idx] = arc_length_full
            self.angle[idx] = angle_full
            self.curvature[idx] = curvature_full

    def get_arc_length(self):
        """
        Get the arc length of the pipeline.

        Returns
        -------
        np.ndarray
            Arc length for each survey point.
        """
        return self.arc_length

    def get_angle(self):
        """
        Get the tangent angle of the pipeline.

        Returns
        -------
        np.ndarray
            Tangent angle for each survey point.
        """
        return self.angle

    def get_curvature(self):
        """
        Get the curvature of the pipeline.

        Returns
        -------
        np.ndarray
            Curvature for each survey point.
        """
        return self.curvature

class FFTSmoother: # pylint: disable=too-many-arguments, too-many-instance-attributes, too-many-locals
    """
    Class to perform FFT smoothing and spectral analysis on the pipeline survey data, grouped by
    (development, survey type, pipeline group, group section type).
    
    Parameters
    ----------
    development : array-like, optional
        Development identifier for each survey point. If not provided, a default value is used.
    survey_type : array-like, optional
        Survey type for each survey point. If not provided, a default value is used.
    pipeline_group : array-like, optional
        Pipeline group for each survey point. If not provided, a default value is used.
    group_section_type : array-like, optional
        Group section type for each survey point. If not provided, a default value is used.
    x : array_like, mandatory
        Coordinates associated with the signal for each survey point.
        These can be either anonymised easting values or arc lengths, depending on context.
    y : array_like, mandatory
        Signal values for each survey point.
        These can be either anonymised northing values or curvatures, depending on context.
    cutoff : float or None, mandatory
        Wavelength or curvature cutoff for FFT filtering. If None, no filtering is applied.
    """
    def __init__(
            self,
            *,
            development=None,
            survey_type=None,
            pipeline_group=None,
            group_section_type=None,
            x,
            y,
            cutoff
        ):
        """
        Initialize an OOSAnonymisation object with route and survey data.
        """
        # Convert to arrays
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        if development is None:
            self.development = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.development = np.asarray(development, dtype=object)
        if survey_type is None:
            self.survey_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.survey_type = np.asarray(survey_type, dtype=object)
        if pipeline_group is None:
            self.pipeline_group = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.pipeline_group = np.asarray(pipeline_group, dtype=object)
        if group_section_type is None:
            self.group_section_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.group_section_type = np.asarray(group_section_type, dtype=object)
        # Initialize group-related attributes
        self.group_tuples = list(zip(
            self.development,
            self.survey_type,
            self.pipeline_group,
            self.group_section_type,
        ))
        self.unique_groups = sorted(set(self.group_tuples), key=self.group_tuples.index)
        self.cutoff = cutoff
        # Initialize _filter attributes
        self.y_smooth = np.full_like(self.y, np.nan, dtype=float)
        self.freqs = np.full_like(self.y, np.nan, dtype=float)
        self.fft = np.full_like(self.y, np.nan, dtype=complex)
        self.freqs_raw = np.full_like(self.y, np.nan, dtype=float)
        self.fft_raw = np.full_like(self.y, np.nan, dtype=complex)
        # Initialize _welch attributes
        self.psd_development = []
        self.psd_survey_type = []
        self.psd_pipeline_group = []
        self.psd_group_section_type = []
        self.psd_freqs = []
        self.psd_vals = []
        # Initialize _reconstruct_coordinates_from_curvature attributes
        self.x_recon = np.full_like(self.x, np.nan, dtype=float)
        self.y_recon = np.full_like(self.x, np.nan, dtype=float)
        # Call the processing functions
        self._filter()
        self._welch()
        self._reconstruct_coordinates_from_curvature()

    def _filter(self):
        """
        Apply FFT low-pass filtering to each group, deduplicating (x_g, y_g) pairs within a group
        before filtering.
        The smoothed value is mapped back to all original indices for each unique pair, ensuring
        identical pairs get identical y_smooth values.

        This method also stores the raw (unfiltered) FFT and frequency values for each group in
        the attributes `fft_raw` and `freqs_raw`.

        Sets the following attributes:
        ------------------------------
        y_smooth : ndarray
            Array of filtered y-values, aligned with input y
            (NaN for points not in a group).
        freqs : ndarray
            Array of filtered frequency values, aligned with input y
            (NaN for points not in a group).
        fft : ndarray
            Array of filtered FFT values, aligned with input y
            (NaN for points not in a group).
        freqs_raw : ndarray
            Array of raw (unfiltered) frequency values, aligned with input y
            (NaN for points not in a group).
        fft_raw : ndarray
            Array of raw (unfiltered) FFT values, aligned with input y
            (NaN for points not in a group).
        """
        for group in self.unique_groups:

            # Get the mask for the current group
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )

            # Get the data for the current group
            x_g = self.x[mask]
            y_g = self.y[mask]

            # Deduplicate (x_g, y_g) pairs
            pairs = np.column_stack((x_g, y_g))

            # Discard rows with NaN in either column
            not_nan_mask = ~np.isnan(pairs).any(axis=1)
            pairs_clean = pairs[not_nan_mask]
            x_g_clean = x_g[not_nan_mask]
            y_g_clean = y_g[not_nan_mask]
            if len(x_g_clean) == 0:
                continue
            _, unique_idx, inverse_idx = np.unique(
                pairs_clean, axis=0, return_index=True, return_inverse=True
            )
            x_g_unique = x_g_clean[unique_idx]
            y_g_unique = y_g_clean[unique_idx]

            # FFT filtering on unique pairs
            if len(x_g_unique) < 2:
                # Not enough points to filter
                y_smooth_unique = y_g_unique.copy()
                freqs_g = np.full_like(x_g_unique, np.nan, dtype=float)
                fft_g = np.full_like(x_g_unique, np.nan, dtype=complex)
                fft_vals_g = np.full_like(x_g_unique, np.nan, dtype=complex)
            else:
                dx_g = np.mean(np.diff(x_g_unique))
                if dx_g == 0:
                    continue
                fs_g = 1 / dx_g
                fft_vals_g = fft(y_g_unique)
                freqs_g = fftfreq(len(x_g_unique), 1 / fs_g)
                fft_g = np.copy(fft_vals_g)
                if self.cutoff is not None:
                    fft_g[np.abs(freqs_g) > (1 / self.cutoff)] = 0
                y_smooth_unique = np.real(ifft(fft_g))

            # Map smoothed values back to all original indices
            y_smooth_g = np.full_like(y_g, np.nan, dtype=float)
            y_smooth_g[not_nan_mask] = y_smooth_unique[inverse_idx]
            freqs_g_full = np.full_like(x_g, np.nan, dtype=float)
            fft_g_full = np.full_like(x_g, np.nan, dtype=complex)
            fft_raw_full = np.full_like(x_g, np.nan, dtype=complex)
            freqs_raw_full = np.full_like(x_g, np.nan, dtype=float)

            # For each original index, assign the frequency and fft value from the unique pair
            for i, idx in enumerate(inverse_idx):
                if len(freqs_g) > idx:
                    freqs_g_full[i] = freqs_g[idx]
                    fft_g_full[i] = fft_g[idx]
                    freqs_raw_full[i] = freqs_g[idx]
                    fft_raw_full[i] = fft_vals_g[idx]

            # Sort by ascending frequency
            sort_idx = np.argsort(freqs_g_full)
            freqs_g_full = freqs_g_full[sort_idx]
            fft_g_full = fft_g_full[sort_idx]
            freqs_raw_full = freqs_raw_full[sort_idx]
            fft_raw_full = fft_raw_full[sort_idx]

            # Assign values
            self.y_smooth[mask] = y_smooth_g
            self.freqs[mask] = freqs_g_full
            self.fft[mask] = fft_g_full
            self.freqs_raw[mask] = freqs_raw_full
            self.fft_raw[mask] = fft_raw_full

    def _welch(self, nperseg=256):
        """
        Compute the Power Spectral Density (PSD) using Welch's method for each group.

        This method estimates the distribution of signal power as a function of wavelength.
        By plotting the PSD against wavelength (1/frequency), you can visually identify
        which wavelength bands contain significant noise or signal energy. 
        Typically, noise appears at shorter wavelengths (higher frequencies), while meaningful
        signal features are often found at longer wavelengths. Use this information to select
        an appropriate cutoff wavelength for filtering out noise.

        Sets the following attributes:
        ------------------------------
        psd_development : list of ndarray
            For each group, an array filled with the development value,
            same length as the PSD frequency array.
        psd_survey_type : list of ndarray
            For each group, an array filled with the survey type value,
            same length as the PSD frequency array.
        psd_pipeline_group : list of ndarray
            For each group, an array filled with the pipeline group value,
            same length as the PSD frequency array.
        psd_group_section_type : list of ndarray
            For each group, an array filled with the group section type value,
            same length as the PSD frequency array.
        psd_freqs : list of ndarray
            List of frequency arrays for each group.
        psd_vals : list of ndarray
            List of PSD arrays for each group.
        """
        for group in self.unique_groups:

            # Get the mask for the current group
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )
            # Get the data for the current group
            x_g = self.x[mask]
            y_g = self.y[mask]
            if len(x_g) < 2 or len(y_g) < 2:
                continue

            # Remove NaN values
            x_g_valid = x_g[~np.isnan(x_g)]
            y_g_valid = y_g[~np.isnan(y_g)]

            # Only keep indices where both x_g and y_g are valid (not NaN)
            valid_mask = ~np.isnan(x_g) & ~np.isnan(y_g)
            x_g_valid = x_g[valid_mask]
            y_g_valid = y_g[valid_mask]
            if len(x_g_valid) < 2 or len(y_g_valid) < 2:
                continue
            dx_g = np.mean(np.diff(x_g_valid))
            if dx_g == 0 or np.isnan(dx_g):
                continue
            fs_g = 1 / dx_g

            # Compute Welch's method
            nperseg_eff = min(nperseg, len(y_g_valid))
            f_welch, pxx_welch = welch(y_g_valid, fs=fs_g, nperseg=nperseg_eff)

            # Store the results
            self.psd_development.append(group[0])
            self.psd_survey_type.append(group[1])
            self.psd_pipeline_group.append(group[2])
            self.psd_group_section_type.append(group[3])
            self.psd_freqs.append(f_welch)
            self.psd_vals.append(pxx_welch)

    def _reconstruct_coordinates_from_curvature(self):
        """
        Reconstruct eastings and northings from arc length and smoothed curvature for each group.
        The result is aligned with self.x and self.y_smooth.
        Sets:
            self.x_recon : ndarray
                Reconstructed eastings (aligned with self.x, NaN for points not in a group)
            self.y_recon : ndarray
                Reconstructed northings (aligned with self.x, NaN for points not in a group)
        """
        for group in self.unique_groups:

            # Get the mask for the current group
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )

            # Get the arc length and curvature
            s = self.x[mask]
            kappa = self.y_smooth[mask]

            # Remove NaN from arc length and curvature
            valid = ~np.isnan(s) & ~np.isnan(kappa)
            if np.sum(valid) < 2:
                continue
            s = s[valid]
            kappa = kappa[valid]

            # Ensure s is sorted
            idx_sort = np.argsort(s)
            s = s[idx_sort]
            ds = np.diff(s, prepend=s[0])
            kappa = kappa[idx_sort]

            # Shift the position of ds and kappa +1 position for dataframe alignment purposes
            ds_angle = np.roll(ds, 1)
            ds_angle[0] = 0.0
            kappa[0] = 0.0
            kappa = np.roll(kappa, 1)
            kappa[0] = 0.0

            # Integrate curvature to get tangent angle
            theta = np.cumsum(kappa * ds_angle)

            # Integrate cos(theta), sin(theta) to get coordinates
            x_rec = np.cumsum(np.cos(theta) * ds)
            y_rec = np.cumsum(np.sin(theta) * ds)

            # Align so the line from the second point to the one before last is horizontal
            dx = x_rec[-2] - x_rec[1]
            dy = y_rec[-2] - y_rec[1]
            angle = -np.arctan2(dy, dx)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            x_rot = (x_rec - x_rec[1]) * cos_a - (y_rec - y_rec[1]) * sin_a + x_rec[1]
            y_rot = (x_rec - x_rec[1]) * sin_a + (y_rec - y_rec[1]) * cos_a

            # Place back into full arrays
            group_indices = np.where(mask)[0][valid][idx_sort]
            self.x_recon[group_indices] = x_rot
            self.y_recon[group_indices] = y_rot

    def get_y_smooth(self):
        """
        Get the FFT smoothed y values.

        Returns
        -------
        np.ndarray
            FFT smoothed y values for each survey point.
        """
        return self.y_smooth

    def get_freqs(self):
        """
        Get the filtered frequency values.

        Returns
        -------
        np.ndarray
            Filtered frequency values for each survey point.
        """
        return self.freqs

    def get_fft(self):
        """
        Get the filtered FFT values.

        Returns
        -------
        np.ndarray
            Filtered FFT values for each survey point.
        """
        return self.fft

    def get_freqs_raw(self):
        """
        Get the raw (unfiltered) frequency values.

        Returns
        -------
        np.ndarray
            Raw frequency values for each survey point.
        """
        return self.freqs_raw

    def get_fft_raw(self):
        """
        Get the raw (unfiltered) FFT values.

        Returns
        -------
        np.ndarray
            Raw FFT values for each survey point.
        """
        return self.fft_raw

    def get_psd_development(self):
        """
        Get the PSD development values.

        Returns
        -------
        list
            PSD development values for each group.
        """
        return self.psd_development

    def get_psd_survey_type(self):
        """
        Get the PSD survey type values.

        Returns
        -------
        list
            PSD survey type values for each group.
        """
        return self.psd_survey_type

    def get_psd_pipeline_group(self):
        """
        Get the PSD pipeline group values.

        Returns
        -------
        list
            PSD pipeline group values for each group.
        """
        return self.psd_pipeline_group

    def get_psd_group_section_type(self):
        """
        Get the PSD group section type values.

        Returns
        -------
        list
            PSD group section type values for each group.
        """
        return self.psd_group_section_type

    def get_psd_freqs(self):
        """
        Get the PSD frequency arrays.

        Returns
        -------
        list
            PSD frequency arrays for each group.
        """
        return self.psd_freqs

    def get_psd_vals(self):
        """
        Get the PSD values arrays.

        Returns
        -------
        list
            PSD values arrays for each group.
        """
        return self.psd_vals

    def get_x_recon(self):
        """
        Get the reconstructed x (easting) coordinates.

        Returns
        -------
        np.ndarray
            Reconstructed x coordinates for each survey point.
        """
        return self.x_recon

    def get_y_recon(self):
        """
        Get the reconstructed y (northing) coordinates.

        Returns
        -------
        np.ndarray
            Reconstructed y coordinates for each survey point.
        """
        return self.y_recon

class GaussianSmoother:
    """
    Class to perform Gaussian kernel smoothing on the pipeline survey, grouped by
    (development, survey type, pipeline group, group section type).

    Parameters
    ----------
    development : array-like, optional
        Development identifier for each survey point. If not provided, a default value is used.
    survey_type : array-like, optional
        Survey type for each survey point. If not provided, a default value is used.
    pipeline_group : array-like, optional
        Pipeline group for each survey point. If not provided, a default value is used.
    group_section_type : array-like, optional
        Group section type for each survey point. If not provided, a default value is used.
    x : array-like
        Anonymised eastings for each survey point.
    y : array-like
        Anonymised northings for each survey point.
    bandwidth : float
        Bandwidth for the Gaussian kernel.
    """
    def __init__(
        self,
        *,
        development=None,
        survey_type=None,
        pipeline_group=None,
        group_section_type=None,
        x,
        y,
        bandwidth
    ):
        # Initialize GaussianSmoother attributes
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.bandwidth = bandwidth
        if development is None:
            self.development = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.development = np.asarray(development, dtype=object)
        if survey_type is None:
            self.survey_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.survey_type = np.asarray(survey_type, dtype=object)
        if pipeline_group is None:
            self.pipeline_group = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.pipeline_group = np.asarray(pipeline_group, dtype=object)
        if group_section_type is None:
            self.group_section_type = np.full(self.y.size, 'Predefined', dtype=object)
        else:
            self.group_section_type = np.asarray(group_section_type, dtype=object)
        # Initialize group-related attributes
        self.group_tuples = list(zip(
            self.development,
            self.survey_type,
            self.pipeline_group,
            self.group_section_type,
        ))
        self.unique_groups = sorted(set(self.group_tuples), key=self.group_tuples.index)
        self.y_smooth = np.full_like(self.y, np.nan, dtype=float)
        # Call the processing function
        self._process()

    def _process(self):
        """
        Apply Gaussian kernel smoothing to each group, using bandwidth.

        The smoothing is performed group-wise, using the same grouping as fft_filter.
        The result is stored in self.y_smooth, aligned with input y.
        """
        # Compute Gaussian kernel
        std = 0.37
        b_scaled = self.bandwidth / std

        for group in self.unique_groups:

            # Create mask for current group
            mask = (
                (self.development == group[0]) &
                (self.survey_type == group[1]) &
                (self.pipeline_group == group[2]) &
                (self.group_section_type == group[3])
            )

            # Extract group data
            x_g = self.x[mask]
            y_g = self.y[mask]

            # Initialize smoothed output
            y_smooth_g = np.empty_like(y_g, dtype=float)
            for i in range(x_g.size):
                x_left = max(x_g[0], x_g[i] - 2 * b_scaled)
                x_right = min(x_g[i] + 2 * b_scaled, x_g[-1])
                idx = np.where((x_g >= x_left) & (x_g <= x_right))[0]
                xgk = x_g[idx]
                ygk = y_g[idx]
                weight = (
                    1 / ((2 * np.pi)**0.5 * std) *
                    np.exp(-0.5 * (np.abs(xgk - x_g[i]) / b_scaled / std)**2)
                )
                sumygk = np.dot(weight, ygk)
                sumweight = np.sum(weight)
                if sumweight != 0:
                    y_smooth_g[i] = sumygk / sumweight
                elif ygk.size > 0:
                    y_smooth_g[i] = ygk[0]
                else:
                    y_smooth_g[i] = np.nan  # or 0, or skip, depending on your needs
            self.y_smooth[mask] = y_smooth_g

    def get_y_smooth(self):
        """
        Get the smoothed y values (i.e., northings) for each survey point.

        Returns
        -------
        np.ndarray
            Smoothed y values for each survey point.
        """
        return self.y_smooth
