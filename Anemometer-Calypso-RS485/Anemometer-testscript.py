#!/usr/bin/env python3

import logging

import sys

import time
from datetime import datetime

import serial

import threading
import queue

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS


class LoggingSystem:
    def _init_(self, loglevel):
        logging.warning('raised an error')
        ## for file logging
        numeric_level = getattr(logging, loglevel.upper(), 10)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level,)


class UserInterface():

    def _init_(self):
        self.keyboard_input_str = None

    def keyboard_read_input(self, KeyboardInputQueue):
        #print('Ready for keyboard input: ')
        while (True):
            
            self.keyboard_input_str = input()

            KeyboardInputQueue.put(self.keyboard_input_str)


class SerialInterface():

    def _init_(self):
        self.serial_interface_connection = None

    def serial_port_setup(self):

        #set the parameters for the serial port
        self.serial_interface_connection = serial.Serial(
            #port = 'COM4',\
            port = '/dev/ttyAMA0',\
            baudrate = 38400,\
            parity = serial.PARITY_NONE,\
            stopbits = serial.STOPBITS_ONE,\
            bytesize = serial.EIGHTBITS,\
            timeout = 2)

        print("connected to: " + self.serial_interface_connection.portstr)

        return()

    def serial_read_input(self, SerialInputQueue):
        
        #Example expected char string
        #$IIMWV,066,R,000.5,M,A*25\r\n

        while (self.serial_interface_connection.isOpen()):

            if (self.serial_interface_connection.inWaiting() > 25):

                timestamp_received_ns = time.time_ns()
               # logging.warning("timestamp_received_ns : " +str(timestamp_received_ns))

                received_connection = self.serial_interface_connection.inWaiting()
                logging.warning("received_connection: " +str(received_connection))

                received_message = self.serial_interface_connection.readline(26)
              #  logging.warning("received message: " +str(received_message))

                received_connection = self.serial_interface_connection.inWaiting()
                logging.warning("received_connection-2: " +str(received_connection))

                received_connection = 0

                decoded_message=received_message.decode('ascii')
              #  logging.warning("decoded message: " + decoded_message[0:25])

                windspeed_message = decoded_message[13:17]
             #   logging.warning("Windspeed message: " + windspeed_message)

                windspeed=float(windspeed_message)
              #  logging.warning("Windspeed [m/s]: " +str (windspeed))

                winddirection_message = decoded_message[7:10]
              #  logging.warning("Winddirection message : " + winddirection_message)

                winddirection=int(winddirection_message)
              #  logging.warning("Winddirection [deg] : " +str (winddirection))

               # logging.warning("**************************\n\n\n**************************")

                SerialInputQueue.put((winddirection, windspeed, timestamp_received_ns))
            
                #if (SerialInputQueue.qsize() > 0):
                #    winddirection, windspeed, timestamp_received_ns = SerialInputQueue.get()
                #    print("Winddirection: " +str (windspeed))
                #Did Check. And Values are actually written into the Queue

            time.sleep(0.01)


class InfluxDBInterface():

    def _init_(self):
        self.write_api = None


    def influxdb_connection_setup(self):

        #set the basic paramters for the inluxDB point access

        self.token = "vRwyh3JmkRbpEskWtiyuOuSHps3cNV-CYarGcQmqrGJ14ZVrT02FnDIzF8LmvsFXWLRASGZ1kf_v6yvjNqp7lg=="
        self.org = "alexandria"
        self.bucket = "Wetterstation-Bucket"

        client = InfluxDBClient(url = "http://192.168.2.3:8086", token = self.token)

        self.write_api = client.write_api(write_options = ASYNCHRONOUS)

        logging.warning("Write API : " +str(self.write_api))

        return()



    def InfluxDB_upload(self, SerialInputQueue):

        #The fuction to be threaded for uploading the received values into the influxDB from the Queue
        
        while(True):
            logging.debug("Loop Upload")
            result = None

            if (SerialInputQueue.qsize() > 0):
                logging.warning("Start Upload")

                logging.warning("Queue Size initially: " +str(SerialInputQueue.qsize()))

                winddirection, windspeed, timestamp_received_ns = SerialInputQueue.get()

                logging.warning("Queue Size post: " +str(SerialInputQueue.qsize()))

                timestamp_received_s = int(timestamp_received_ns/1000000000)

                #print("Timestamp s: " +str(timestamp_received_s))

                local_time_human = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_received_s))

                logging.warning("Winddirection: {} Windspeed: {} Epoch-Timestamp: {} \n Lokale Zeit: {} ".format(winddirection, windspeed, timestamp_received_ns, local_time_human))
           
                point = Point("Testrun").tag("Sensor", "Anemometer").field("Winddirection_[deg]", winddirection).field("Windspeed_[m/s]", windspeed).field("Reading_received_timestamp_[ns]", timestamp_received_ns).field("Reading_received_timestamp_[UTC]", local_time_human)


                upload_start_ns = time.time_ns()
                result = self.write_api.write(self.bucket, self.org, point)
                upload_finish_ns = time.time_ns()

                logging.warning("timedelta Upload: " +str(upload_finish_ns - upload_start_ns))

                logging.info("Result : " +str(result))

            time.sleep(0.01)

        

def main():

    EXIT_COMMAND = "exit" # Command to exit this program

    Logging_Init = LoggingSystem()

    logging.warning('Logging Initiated')

    Keyboard_Input = UserInterface()

    logging.warning("User Interface loaded")

    Calypso_Serial = SerialInterface()
    Calypso_Serial.serial_port_setup()

    logging.warning("Serial Port set up")

    Upload_Server = InfluxDBInterface()
    Upload_Server.influxdb_connection_setup()

    logging.warning("InfluxDB connection set up")

    KeyboardInputQueue = queue.Queue()
    SerialInputQueue = queue.Queue()

    logging.warning("Queues set up")

    KeyboardInputThread = threading.Thread(target= Keyboard_Input.keyboard_read_input, args=(KeyboardInputQueue,), daemon=True)
    KeyboardInputThread.start()

    SerialInputThread = threading.Thread(target= Calypso_Serial.serial_read_input, args=(SerialInputQueue,), daemon=True)
    SerialInputThread.start()

    InfluxDBOutputThread = threading.Thread(target= Upload_Server.InfluxDB_upload, args=(SerialInputQueue,), daemon=True)
    InfluxDBOutputThread.start()

    logging.warning("Threads started")

    # Main loop
    while (True):

        if (KeyboardInputQueue.qsize() > 0):
            keyboard_input_str = KeyboardInputQueue.get()
            print("input_str = {}".format(keyboard_input_str))

            if (keyboard_input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                Calypso_Serial.serial_interface_connection.close()
                print("Serial Interfacce queue" +str(SerialInputQueue.qsize()))
                while (SerialInputQueue.qsize() > 0):
                    time.sleep(0.1)
                    if (SerialInputQueue.qsize() == 0):
                        #KeyboardInputThread.stop()
                         #Calypso_Serial.stop()
                        #InfluxDBOutputThread.stop()

                        break # exit the while loop
                
            # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01) 
    
    print("End.")

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()