#!/usr/bin/python
import time
# used lib is: https://github.com/adafruit/Adafruit_CircuitPython_DHT
# lib usage: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
import adafruit_dht 
import logging
import os
import board 

dhtSensor1 = adafruit_dht.DHT22(board.D4)# 3.3V
dhtSensor2 = adafruit_dht.DHT22(board.D17)# 5V
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
		hum, temp  = dev.humidity, dev.temperature
		if use_print:
			print("PIN "+str(dev)+" :", temp, hum)
	# except RuntimeError as error:
	# 	# Errors happen fairly often, DHT's are hard to read, just keep going
	# 	print(error.args[0])
	# 	time.sleep(2.0)
	# except Exception as error:
	# 	dev.exit()
	# 	raise error			
	except Exception as e:
		if use_print:
			print(e)
		error = 1
	return temp, hum, error

def read2dev(dhtSensor1, dhtSensor2, timeout=sleep_secs):
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
		temp_in, hum_in, error_in    = read(dhtSensor1)
		time.sleep(1)
		temp_out, hum_out, error_out = read(dhtSensor2)
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

file_name ="/home/pitwo/temp/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
temperature_inside, humidity_inside, temperature_outside, humidity_outside, ci, co = read2dev(dhtSensor1, dhtSensor2)
if use_print:
    print("Start values outside", temperature_inside, humidity_inside, humidity_outside, temperature_outside)
    print("Logging started to", file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside\tCorrectReadingsIn\tCorrectReadingsOut")
if use_print:
    print("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside\tCorrectReadingsIn\tCorrectReadingsOut")

i = 1
while True:
	temperature_inside, humidity_inside, temperature_outside, humidity_outside, ci, co = read2dev(dhtSensor1, dhtSensor2)
	result = "\t"+str(i)+"\t"+str(temperature_outside)+"\t"+str(humidity_outside)+"\t"+str(temperature_inside)+"\t"+str(humidity_inside)+"\t"+str(ci)+"\t"+str(co)
	logging.info(result)
	timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
	if use_print:
		print(timee+result)
	i = i+1