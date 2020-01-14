#!/usr/bin/python

import pyiridium9602
from additional_functions import *
import threading
import queue
import time

#  Thread to take numerical inputs that initiate functions

# Initiate serial port and modem interface

ser = pyiridium9602.IridiumCommunicator('/dev/ttyUSB0')
ser.timeout = 5
ser.connect()



def read_kbd_input(inputQueue): # Establish queue that will read keyboard inputs
    print('Ready for keyboard input:')

    while (True):
        input_str = input()
        inputQueue.put(input_str)


def main():
    EXIT_COMMAND = 0

    MENU = "menu"
    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()

    while (True):
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()
            if len(input_str) < 3:
                func_code = int(input_str)
            else:
                func_code = 100  # Prevent 'variable accessed before assignment' error
            #print("input_str = {}".format(input_str))

            if input_str == MENU:  # Show list of functions with function code
                menu = open('FunctionList.txt', 'r')
                options = menu.readlines()
                for a in options:
                    a = a.strip()
                    print(a)

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                break

            if func_code == 0:
                # Creates a text document with a list of time stamps and signal qualities,
                # and sends a SBD message with contents
                get_signal_qual(ser)
                print('Signal Quality Recorded')

            if func_code == 1:
                ser.initiate_session()  # Send MO messages and Retrieve MT messages
                print('Session Initiated')

            if func_code == 2:  # Enable radio activity
                enable_radio(ser)

            if func_code == 3:  # Disable radio activity
                disable_radio(ser)

            if func_code == 4: # Returns the latitude, longitude and altitude of the modem
                lat, long, alt = get_location(ser)
                print(lat, long, alt)

            if func_code == 5:
                local_time = ser.acquire_system_time()  # Returns the Iridium system time
                print(local_time)

            if func_code == 6:  # Returns location, signal quality and time in a document - under development
                loc_sig_time(ser)

            if func_code == 7:  # Returns info on satellite in view, beam and signal quality. Needs work
                event_report(ser)

            if func_code == 8:  # Runs a testing loop and records a doc
                f = open('testing.txt', 'w+')
                testing_loop(ser, 'Message to Send', f)

            if func_code == 9:  # Sends the data contained in a defined file
                send_potA(ser)

            if func_code == 10:  # Sends the data contained in a defined file
                send_potB(ser)

            if func_code == 11:  # Retrieves a message from the MT buffer
                get_MT_msg(ser)


            # Insert your code here to do whatever you want with the input_str.

        # The rest of your program goes here.

        time.sleep(0.01)
    print("End.")

if (__name__ == '__main__'):
    main()