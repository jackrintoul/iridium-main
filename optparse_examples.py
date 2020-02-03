#!/usr/bin/python

"""  Iridium 9603 Communication Script

This script enables simple communication with an Iridium 9603 modem utilising the pyiridium9602 module.
It is assumed the modem is accessible through a serial connection and that the pyiridium9602 module is installed.

This script contains the functions:
    * initiate_modem - initiates an IridiumCommunicator object through the pyiridium9602 package to allow communication with the modem
    * data_loop - records the required data to be sent or stored
    * send_tlm - parses data from an existing file (usually telemetry or acquired data) to be sent through an SBD message

"""

from pyiridium9602 import *
from additional_functions import *
from optparse_functions import *
import time
from optparse import OptionParser, OptionError


def initiate_modem(ser, port_name):
    """ Initiates a serial object to communicate with the Iridium modem.

    :param ser: the name of the IridiumCommunicator object for reference by other functions (default = ser)
    :param port_name: the location of the serial connection (default = /dev/ttyUSB0)
    :return: ser
    """
    connected = False
    max_attempts = 10
    attempt = 0

    while connected is False and attempt < max_attempts:
        try:
            ser = pyiridium9602.IridiumCommunicator(port_name)
            ser.timeout = 2
            ser.connect()
        except IridiumError as e:
            print(e)

        if ser.is_connected() is True:
            connected = True
            print('Connection Achieved')
            return ser
        else:
            attempt += 1
    print('Connection Decieved')
    exit()


def data_loop(self, iterations, delay, sig, location, sys_time, filename):
    """Records specified data from the modem

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
            a.append(str(signal_qual(self)) + ' ')  # Retrieve signal quality
        if location is True:
            a.append(str(get_location(self)) + ' ')  # Retrieve location
        if sys_time is True:
            a.append(str(sys_time(self)) + ' ')  # Retrieve system time
        result.append(a)
        time.sleep(delay)
    print(result)
    return result


def send_tlm(self, filename):
    """ Retrieves data from the flight computer and sends contents as SBD message.
    Parameters:
    -----------
    filename : string
        location of the data to be sent
    """
    try:
        f = open(filename, 'r')
        result = f.read()  # Retrieve contents of text file
        self.queue_send_message(result)  # Move message to MO Buffer
        time.sleep(1)
        self.initiate_session()  # Send message to Iridium network
        print(result)
        return result
    except IridiumError as error:
        print(error)

def main():
    parser = OptionParser('usage %prog ')

    parser.set_default('iterations', 10)
    parser.set_default('delay', 1)
    parser.set_default('port_name', '/dev/ttyUSB0')
    parser.set_default('connection_name', 'ser')
    parser.set_default('buccy_data_filename', 'PoTA.txt')

    parser.add_option('-c', dest='connection_name', type='string', help='define name of the pyiridium9602 object')
    parser.add_option('-b', dest='buccy_data', action='store_false', default=True, help='activate to send telemetry')
    parser.add_option('-n', dest='buccy_data_filename', type='string', help='specify the location of the data to send')
    parser.add_option('-r', dest='record', action='store_true', default=False, help='activate to record new data')
    parser.add_option('-p', dest='port_name', type='string', help='specify the port to connect to the modem')
    parser.add_option('-i', dest='iterations', type='int', help='specify the number of data points to record')
    parser.add_option('-d', dest='delay', type='float', help='specify the time between each data point in seconds')
    parser.add_option('-s', dest='sig', action='store_true', default=False, help='activate to record signal quality')
    parser.add_option('-l', dest='location', action='store_true', default=False, help='activate to record location')
    parser.add_option('-t', dest='sys_time', action='store_true', default=False, help='activate to system_time')
    parser.add_option('-m', dest='send', action='store_true', default=False, help='activate to send results as SBD msg')
    parser.add_option('-f', '--file', type='string', dest='filename', default=False, help='define location of data storage')
    parser.add_option('-e', dest='enable', action='store_true', default=False, help='activite to enable radio after disabling')
    parser.add_option('-o', dest='disable', action='store_true', default=False,help='activate to disable radio')

    try:
        (options, args) = parser.parse_args()
    except SystemExit as e:
        print(e)
        return

    try:
        ser = initiate_modem(options.connection_name, options.port_name)  # Establish serial object
    except IridiumError as e:
        print(e)
        exit()

    if options.enable:
        enable_radio(ser)
        print('radio enabled')
    elif options.disable:
        disable_radio(ser)
        print('radio disabled')



    if options.buccy_data:  # Default action - send existing data
        try:
            result = send_tlm(ser, options.buccy_data_filename)
            status = ser.acquire_response(b'AT+SBDS')
            stat = ser.acquire_response(b'AT')
            print(stat)  # Check and print the status of SBD to ensure message has sent
        except IridiumError as err:
            print('Error when sending telemetry: ' + str(err))
    else:
        try:
            result = data_loop(ser, options.iterations, options.delay, options.sig,
                               options.sys_time, options.location, options.filename)
        except IridiumError as err:
            print(err)
        except OptionError as err:
            print(err)

    if options.filename:
        for i in range(options.iterations):
            f = open(options.filename, "a")
            f.write(str(result))
        print('This is the result: ' + str(result))

    if options.send is True:
        try:
            result = str(result)
            result = result.replace('[', '')
            result = result.replace(']', '')
            result = result.replace(' ', '')
            result = result.replace(',', '')
            result = result.replace("'", "")
            if len(result) > 100:
                print('message stripped to 100 characters')
                result = result[:100]
            ser.queue_send_message(result)
            print(result)
            status = ser.acquire_response(b'AT+SBDS')
            print(status)
            ser.initiate_session()
        except IridiumError as err:
            print(err)
        except UnboundLocalError as err:
            print(str(err) + 'helo')


if __name__ == '__main__':
    main()

# parser.add_option("-s", "--signal", )
