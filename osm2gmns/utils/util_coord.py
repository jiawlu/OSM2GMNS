# Copyright (C) 2012 Tobias Bieniek <Tobias.Bieniek@gmx.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


try:
    import numpy as mathlib
    use_numpy = True
except ImportError:
    import math as mathlib
    use_numpy = False


K0 = 0.9996

E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)

SQRT_E = (1 - E)**0.5
_E = (1 - SQRT_E) / (1 + SQRT_E)
_E2 = _E * _E
_E3 = _E2 * _E
_E4 = _E3 * _E
_E5 = _E4 * _E

M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
M3 = (15 * E2 / 256 + 45 * E3 / 1024)
M4 = (35 * E3 / 3072)

P2 = (3. / 2 * _E - 27. / 32 * _E3 + 269. / 512 * _E5)
P3 = (21. / 16 * _E2 - 55. / 32 * _E4)
P4 = (151. / 96 * _E3 - 417. / 128 * _E5)
P5 = (1097. / 512 * _E4)

R = 6378137

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def in_bounds(x, lower, upper, upper_strict=False):
    if upper_strict and use_numpy:
        return lower <= mathlib.min(x) and mathlib.max(x) < upper
    elif upper_strict and not use_numpy:
        return lower <= x < upper
    elif use_numpy:
        return lower <= mathlib.min(x) and mathlib.max(x) <= upper
    return lower <= x <= upper


def mixed_signs(x):
    return use_numpy and mathlib.min(x) < 0 <= mathlib.max(x)


def negative(x):
    return mathlib.max(x) < 0 if use_numpy else x < 0


def latitude_to_zone_letter(latitude):
    # If the input is a numpy array, just use the first element
    # User responsibility to make sure that all points are in one zone
    if use_numpy and isinstance(latitude, mathlib.ndarray):
        latitude = latitude.flat[0]

    return ZONE_LETTERS[int(latitude + 80) >> 3] if -80 <= latitude <= 84 else None


class OutOfRangeError(ValueError):
    pass


def from_latlon(longitude, latitude, central_longitude):
    central_lon_rad = mathlib.radians(central_longitude)

    lat_rad = mathlib.radians(latitude)
    lat_sin = mathlib.sin(lat_rad)
    lat_cos = mathlib.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan * lat_tan
    lat_tan4 = lat_tan2 * lat_tan2

    lon_rad = mathlib.radians(longitude)

    n = R / mathlib.sqrt(1 - E * lat_sin ** 2)
    c = E_P2 * lat_cos ** 2

    a = lat_cos * (lon_rad - central_lon_rad)
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    m = R * (M1 * lat_rad - M2 * mathlib.sin(2 * lat_rad) + M3 * mathlib.sin(4 * lat_rad) - M4 * mathlib.sin(6 * lat_rad))
    easting = K0 * n * (a + a3 / 6 * (1 - lat_tan2 + c) + a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)) + 500000
    northing = K0 * (m + n * lat_tan * (a2 / 2 + a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c ** 2) + a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)))

    if mixed_signs(latitude):
        raise ValueError("latitudes must all have the same sign")
    elif negative(latitude):
        northing += 10000000

    return easting, northing


def to_latlon(easting, northing, central_longitude, northern):  # , zone_number, zone_letter=None, northern=None, strict=True
    # if not zone_letter and northern is None:
    #     raise ValueError('either zone_letter or northern needs to be set')
    #
    # elif zone_letter and northern is not None:
    #     raise ValueError('set either zone_letter or northern, but not both')
    #
    #
    if not in_bounds(easting, 100000, 1000000, upper_strict=True):
        raise OutOfRangeError('easting out of range (must be between 100.000 m and 999.999 m)')
    if not in_bounds(northing, 0, 10000000):
        raise OutOfRangeError('northing out of range (must be between 0 m and 10.000.000 m)')
    #
    # check_valid_zone(zone_number, zone_letter)
    #
    # if zone_letter:
    #     zone_letter = zone_letter.upper()
    #     northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * mathlib.sin(2 * mu) +
             P3 * mathlib.sin(4 * mu) +
             P4 * mathlib.sin(6 * mu) +
             P5 * mathlib.sin(8 * mu))

    p_sin = mathlib.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = mathlib.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = mathlib.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = _E * p_cos ** 2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return mathlib.degrees(longitude) + central_longitude, mathlib.degrees(latitude)
