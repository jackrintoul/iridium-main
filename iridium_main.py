#!/usr/bin/python

import pyiridium9602
from pyproj import Proj, transform
import time
from additional_functions import *
# get_location, sys_time_to_local, initiate_modem


plz, b, PoTA = initiate_modem()
while True:
    time.sleep(2)
    #plz.send_message(PoTA)
    plz.initiate_session()
    plz.clear_both_buffers()
    print('tick')


while True:
    event_report(plz)
    time.sleep(2)

g = plz.acquire_response(b'AT')
print(g)

while True:
    plz.initiate_session()

    # Get location information from the Iridium modem
    #long, lat, alt = get_location(plz)
    #b.write(str(long) + ', ' + str(lat) + ', ' + str(alt) + '\n')
    #print(long, lat, alt)

    time.sleep(.2)
    sigQual = plz.acquire_signal_quality()
    #sys_time_to_local(plz)
    print(sigQual)
    b.write('Signal Qual:' + str(sigQual) + '\n')
    if isinstance(sigQual, int):
        if int(sigQual) >= 2:
            print('Connection to Iridium Network')
            plz.queue_send_message(PoTA)
            plz.initiate_session()
        #print('location saved')
