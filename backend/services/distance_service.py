"""
Distance calculation using the Haversine formula.

No paid Google Maps API is used - this works purely from stored
latitude/longitude, which is exactly what Section 12 of the spec requires.
"""

import math

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the great-circle distance in kilometres between two
    (latitude, longitude) points.
    """
    if None in (lat1, lon1, lat2, lon2):
        raise ValueError("All coordinates must be provided to calculate distance.")

    lat1_r, lon1_r, lat2_r, lon2_r = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * c


def location_score(distance_km: float, max_radius_km: float) -> float:
    """
    Converts a raw distance into a 0-1 score for the matching engine.

    - Beyond max_radius_km -> 0 (the caller is expected to also exclude
      the worker entirely, not just award a zero score).
    - At distance 0 -> 1.0 (best possible score).
    - Linear falloff in between.
    """
    if distance_km is None or max_radius_km <= 0:
        return 0.0
    if distance_km > max_radius_km:
        return 0.0
    return max(0.0, 1 - (distance_km / max_radius_km))
