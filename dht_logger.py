import time
import adafruit_dht
import logging
import os
import board

sensor      = 22
pin_outside = 4  # 5V
pin_inside  = 17 # 3.3V
sleep_secs  = 60
use_print   = False

humidity_outside = -111
humidity_inside  = -111
temperature_inside = -111
temperature_outside = -111

dht_device = adafruit_dht.DHT22(board.D4)

def mean(my_list):
	return round(sum(my_list)/len(my_list),2)

def check_error(in_value, ctrl="hum"):
    if in_value is None or isinstance(in_value, str):
       return True
    if ctrl=="hum":
        if in_value<10 or in_value>100:
            return True
        else:
            return False
    else:
        if in_value<-25 or in_value > 55:
            return True
        else:
            return False

def read(device, timeout=sleep_secs):
	hum = -111
	temp = -111
	tmp  = 1
	temp_arr = []
	hum_arr  = []
	while True:
		error = 0
		try:
			temp = device.temperature
			hum  = device.humidity
			if use_print:
				print(temp, hum)
		except Exception as e:
			if use_print:
				print(e)
			error = 1
		if tmp>=timeout:
			if use_print:
				print(hum_arr, temp_arr)
			if len(hum_arr) == 0:
				hum_arr.append(-222)
			if len(temp_arr) == 0:
				temp_arr.append(-222)
			return mean(hum_arr), mean(temp_arr)
		if tmp<timeout and error == 0:
			if not check_error(temp, ctrl="temp"): temp_arr.append(temp)
			if not check_error(hum,  ctrl="hum"): hum_arr.append(hum)
			if use_print:
				print(temp_arr, hum_arr)
		time.sleep(2)
		tmp = tmp+2

file_name ="/home/pi/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
humidity_out_start, temperature_out_start = read(dht_device)
#hum_in, temp_in = Adafruit_DHT.read_retry(sensor, pin_inside)
if use_print:
    #print("Start values inside", hum_in, temp_in)
    print("Start values outside", humidity_out_start, temperature_out_start)
    print("Logging started to", file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside")
if use_print:
    print("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside")

i = 1
while True:
    humidity_outside, temperature_outside = read(dht_device)
    #humidity_inside  = check_error(humidity_inside, ctrl="hum")
    #temperature_inside = check_error(temperature_inside, ctrl="temp")
    result = str(i)+"\t"+str(temperature_outside)+"\t"+str(humidity_outside)+"\t"+str(temperature_inside)+"\t"+str(humidity_inside)
    logging.info(result)
    timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    if use_print:
        print(timee+result)
	i = i+1
