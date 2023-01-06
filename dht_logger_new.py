import time
import Adafruit_DHT
import logging
import os

sensor  = 22
dev_in = 4  # 3.3V
dev_out  = 17 # 5V
sleep_secs  = 10
use_print   = False

humidity_outside = -111
humidity_inside  = -111
temperature_inside = -111
temperature_outside = -111

def mean(my_list):
	return round(sum(my_list)/len(my_list), 2)

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

def read(dev):
	error = 0
	temp = -111
	hum  = -111
	try:
		hum, temp  = Adafruit_DHT.read_retry(sensor, dev)
		if use_print:
			print("PIN "+str(dev)+" :", temp, hum)
	except Exception as e:
		if use_print:
			print(e)
		error = 1
	return temp, hum, error

def read2dev(dev_in, dev_out, timeout=sleep_secs):
	hum_in   = -111
	temp_in  = -111
	hum_out  = -111
	temp_out = -111
	tmp          = 1
	temp_arr_in  = []
	hum_arr_in   = []
	temp_arr_out = []
	hum_arr_out  = []
	correct_in   = 0
	correct_out  = 0
	error_in     = 0
	error_out    = 0
	while True:
		error = 0
		temp_in, hum_in, error_in    = read(dev_in)
		time.sleep(1)
		temp_out, hum_out, error_out = read(dev_out)
		if tmp>=timeout:
			if use_print:	print(temp_arr_in, hum_arr_in, temp_arr_out, hum_arr_out)
			if len(temp_arr_in)  == 0:	temp_arr_in.append(-222)
			if len(hum_arr_in)   == 0:	hum_arr_in.append(-222)
			if len(temp_arr_out) == 0:	temp_arr_out.append(-222)
			if len(hum_arr_out)  == 0:	hum_arr_out.append(-222)
			return mean(temp_arr_in), mean(hum_arr_in), mean(temp_arr_out), mean(hum_arr_out), correct_in, correct_out
		if tmp<timeout and error_in == 0:
			if use_print: print(temp_arr_in, hum_arr_in)
			if not check_error(temp_in, ctrl="temp"): temp_arr_in.append(round(temp_in,2))
			if not check_error(hum_in,  ctrl="hum"): hum_arr_in.append(round(hum_in,2))
			correct_in = correct_in+1
		if tmp<timeout and error_out == 0:
			if use_print: print(temp_arr_out, hum_arr_out)
			if not check_error(temp_out, ctrl="temp"): temp_arr_out.append(round(temp_out,2))
			if not check_error(hum_out,  ctrl="hum"): hum_arr_out.append(round(hum_out,2))
			correct_out = correct_out+1
		time.sleep(1)
		tmp = tmp+1

file_name ="/home/pi/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
temperature_inside, humidity_inside, temperature_outside, humidity_outside, ci, co = read2dev(dev_in, dev_out)
if use_print:
    print("Start values outside", temperature_inside, humidity_inside, humidity_outside, temperature_outside)
    print("Logging started to", file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside\tCorrectReadingsIn\tCorrectReadingsOut")
if use_print:
    print("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside\tCorrectReadingsIn\tCorrectReadingsOut")

i = 1
while True:
	temperature_inside, humidity_inside, temperature_outside, humidity_outside, ci, co = read2dev(dev_in, dev_out)
	result = str(i)+"\t"+str(temperature_outside)+"\t"+str(humidity_outside)+"\t"+str(temperature_inside)+"\t"+str(humidity_inside)+"\t"+str(ci)+"\t"+str(co)
	logging.info(result)
	timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
	if use_print:
		print(timee+result)
	i = i+1
