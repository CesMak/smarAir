import time
import Adafruit_DHT
import logging
import os

sensor     = 22
pin_outside= 4  # 5V
pin_inside  = 17 # 3.3V
sleep_secs = 10
use_print  = True
# journalctl -u dht_logger.service

humidity_outside = -111
humidity_inside  = -111
temperature_inside = -111
temperature_outside = -111

file_name ="/home/pi/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
humidity_out_start, temperature_out_start = Adafruit_DHT.read_retry(sensor, pin_outside)
hum_in, temp_in = Adafruit_DHT.read_retry(sensor, pin_inside)
if use_print:
    print("Start values inside", hum_in, temp_in)
    print("Start values outside", humidity_out_start, temperature_out_start)
    print("Logging started to", file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside")
if use_print:
    print("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside")

def check_error(in_value, ctrl="hum"):
    if in_value is None:
        return "-222"
    if ctrl=="hum":
        if in_value<20 or in_value>100:
            return "-111"
        else:
            return str(round(in_value,2))
    else:
        if in_value<-25 or in_value > 55:
            return "-111"
        else:
            return str(round(in_value,2))

for i in range(200000000):
    try:
        humidity_outside, temperature_outside = Adafruit_DHT.read_retry(sensor, pin_outside)
    except Exception as e:
        logging.error("outside_temp read did not work")
        if use_print:
            print("outside temp, hum read did not work!")
    try:
        humidity_inside, temperature_inside = Adafruit_DHT.read_retry(sensor, pin_inside)
    except Exception as e:
        logging.error("inside_temp read did not work")
        if use_print:
            print("inside temp, hum read did not work!")

    humidity_outside = check_error(humidity_outside, ctrl="hum")
    humidity_inside  = check_error(humidity_inside, ctrl="hum")
    temperature_inside = check_error(temperature_inside, ctrl="temp")
    temperature_outside = check_error(temperature_outside, ctrl="temp")

    result = str(i)+"\t"+temperature_outside+"\t"+humidity_outside+"\t"+temperature_inside+"\t"+humidity_inside
    logging.info(result)
    timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    if use_print:
        print(timee+result)
    time.sleep(sleep_secs)
