from typing import Dict
import numpy as np
import pandas as pd
import pvlib

from sunpeek.common import unit_uncertainty as uu
from sunpeek.common.unit_uncertainty import Q


# from sunpeek.components import Array


def calc_shading_aoi_elevation(internal_shading_fraction: pd.Series,
                               sun_apparent_elevation: pd.Series,
                               aoi: pd.Series = None,
                               max_aoi_shadow: Q = None,
                               min_elevation_shadow: Q = None,
                               ) -> pd.Series:
    """Calculate shading effects caused by large angles of incidence or low sun elevation.

    Parameters
    ----------
    internal_shading_fraction : pd.Series
        Row-to-row shading fraction.
    sun_apparent_elevation : pd.Series
        Sun apparent elevation (altitude) angle in radians
    aoi : pd.Series, optional
        The angle of incidence (AOI) between the normal vector of the collector plane and the sun-beam vector.
    max_aoi_shadow : Quantity, optional
        Array is considered shadowed if aoi is greater than `max_aoi_shadow`. See array.max_aoi_shadow.
    min_elevation_shadow : Quantity, optional
        Array is considered shadowed if sun apparent elevation is less than `min_elevation_shadow`. See array.min_elevation_shadow.

    Returns
    -------
    is_shadowed : pd.Series.
        Boolean, True if the array is to be considered as affected by beam shading, taking all modeled effects
        into account (internal shading, minimum sun elevation angle, maximum allowed aoi).
    """
    is_not_shadowed = np.ones(len(internal_shading_fraction))
    # Maximum angle of incidence
    if max_aoi_shadow is not None:
        if aoi is None:
            raise TypeError('Angle of incidence (aoi) is a required argument if also max_aoi_shadow is specified.')
        is_not_shadowed *= (aoi.pint.m_as('deg').to_numpy() <= max_aoi_shadow.m_as('deg'))
    # Minimum apparent sun elevation
    if min_elevation_shadow is not None:
        is_not_shadowed *= (sun_apparent_elevation.pint.m_as('deg').to_numpy() >= min_elevation_shadow.m_as('deg'))

    is_not_shadowed *= (internal_shading_fraction == 0)
    is_shadowed = uu.to_s(1 - is_not_shadowed, 'dimensionless')

    return is_shadowed


# ToDo Remove
# def calc_masking_angle_05(array: Array) -> Q | None:
def calc_masking_angle_05(array) -> Q | None:
    """Calculate diffuse radiation masking angle of an array at slant height 0.5.

    Returns
    -------
    masking_angle : Q
        This is the static masking angle for diffuse radiation, computed as shadow angle at collector slant height 0.5.
        Return None if the array has no valid collector.
    """

    # if (array.collector is None) or isinstance(array.collector, UninitialisedCollector:
    if array.collector is None:
        return None

    geom = calc_sloped_shading_geometry(ground_tilt=array.ground_tilt,
                                        ground_azimuth=array.ground_azim,
                                        collector_tilt=array.tilt,
                                        collector_azimuth=array.azim,
                                        collector_row_spacing=array.row_spacing,
                                        collector_gross_length=array.collector.gross_length)

    A_prime = geom['a_prime']
    S = array.row_spacing
    beta = geom['beta']
    theta = geom['theta']

    # calc D and H for conditions where shadow hits slant height equals 0.5 (half of slant height)
    D = S * np.cos(theta) - A_prime * np.cos(beta) + A_prime * 0.5 * np.cos(beta)
    H = A_prime * np.sin(beta) - S * np.sin(theta) - A_prime * 0.5 * np.sin(beta)

    masking_angle = np.arctan(H / D)

    return masking_angle


def calc_BanyAppelbaum_shading(collector_tilt: Q,
                               collector_azimuth: Q,
                               collector_gross_length: Q,
                               collector_row_spacing: Q,
                               sun_azimuth: pd.Series,
                               sun_apparent_elevation: pd.Series,
                               ground_tilt: Q = Q(0, 'deg'),
                               aoi: pd.Series = None,
                               max_aoi_shadow: Q = None,
                               min_elevation_shadow: Q = None,
                               ) -> Dict[str, pd.Series]:
    """Calculate internal shading (row-to-row shading), considering also max aoi and min elevation effects.

    Parameters
    ----------
    collector_tilt : Quantity
        Tilt angle of collectors. Same as array.tilt.
    collector_azimuth : Quantity
        Azimuth angle of collectors. Same as array.azim.
    collector_gross_length : Quantity
        Gross length of collectors. Same as array.collector.gross_length.
    collector_row_spacing : Quantity
        The spacing between adjacent rows of collectors, measured along the ground surface.
        If the ground is tilted, this is not the same as the horizontal distance. Same as array.row_spacing.
    sun_azimuth : pd.Series
        Sun azimuth angle in radians
    sun_apparent_elevation : pd.Series
        Apparent sun elevation (altitude) angle in radians
    ground_tilt : Quantity, optional
        Tilt angle of sloped ground.
    aoi : pd.Series, optional
        The angle of incidence (AOI) between the normal vector of the collector plane and the sun-beam vector.
    max_aoi_shadow : Quantity, optional
        Array is considered shadowed if aoi is greater than `max_aoi_shadow`. See array.max_aoi_shadow.
    min_elevation_shadow : Quantity, optional
        Array is considered shadowed if sun apparent elevation is less than `min_elevation_shadow`. See array.min_elevation_shadow.

    Returns
    -------
    Dict with str keys and pint-pandas Series as values:
    is_shadowed : pd.Series
        Boolean, True if the array is to be considered as affected by beam shading, taking all modeled effects
        into account (internal shading, minimum sun elevation angle, maximum allowed aoi).
    internal_shading_fraction : pd.Series
        Float between 0 and 1. Degree of shading of the collectors due to row-to-row shading,
        from not shaded (0) to completely shaded (1).
    """

    sf = calc_BanyAppelbaum_shading_fraction(
        collector_tilt=collector_tilt,
        collector_azimuth=collector_azimuth,
        collector_gross_length=collector_gross_length,
        collector_row_spacing=collector_row_spacing,
        ground_tilt=ground_tilt,
        sun_azimuth=sun_azimuth,
        sun_apparent_elevation=sun_apparent_elevation)

    # Treat sun behind collector or below horizon
    sun_behind_coll = _check_sun_behind_collector(collector_tilt, collector_azimuth,
                                                  sun_apparent_elevation, sun_azimuth)
    sun_below_horizon = (sun_apparent_elevation.pint.m_as('deg') <= 0).to_numpy()
    no_sun = sun_behind_coll | sun_below_horizon
    sf[no_sun] = 1

    is_shadowed = calc_shading_aoi_elevation(internal_shading_fraction=sf,
                                             sun_apparent_elevation=sun_apparent_elevation,
                                             aoi=aoi,
                                             max_aoi_shadow=max_aoi_shadow,
                                             min_elevation_shadow=min_elevation_shadow)

    return {'internal_shading_fraction': sf,
            'is_shadowed': is_shadowed,
            }


def calc_BanyAppelbaum_shading_fraction(collector_tilt: Q,
                                        collector_azimuth: Q,
                                        collector_gross_length: Q,
                                        collector_row_spacing: Q,
                                        sun_azimuth: pd.Series,
                                        sun_apparent_elevation: pd.Series,
                                        ground_tilt: Q = Q(0, 'deg'),
                                        ) -> pd.Series:
    """Calculate internal shading (row-to-row shading) of a collector array.

    Parameters
    ----------
    collector_tilt : Quantity
        Tilt angle of collectors. Same as array.tilt.
    collector_azimuth : Quantity
        Azimuth angle of collectors. Same as array.azim.
    collector_gross_length : Quantity
        Gross length of collectors. Same as array.collector.gross_length.
    collector_row_spacing : Quantity
        The spacing between adjacent rows of collectors, measured along the ground surface.
        If the ground is tilted, this is not the same as the horizontal distance. Same as array.row_spacing.
    sun_azimuth : pd.Series
        Sun azimuth angle in radians
    sun_apparent_elevation : pd.Series
        Apparent sun elevation (altitude) angle in radians
    ground_tilt : Quantity, optional
        Tilt angle of sloped ground.

    Returns
    -------
    Dict with str keys and pint-pandas Series as values:
    internal_shading_fraction : pd.Series
        Float between 0 and 1. Degree of shading of the collectors due to row-to-row shading,
        from not shaded (0) to completely shaded (1).

    Notes
    -----
    This algorithm supports tilted ground, but only if ground and collectors have the same azimuth angle.
    Arbitrary sloped ground is supported by :class:`StrategyInternalShading_SlopedGround`.

    Calculation based on [1].

    internal_shading_fraction calculation taken from ADA implementation:
    https://gitlab.com/sunpeek/sunpeek/uploads/d383e5e42f77516953810e13ac0f42cb/vDP_CollectorField_rd_bT_shaded.m
    This implementation has been extended and takes component.ground_tilt into account.
    Not used in algorithms: component pressure, component humidity / dewpoint
    See also discussion in https://gitlab.com/sunpeek/sunpeek/-/issues/128/

    References
    ----------
    .. [1] Bany, J. and Appelbaum, J. (1987): "The effect of shading on the design of a field of solar collectors",
        Solar Cells 20, p. 201 - 228
        :doi:`https://doi.org/10.1016/0379-6787(87)90029-9`
    """

    beta = collector_tilt.m_as('rad')
    theta = ground_tilt.m_as('rad')

    sb = np.sin(beta)
    cb = np.cos(beta)

    A = collector_gross_length.m_as('m')
    B = collector_row_spacing.m_as('m') * np.sin(theta)
    Hc = A * sb
    b = B / Hc
    D = collector_row_spacing.m_as('m') * np.cos(theta) - A * cb
    d = D / Hc  # Relative collector spacing
    gamma = sun_azimuth.pint.m_as('rad').to_numpy() - collector_azimuth.m_as('rad')
    alpha = sun_apparent_elevation.pint.m_as('rad').to_numpy()

    # sf: shading fraction [0..1]
    cg = np.cos(gamma)
    # Formula (18), nomenclature according to BANY and APPELBAUM (1987),
    # Formula that only works for ground_tilt = 0°
    # sf = 1 - ((d * sb + cb) / (cb + sb * cg / np.tan(alpha)))

    # Formula (29), nomenclature according to BANY and APPELBAUM (1987)
    # Formula that works for ground_tilt = ° and for ground_tilt > 0°
    sf = (1 - b) * (1 - (((d * sb / (1 - b)) + cb) / (cb + (sb * cg / np.tan(alpha)))))
    sf[sf > 1] = 1
    sf[sf < 0] = 0
    sf[np.isnan(sf)] = 1
    internal_shading_fraction = uu.to_s(sf, 'dimensionless')

    return internal_shading_fraction


def calc_sloped_shading(collector_tilt: Q,
                        collector_azimuth: Q,
                        collector_gross_length: Q,
                        collector_row_spacing: Q,
                        ground_tilt: Q,
                        ground_azimuth: Q,
                        sun_azimuth: pd.Series,
                        sun_apparent_elevation: pd.Series,
                        aoi: pd.Series = None,
                        max_aoi_shadow: Q = None,
                        min_elevation_shadow: Q = None,
                        ) -> Dict[str, pd.Series]:
    """Calculate internal shading for sloped ground, and several related virtual sensors.

    Parameters
    ----------
    collector_tilt : Quantity
        For sloped grounds, the collector tilt is the angle beta which is complementary to the angle between
        the collector surface edge and the vertical axis, extending downward to the horizontal.
        It can be measured, e.g., using a plumb line from the highest point on the edge of the collector surface.
        Refer to the documentation of shading on sloped ground for figures and more explanations.
    collector_azimuth : Quantity
        Azimuth angle of collectors. Same as array.azim.
    collector_gross_length : Quantity
        Gross length of collectors. Same as array.collector.gross_length.
    collector_row_spacing : Quantity
        The spacing between adjacent rows of collectors, measured along the ground surface.
        If the ground is tilted, this is not the same as the horizontal distance. Same as array.row_spacing.
    ground_tilt : Quantity
        Tilt angle of sloped ground.
    ground_azimuth : Quantity
        Azimuth angle of sloped ground.
    sun_azimuth: pd.Series
        Sun azimuth angle in radians
    sun_apparent_elevation : pd.Series
        Apparent sun elevation (altitude) angle in radians
    aoi : pd.Series, optional
        The angle of incidence (AOI) between the normal vector of the collector plane and the sun-beam vector.
    max_aoi_shadow : Quantity, optional
        Array is considered shadowed if aoi is greater than `max_aoi_shadow`. See array.max_aoi_shadow.
    min_elevation_shadow : Quantity, optional
        Array is considered shadowed if sun apparent elevation is less than `min_elevation_shadow`.
        See array.min_elevation_shadow.

    Returns
    -------
    Dict with str keys and pint-pandas Series as values.
    is_shadowed : pd.Series
        Boolean, True if the array is to be considered as affected by beam shading, taking all modeled effects
        into account (internal shading, minimum sun elevation angle, maximum allowed aoi).
    internal_shading_fraction : pd.Series
        Floats between 0 and 1. Degree of shading of the collectors due to row-to-row shading,
        from 0 (not shaded) to 1 (completely shaded).

    Notes
    -----
    Calculation based on [1], [2] and [3].

    References
    ----------
    .. [1] Bany, J. and Appelbaum, J. (1987): "The effect of shading on the design of a field of solar collectors",
        Solar Cells 20, p. 201 - 228
        :doi:`https://doi.org/10.1016/0379-6787(87)90029-9`

    .. [2] J. Appelbaum and J. Bany, “Shadow effect of adjacent solar collectors in large scale systems,” Solar Energy,
        vol. 23, no. 6, pp. 497–507, 1979,
        :doi: 10.1016/0038-092X(79)90073-2.

    .. [3] Zauner, P. et al., (2024): "Internal Shading for Fixed-Mounted Collectors on Sloped Ground"
    """

    sf = calc_sloped_shading_fraction(collector_tilt=collector_tilt,
                                      collector_azimuth=collector_azimuth,
                                      collector_gross_length=collector_gross_length,
                                      collector_row_spacing=collector_row_spacing,
                                      ground_tilt=ground_tilt,
                                      ground_azimuth=ground_azimuth,
                                      sun_azimuth=sun_azimuth,
                                      sun_apparent_elevation=sun_apparent_elevation)

    # Treat sun behind collector, below horizon, or behind hill
    aoi_projection_ground = pvlib.irradiance.aoi_projection(
        surface_tilt=ground_tilt.m_as('deg'),
        surface_azimuth=ground_azimuth.m_as('deg'),
        solar_zenith=90 - sun_apparent_elevation.pint.m_as('deg').to_numpy(),
        solar_azimuth=sun_azimuth.pint.m_as('deg').to_numpy())
    sun_behind_coll = _check_sun_behind_collector(collector_tilt, collector_azimuth,
                                                  sun_apparent_elevation, sun_azimuth)
    sun_below_horizon__coll = (sun_apparent_elevation.pint.m_as('deg') <= 0).to_numpy()
    sun_behind_hill = (aoi_projection_ground < 0)
    sun_below_horizon__ground = (sun_apparent_elevation.pint.m_as('deg') <= 0).to_numpy()
    no_sun = sun_behind_coll | sun_below_horizon__coll | sun_behind_hill | sun_below_horizon__ground
    sf[no_sun] = 1

    is_shadowed = calc_shading_aoi_elevation(internal_shading_fraction=sf,
                                             sun_apparent_elevation=sun_apparent_elevation,
                                             aoi=aoi,
                                             max_aoi_shadow=max_aoi_shadow,
                                             min_elevation_shadow=min_elevation_shadow)

    return {'internal_shading_fraction': sf,
            'is_shadowed': is_shadowed,
            }


def _check_sun_behind_collector(collector_tilt: Q,
                                collector_azimuth: Q,
                                sun_apparent_elevation: pd.Series,
                                sun_azimuth: pd.Series,
                                ) -> np.ndarray:
    """Check if sun is behind collector.
    """
    aoi_projection = pvlib.irradiance.aoi_projection(
        surface_tilt=collector_tilt.m_as('deg'),
        surface_azimuth=collector_azimuth.m_as('deg'),
        solar_zenith=90 - sun_apparent_elevation.pint.m_as('deg').to_numpy(),
        solar_azimuth=sun_azimuth.pint.m_as('deg').to_numpy())
    sun_behind_coll = (aoi_projection < 0)

    return sun_behind_coll


def calc_sloped_shading_fraction(collector_tilt: Q,
                                 collector_azimuth: Q,
                                 collector_gross_length: Q,
                                 collector_row_spacing: Q,
                                 ground_tilt: Q,
                                 ground_azimuth: Q,
                                 sun_azimuth: pd.Series,
                                 sun_apparent_elevation: pd.Series,
                                 ) -> pd.Series:
    """Calculate shading fraction of beam shading for parallel collector rows on sloped ground.

    Parameters
    ----------
    Are documented in :func:`calc_sloped_shading`

    Returns
    -------
    sf: pd.Series
        Shading height is height of shaded collector part, measured from bottom to top, up along collector slant height.
        sf is the relative shading fraction, that is: Shadow height divided by collector gross length.

    Notes
    -----
    Note that this calculation allows collector and ground orientation (tilt, azimuth) to be different.
    See also references in `_calc` method.

    References
    ----------
    .. [1] Bany, J. and Appelbaum, J. (1987): "The effect of shading on the design of a field of solar collectors",
        Solar Cells 20, p. 201 - 228
        :doi:`https://doi.org/10.1016/0379-6787(87)90029-9`
    """

    geometry = calc_sloped_shading_geometry(collector_tilt=collector_tilt,
                                            collector_azimuth=collector_azimuth,
                                            collector_gross_length=collector_gross_length,
                                            collector_row_spacing=collector_row_spacing,
                                            ground_tilt=ground_tilt,
                                            ground_azimuth=ground_azimuth)

    gamma_s_rel = sun_azimuth.pint.m_as('rad').to_numpy() - collector_azimuth.m_as('rad')
    alpha = sun_apparent_elevation.pint.m_as('rad').to_numpy()
    s = collector_row_spacing.m_as('meter')

    # Define projections of x and y-coordinate of solar irradiation (collector not included here)
    # See equations (8) and (11) of [1]
    a_prime = geometry['a_prime'].m_as('m')
    beta = geometry['beta'].m_as('rad')
    theta = geometry['theta'].m_as('rad')
    epsilon = geometry['epsilon'].m_as('rad')
    chi = geometry["chi"].m_as('rad')

    # apparent height and distance between collectors
    h = a_prime * np.sin(beta) - s * np.sin(theta)
    d = s * np.cos(theta) - a_prime * np.cos(beta)

    # calculating helper variable te
    upper = np.sin(chi) * d + np.cos(chi) * np.cos(epsilon) * h
    lower = (
            np.sin(chi) * np.cos(gamma_s_rel)
            - np.sin(epsilon) * np.cos(chi) * np.sin(gamma_s_rel)
            + np.tan(alpha) * np.cos(epsilon) * np.cos(chi)
    )
    te = upper / lower

    # calculating shadow height on collector (in azimuth direction)
    dy = te * np.cos(gamma_s_rel) - d
    dz = h - te * (np.tan(alpha) - np.tan(epsilon) * np.sin(gamma_s_rel))
    fe = np.sqrt(dy ** 2 + dz ** 2)

    # calculating shadow fraction
    no_shadow2 = dy < 0
    sf_abs = fe * 1
    sf_abs[no_shadow2] = -fe[no_shadow2]
    sf = sf_abs / a_prime
    sf[sf > 1] = 1
    sf[sf < 0] = 0
    sf[np.isnan(sf)] = 1
    internal_shading_fraction = uu.to_s(sf, 'dimensionless')

    return internal_shading_fraction


def calc_sloped_shading_geometry(collector_tilt: Q,
                                 collector_azimuth: Q,
                                 collector_gross_length: Q,
                                 collector_row_spacing: Q,
                                 ground_tilt: Q,
                                 ground_azimuth: Q,
                                 ) -> Dict[str, Q]:
    """
    Calculate auxiliary geometry values, used as inputs for the shadow calculation.

    Parameters
    ----------
    Are documented in :func:`calc_sloped_shading`

    Returns
    -------
    Dict with these geometry results as Quantities with the following units:
    theta: Quantity [radians (dimensionless)]
        Ground slope in collector azimuth direction.
    epsilon: Quantity [radians (dimensionless)]
        Slope along the collector row (perpendicular to the collector azimuth).
    beta: Quantity [radians (dimensionless)]
        Absolute tílt of the collector surface in collector azimuth direction.
    a_prime: Quantity [meter]
        Collector gross length in collector azimuth direction.
    collector_row_spacing: Quantity [meter]
    collector_gross_length: Quantity [meter]
    collector_azimuth: Quantity [radians (dimensionless)]
    plane_a: Quantity [dimensionless], x-coordinate of the plane's normal vector (see Notes).
    plane_b: Quantity [dimensionless], y-coordinate of the plane's normal vector (see Notes).
    plane_c: Quantity [dimensionless], z-coordinate of the plane's normal vector (see Notes).
    plane_d: Quantity [meter], constant in plane equation (see Notes).

    Notes
    -----
    Parameters are documented in :func:`calc_sloped_shading`
    The internal shadow calculation needs geometrical values such as absolute collector tilt and collector
    gross length in the direction of the collector azimuth. However, for practical reasons, these are measured in
    a different direction (see [1] for details).
    This method computes the measured input quantities in direction of the collector azimuth.
    For further calculation, a plane in 3D is required, defined as
    a*x + b*y +c*z + d = 0, with (a, b, c) being the normal vector of the plane.
    The coefficients (a, b, c, d) are returned as a dict.

    References
    ----------
    .. [1] Zauner, P. et al., (2024): "Internal Shading for Fixed-Mounted Collectors on Sloped Ground"
    """
    a = collector_gross_length
    s = collector_row_spacing

    gamma = collector_azimuth - ground_azimuth
    theta = np.arctan(np.cos(gamma) * np.tan(ground_tilt))
    epsilon = np.arctan(np.sin(gamma) * np.tan(ground_tilt))
    delta = np.arcsin(np.sin(collector_tilt) / np.cos(epsilon)) - theta
    chi = theta + delta

    # Plane coordinates
    plane = {'plane_a': np.sin(epsilon) * np.cos(chi),
             'plane_b': -np.sin(chi),
             'plane_c': np.cos(epsilon) * np.cos(chi),
             'plane_d': s * (np.cos(theta) * np.sin(chi) - np.sin(theta) * np.cos(epsilon) * np.cos(chi))}

    # Normalize plane coefficients
    normalization_factor = 1 / (np.sqrt(plane['plane_a'] ** 2 + plane['plane_b'] ** 2 + plane['plane_c'] ** 2))
    normalize = lambda x: x * normalization_factor
    out = {k: normalize(v) for (k, v) in plane.items()}

    # Angle beta of P1P2 against horizontal (x-coord. = 0)
    beta = np.arctan(np.tan(chi) / np.cos(epsilon))
    epsilon_prime = np.arccos((np.cos(beta) * np.cos(chi)) + (np.cos(epsilon) * np.sin(beta) * np.sin(chi)))
    a_prime = a / (np.cos(epsilon_prime))

    # ToDo PO Remove / Move to Array property
    # calculate shadow angle midpoint
    # D = s * np.cos(theta) - a_prime * np.cos(beta) + a_prime * 0.5 * np.cos(beta)
    # H = a_prime * np.sin(beta) - s * np.sin(theta) - a_prime * 0.5 * np.sin(beta)
    # shadow_angle_midpoint = np.arctan(H / D)

    # Add values to the output dictionary
    out['theta'] = theta  # ground tilt in azimuth direction
    out['chi'] = chi  # ground tilt in azimuth direction
    out['epsilon'] = epsilon  # ground tilt perpendicular to azimuth direction
    out['beta'] = beta  # collector tilt in azimuth direction
    out['a_prime'] = a_prime  # apparent collector height in azimuth direction
    return out
