#!/usr/bin/python

# Author: Jack Rintoul - 2/12/19

# Functions to supplement the pyiridium9602 package


from pyproj import Proj, transform
import time
import pyiridium9602

TIME_BETWEEN_EPOCHS = 1425340800
# get_location retrieves X, Y, X co-ordinates from the Iridium 9603 Modem and converts to lat, long.


def initiate_modem():
    f = open('/home/jack/Iridium/PoT_A.txt', "r")  # Read telemetry
    PoTA = f.read()
    # print(PoTA)
    b = open('/home/jack/Iridium/site-packages/GPS_Results.txt', "w")  # Open document to record test results

    plz = pyiridium9602.IridiumCommunicator('/dev/ttyUSB0')  # Initiate modem object
    plz._connect_timeout = 5

    plz.connect()  # Connect to modem
    return plz, b, PoTA

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

# Iridium system time is given as time since Iridium epoch, which occurred on March 3, 2015.
# The time since epoch is given as a count of 0.09s (90ms) increments.


def sys_time_to_local(self):
    session_time = 0
    epoch_time = self.request_system_time()  # Time since Iridium epoch (in 0.09s increments)
    if isinstance(epoch_time, int):  # If Iridium network is unavailable, the result will be None
        time_since_iridium_epoch = epoch_time * 0.09  # In seconds
        session_time = time_since_iridium_epoch + TIME_BETWEEN_EPOCHS  # Time since Unix epoch in seconds
        # epoch_time = 149663654 Example of time since Iridium epoch, used for testing
        session_time = time.strftime("%m %d %Y %H:%M:%S", time.localtime(session_time))  # Convert to readable format
    else:
        print('Time Not Available')
    return session_time


