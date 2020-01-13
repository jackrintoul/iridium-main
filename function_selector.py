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



def read_kbd_input(inputQueue):
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
                func_code = 100
            #print("input_str = {}".format(input_str))

            if input_str == MENU:
                menu = open('FunctionList.txt', 'r')
                options = menu.readlines()
                for a in options:
                    a = a.strip()
                    print(a)

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                break

            if func_code == 0:
                # Open a txt document to record signal strength and system time
                initial_time = ser.acquire_system_time()
                signal_report = open("signal_reports/signal_report_%s.txt" % initial_time, 'w+')
                for i in range(0, 3):
                    sig = ser.acquire_signal_quality()
                    current_time = ser.acquire_system_time()
                    print(current_time)
                    #print('signal quality: ' + str(sig) + ' Time:' + str(current_time))
                    result_line = str(current_time) + '  ' + str(sig) + '\n'
                    signal_report.write(result_line)
                    time.sleep(1)
                signal_report.close()
                #report = open("signal_reports/signal_report_%s.txt" % initial_time, 'r')
                report = open("signal_reports/signal_report_1989541564.txt", 'r')
                msg = report.read()
                hex_msg = msg.encode('utf-8')
                print(msg)
                print(hex_msg)
                ser.queue_send_message(msg)
                ser.initiate_session()
                print('Message Sent')

            if func_code == 1:
                ser.initiate_session()
                print('Session Initiated')

            if func_code == 2:
                enable_radio(ser)

            if func_code == 3:
                disable_radio(ser)

            if func_code == 4:
                lat, long, alt = get_location(ser)
                print(lat, long, alt)

            if func_code == 5:
                local_time = ser.acquire_system_time()
                print(local_time)

            if func_code == 6:
                lat, long, alt = get_location(ser)
                sig = ser.acquire_signal_quality()
                local_time = ser.acquire_system_time(ser)
                print(str(local_time) + ', ' + 'signal:' + str(sig) + ' location: ' + str(lat), str(long), str(alt))

            if func_code == 7:
                local_time = sys_time_to_local(ser)
                result = event_report(ser)
                f = open("%s.txt" % local_time, 'w+')
                data_str = str(local_time) + str(result)
                print(result)
                f.write(data_str)

            if func_code == 8:
                f = open('testing.txt', 'w+')
                testing_loop(ser, 'Message to Send', f)

            if func_code == 9:
                send_potA(ser)

            if func_code == 10:
                send_potB(ser)

            if func_code == 11:
                get_MT_msg(ser)


            # Insert your code here to do whatever you want with the input_str.

        # The rest of your program goes here.

        time.sleep(0.01)
    print("End.")

if (__name__ == '__main__'):
    main()