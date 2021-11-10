from datetime import datetime
import sys

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

import serial

token = "vRwyh3JmkRbpEskWtiyuOuSHps3cNV-CYarGcQmqrGJ14ZVrT02FnDIzF8LmvsFXWLRASGZ1kf_v6yvjNqp7lg=="
org = "alexandria"
bucket = "Wetterstation-Bucket"

client = InfluxDBClient(url="http://192.168.2.2:8086", token=token)

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
#$IIMWV,066,R,000.5,M,A*25

while True:
 received_message=serial_connection.readline(27)
 print("received message: " +str(received_message))
 # if received_message != " ":
 decoded_message=received_message.decode('ascii')
 print("decoded message: " + decoded_message)
 
 windspeed_message = decoded_message[13:18]
 print("Windspeed message: " + windspeed_message)
 
 windspeed=float(windspeed_message)
 print("Windspeed : " +str (windspeed)) 
 
 winddirection_message = decoded_message[8:10]
 print("Winddirection message : " + winddirection_message)
  
 winddirection=int(winddirection_message)
 print("Winddirection : " +str (winddirection))
 
 point = Point("Testrun").tag("Sensor", "Anemometer").field("Winddirection", winddirection).field("Windspeed", windspeed).time(datetime.utcnow(), WritePrecision.NS)

 result=write_api.write(bucket, org, point)

 print("Result : " +str(result)) 

serial_connection.close()

sys.exit()