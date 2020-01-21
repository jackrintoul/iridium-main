#!/usr/bin/python

# Author: Jack Rintoul - 2/12/19

# Functions to supplement the pyiridium9602 package


from pyproj import Proj, transform
import time
import pyiridium9602

TIME_BETWEEN_EPOCHS = 1425398400


def get_signal_qual(self):
    initial_time = self.acquire_system_time()
    signal_report = open("signal_reports/signal_report_%s.txt" % initial_time, 'w+')
    for i in range(0, 3):  # Sets number of readings to record
        sig = self.acquire_signal_quality()  # Retrieve signal quality
        current_time = self.acquire_system_time()  # Retrieve system time
        print(current_time)
        # print('signal quality: ' + str(sig) + ' Time:' + str(current_time))
        result_line = str(current_time) + '  ' + str(sig) + '\n'
        signal_report.write(result_line)
        time.sleep(1)  # Delay between recordings
    signal_report.close()  # Close doc to save contents
    report = open("signal_reports/signal_report_%s.txt" % initial_time, 'r')  # saves doc with first time signature
    # report = open("signal_reports/signal_report_1989541564.txt", 'r')
    msg = report.read()  # record contents of doc
    hex_msg = msg.encode('utf-8')  # convert to hex to send
    print(msg)
    print(hex_msg)
    self.queue_send_message(msg)  # Upload message to MO buffer
    self.initiate_session()  # Clean MO buffer and send message
    print('Message Sent')


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


def sys_time_to_local(self):  # Convert Iridium system time to local time - probably should be done on the ground
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


def system_time(self):
    sys_time = self.acquire_system_time()
    return sys_time


def testing_loop(self, data, file):
    for i in range(0, 10):
        self.initiate_session()

        # Get location information from the Iridium modem
        # long, lat, alt = get_location(plz)
        # b.write(str(long) + ', ' + str(lat) + ', ' + str(alt) + '\n')
        # print(long, lat, alt)

        time.sleep(2)
        sigQual = self.acquire_signal_quality()
        # sys_time_to_local(plz)
        print(sigQual)
        file.write('Signal Qual:' + str(sigQual) + '\n')
        if int(sigQual) >= 4:
            print('Connection to Iridium Network')
            self.queue_send_message(data)
            self.initiate_session()
        # print('location saved')


def enable_radio(self):  # Allows the Iridium modem to transmit signals
    self.acquire_response(b'AT*R1')
    print('Radio Activity Enabled')


def disable_radio(self):  # Prevents the Iridium modem from sending signals
    self.acquire_response(b'AT*R0')
    print('Radio Activity Disabled')


def event_report(self):
    a = self.acquire_response(b'AT+CIER=1,1,1,1,1')  # Activates all fields for event reporting
    a = self.acquire_response(b'AT')  # Recieve response
    a = a.decode('utf-8')
    a = a.strip()
    a = a.split('+')
    time_stamp = self.acquire_system_time()
    for b in range(0, len(a)):
        a[b] = a[b].strip()
    print(a)
    sig = a[1][-1]
    if len(a) > 2:
        location_details = a[4].split(',')
        # print(location_details)
        sat_num = location_details[1][-1]
        beam_num = location_details[2]
        location_indicator = location_details[3]
        if location_indicator == 0:
            print('bucc location')
        elif location_indicator == 1:
            print('iridium location')
        x = int(location_details[4])
        y = int(location_details[5])
        z = int(location_details[6][0:5])
        # print(sat_num, beam_num,location_indicator)
        # print('Signal Strength: ' + sig)
        # print(x, y, z)
        if isinstance(x, int):
            # 'geocent' refers to the geo-centered frame that the co-ordinates are returned in
            inProj = Proj(proj='geocent', ellps='WGS84', datum='WGS84')

            # 'latlong' is the frame to be converted to
            outProj = Proj(proj='latlong', ellps='WGS84', datum='WGS84')

            # Convert X, Y, Z to latitude, longitude and altitude
            long, lat, alt = transform(inProj, outProj, x, y, z, radians=False)
            # l = [str(long), str(lat), str(alt)]
            print(long, lat, alt)
            result = str(sig) + ' , ' + sat_num + ' , ' + beam_num + ' , ' + str(long), str(lat), str(alt)
        f = open("%s.txt" % time_stamp, 'w+')
        data_str = str(time_stamp) + str(result)
        print(result)
        f.write(data_str)

    self.initiate_session()
    print('message sent')


def send_potA(self):
    f = open("PoTA.txt", 'r') # This text should be a byte string that is to be sent through a SBD message
    msg = f.read()
    self.queue_send_message(msg)
    self.initiate_session()


def send_potB(self):
    f = open("PoTB.txt", 'r') # This text should be a byte string that is to be sent through a SBD message
    msg = f.read()
    self.queue_send_message(msg)
    self.initiate_session()


def get_MT_msg(self):
    a = self.acquire_response(b'AT+SBDSX')
    b = a.decode()
    c = b.strip()
    d = c.split()
    print(d)
    if d[4] == 1:
        g = self.acquire_response(b'AT+SBDRB')
        print(g)
    else:
        print('No MT Message')


def loc_sig_time(self):
    lat, long, alt = get_location(self)
    sig = self.acquire_signal_quality()
    local_time = self.acquire_system_time(self)
    print(str(local_time) + ', ' + 'signal:' + str(sig) + ' location: ' + str(lat), str(long), str(alt))