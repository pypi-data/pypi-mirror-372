def longitude_to_360(lon: float) -> float:
    """
    Convert longitude value to [0, 360) format.

    Arguments:
    ----------
    lon : float
        Longitude value in either [0, 360) or [-180, 180) format.

    Returns:
    --------
    float
        Longitude value in [0, 360) format.
    """
    return lon % 360.0


def longitude_to_180(lon: float) -> float:
    """Convert longitude value to [-180, 180) format.

    Arguments:
    ----------
    lon : float
        Longitude value in either [0, 360) or [-180, 180) format.

    Returns:
    --------
    float
        Longitude value in [-180, 180) format.
    """
    return (lon + 180.0) % 360 - 180.0


def lon_hemisphere(lon):
    """
    Boolean value representing the hemisphere for a given longitude.

    Eastern hemishpere values [0,180) are encoded as True.

    Western hemisphere values [-180, 0) are encoded as False.

    For internal consistency, the following edge-cases conventions
    are made:

     - `0.0` is taken as Eastern
     - `360.0` is taken as Western
     - `-180.0` is taken as Western
     - `180.0` is taken as Eastern
    """
    if abs(lon - 180.0) < 1e-5:
        return True

    if abs(lon - 360.0) < 1e-5:
        return False

    return longitude_to_180(lon) >= 0.0
