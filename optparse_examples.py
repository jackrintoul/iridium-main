#!/usr/bin/python

"""  Iridium 9603 Communication Script

This script enables simple communication with an Iridium 9603 modem utilising the pyiridium9602 module.
It is assumed the modem is accessible through a serial connection and that the pyiridium9602 module is installed.

This script contains the function:
    * data_loop - records the required data to be sent or stored
"""


import pyiridium9602
from additional_functions import *
from optparse_functions import *
import time
from optparse import OptionParser

ser = pyiridium9602.IridiumCommunicator('/dev/ttyUSB0')
ser.timeout = 5
ser.connect()


def data_loop(self, iterations, delay, sig, location):
    """Establishes the modem and records specified data

    Parameters:
    -----------
    port_name : str
        defines the location of the port to connect to the modem
    iterations : int
        How many samples to be taken before results are saved or sent
    delay : int
        The time between each sample (in seconds)
    sig : bool
        Record signal quality data
    location : bool
        Record location data
    record : bool
        Record all results into a file to be accessed later
    send : bool
        Send results as an Iridium SBD message
    """

    result = []
    for i in range(iterations):
        a = []
        if sig is True:
            a.append(str(signal_qual(ser)) + ' ')
        if location is True:
            a.append(str(get_location(ser)) + ' ')
        a.append(str(sys_time(ser)) + '\n')
        result.append(a)
        time.sleep(delay)
    print(result)
    return result


def main():
    parser = OptionParser('usage %prog ')

    parser.set_default('iterations', 10)
    parser.set_default('delay', 1)

    parser.add_option('-p', dest='port_name', type='string', help='specify the port to connect to the modem')
    parser.add_option('-i', dest='iterations', type='int', default='5', help='specify the number of data points to record')
    parser.add_option('-d', dest='delay', type='int', default='10', help='specify the time between each data point in seconds')
    parser.add_option('-s', dest='sig', action='store_true', default=False, help='activate to record signal quality')
    parser.add_option('-l', dest='location', action='store_true', default=False, help='activate to record location')
    parser.add_option('-t', dest='time', action='store_true', default=False, help='activate to system_time')
    parser.add_option('-m', dest='send', action='store_true', default=False, help='activate to send results as SBD msg')
    parser.add_option("-f", "--file", type="string", dest="filename")

    (options, args) = parser.parse_args()

    result = data_loop(options.iterations, options.delay, options.sig,
                         options.location, options.filename)

    if options.filename:
        for i in range(options.iterations):
            f = open(options.filename, "a")
            f.write(str(result))
        print('This is the result: ' + str(result))

    if options.send is not None:
        ser.queue_send_message(result)
        print('Result Sent')
        print('This is the result: ' + str(result))


if __name__ == '__main__':
    main()

# parser.add_option("-s", "--signal", )
