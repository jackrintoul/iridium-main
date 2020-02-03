#!/usr/bin/python

"""" Iridium 9603 Functions

This script is to be used in conjunction with optparse_examples.py to operate an Iridium 9603 Modem that is installed
on a cubesat. The functions contained in this script utilise functions from the pyiridium9602 package.

The functions contained below contain:
    * signal_qual - acquire the signal strength of the Iridium network as measured by the modem on a scale of 0-5.
    * get_location - acquire the location of the modem in a ECEF frame, which is then converted to lat, long and alt.
    * sys_time - acquire the current system time of the Iridium network, in 0.09s increments from IridiumNEXT epoch,
            which occurred on 1800 UTC March 3, 2015
    * enable_radio - enable the radio after it has been disable. The radio will be enabled on start up
    * disable_radio - disable the radio when required

"""

import pyiridium9602
import time
from pyproj import Proj, transform


def signal_qual(self):
    """ Determines the current signal quality available to the modem

    Parameters:
    ----------
    self : serial object.
        self is the pyiridium9602.IridiumCommunicator object currently assigned to the modem

    Returns:
    -------
    sig : int
        A measure of the signal quality, between 0-5.

    """
    sig = None
    while sig is None:
        sig = self.acquire_signal_quality()
        time.sleep(0.5)
    return sig


def get_location(self):
    """ Determines the location of the Iridium modem based on communication to the Iridium constellation.

    Parameters:
    ----------
    self - serial object.
        self is the pyiridium9602.IridiumCommunicator object currently assigned to the modem

    Returns:
    --------
    lat - float
        latitude
    long - float
        longitude
    alt - float
        altitude in metres.
    """
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
    """ Retrieves the current Iridium system time

    Parameters:
    ----------
    self - serial object.
        self is the pyiridium9602.IridiumCommunicator object currently assigned to the modem

    Returns:
    --------
    timestamp - int
        a count in 0.09s increments from IridiumNEXT epoch, which occurred on 1800 UTC March 3, 2015
    """
    timestamp = None
    for i in range(10):
        while timestamp is None:
            timestamp = self.acquire_system_time()
            break
    return timestamp


def enable_radio(self):
    """ Enable radio activity on the modem after it has been disabled.
    The radio will be active on start up and will only need to be enabled after it has been actively disabled

    :param self: the active serial connection with a disabled radio

    """
    self.acquire_response(b'AT*R1')



def disable_radio(self):
    """  Disable radio activity

    Disabling the radio will limit radio emissions and offer power saving.

    :param self: The active serial connection

    """
    self.acquire_response(b'AT*R0')

