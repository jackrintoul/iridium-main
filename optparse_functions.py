#!/usr/bin/python

import pyiridium9602
import time
from pyproj import Proj, transform


def signal_qual(self):
    sig = None
    while sig is None:
        sig = self.acquire_signal_quality()
        time.sleep(0.5)
    return sig


def get_location(self):
    # h = b'\r\nAT-MSGEO\r\r\n-MSGEO: -3936,3464,-3612,7402d50c\r\n\r\n'
    # an example of the string returned from the AT-MSGEO used for testing.
    h = self.acquire_response(b'AT-MSGEO')
    if isinstance(h, bytes):
        h = h.decode('utf-8')
        h = h.strip()
        h = h.split(':')
        h = h[1].split(',')
        x = int(h[0])*1000  # Convert coordinates to meters.
        y = int(h[1])*1000
        z = int(h[2])*1000
    else:
        print('Location not available')

    # 'geocent' refers to the geo-centered frame that the co-ordinates are returned in
    inProj = Proj(proj='geocent', ellps='WGS84', datum='WGS84')

    # 'latlong' is the frame to be converted to
    outProj = Proj(proj='latlong', ellps='WGS84', datum='WGS84')

    # Convert X, Y, Z to latitude, longitude and altitude
    long, lat, alt = transform(inProj, outProj, x, y, z, radians=False)
    # l = [str(long), str(lat), str(alt)]
    return long, lat, alt


def sys_time(self):
    timestamp = None
    while timestamp is None:
        timestamp = self.acquire_system_time()
    return timestamp
