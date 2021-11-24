
from datetime import datetime
import sys
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

import serial

token = "vRwyh3JmkRbpEskWtiyuOuSHps3cNV-CYarGcQmqrGJ14ZVrT02FnDIzF8LmvsFXWLRASGZ1kf_v6yvjNqp7lg=="
org = "alexandria"
bucket = "Wetterstation-Bucket"

client = InfluxDBClient(url="http://192.168.2.3:8086", token=token)

write_api = client.write_api(write_options=ASYNCHRONOUS)

serial_connection = serial.Serial(
    port='COM4',\
    baudrate=38400,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=2)
print("connected to: " + serial_connection.portstr)

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

  time.sleep(0.4)

serial_connection.close()

sys.exit()
