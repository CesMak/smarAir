import time
import Adafruit_DHT
import logging
import os

# NOTE: This is a minimal starting program 

sensor     = 22
pin        = 4
sleep_secs = 1 # 60*10

file_name ="/home/pi/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
print("Started logging to:"+file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature\tHumidity")
for i in range(2000000):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is None:
        humidity =0.0
    if temperature is None:
        temperature = 0.0

    logging.info(str(i)+"\t"+str(round(temperature,2))+"\t"+str(round(humidity,2)))
        #timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        #print(timee+"\t"+str(i)+"\t"+str(round(temperature,2))+"\t"+str(round(humidity,2)))
    time.sleep(sleep_secs)
