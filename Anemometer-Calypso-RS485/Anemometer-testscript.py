#!/usr/bin/env python3

import sys

import time
from datetime import datetime

import serial

import threading
import queue

import logging

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

def keyboard_read_input(KeyboardInputQueue):
    #print('Ready for keyboard input:')
    while (True):
        
        keyboard_input_str = input()

        KeyboardInputQueue.put(keyboard_input_str)


def serial_read_input(SerialInputQueue):

    #Example expected char string
    #$IIMWV,066,R,000.5,M,A*25\r\n

    while (serial_connection.isOpen()):

        if (serial_connection.inWaiting() > 0):

        timestamp_received_ns = time.time_ns()
        print("timestamp_received_ns : " +str(timestamp_received_ns))

        received_connection = serial_connection.inWaiting()
        print("received_connection: " +str(received_connection))

        received_message = serial_connection.readline(27)
        print("received message: " +str(received_message))

        received_connection = 0

        decoded_message=received_message.decode('ascii')
        print("decoded message: " + decoded_message[0:25])

        windspeed_message = decoded_message[13:17]
        print("Windspeed message: " + windspeed_message)

        windspeed=float(windspeed_message)
        print("Windspeed [m/s]: " +str (windspeed))

        winddirection_message = decoded_message[7:10]
        print("Winddirection message : " + winddirection_message)

        winddirection=int(winddirection_message)
        print("Winddirection [deg] : " +str (winddirection))

        point = Point("Testrun").tag("Sensor", "Anemometer").field("Winddirection_[deg]", winddirection).field("Windspeed_[m/s]", windspeed).field("Reading_received_timestamp_[ns]", timestamp_received_ns)

        result=write_api.write(bucket, org, point)

        print("Result : " +str(result))
        print("**************************\n\n\n**************************")
        
        time.sleep(0.01)


def InfluxDB_upload(SerialInputQueue):

    #The fuction to be threaded for uploading the received values into the influxDB from the Queue




def serial_port_setup():

     #set the parameters for the serial port
    serial_connection_set_up = serial.Serial(
        port='COM4',\
        baudrate=38400,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=2)

    print("connected to: " + serial_connection.portstr)

    return(serial_connection_set_up)

def influxdb_connection_setup():

    #set the basic paramters for the inluxDB point access

    token = "vRwyh3JmkRbpEskWtiyuOuSHps3cNV-CYarGcQmqrGJ14ZVrT02FnDIzF8LmvsFXWLRASGZ1kf_v6yvjNqp7lg=="
    org = "alexandria"
    bucket = "Wetterstation-Bucket"

    client = InfluxDBClient(url="http://192.168.2.3:8086", token=token)

    write_api = client.write_api(write_options=ASYNCHRONOUS)

    return([write_api,bucket,org])

def main():

    EXIT_COMMAND = "exit" # Command to exit this program

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
       raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, ...)





    KeyboardInputQueue = queue.Queue()

    KeyboardInputThread = threading.Thread(target= keyboard_read_input, args=(KeyboardInputQueue,), daemon=True)
    KeyboardInputThread.start()

    # Main loop
    while (True):

        # Read keyboard inputs
        # Note: if this queue were being read in multiple places we would need to use the queueLock above to ensure
        # multi-method-call atomic access. Since this is the only place we are removing from the queue, however, in this
        # example program, no locks are required.
        if (KeyboardInputQueue.qsize() > 0):
            keyboard_input_str = KeyboardInputQueue.get()
            print("input_str = {}".format(input_str))

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                serial_connection_set_up.close()
                break # exit the while loop
            
            # Insert your code here to do whatever you want with the input_str.

        # The rest of your program goes here.

        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01) 
    
    print("End.")

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()