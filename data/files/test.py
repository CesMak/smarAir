import time
import Adafruit_DHT
import logging
import os

sensor     = 22
pin_outside= 4  # 5V
pin_inside  = 17 # 3.3V
sleep_secs = 60*10

file_name ="/home/pi/"+time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())+"_logging.txt"
print("Started logging to:"+file_name)
logging.basicConfig(format='%(asctime)s %(message)s', filename=file_name, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.info("DateTime\tEntry\tPower\tTemperature_outside\tHumidity_outside\tTemperature_inside\tHumidity_inside")
for i in range(200000000):
    try:
    	humidity_outside, temperature_outside = Adafruit_DHT.read_retry(sensor, pin_outside)
    except Exception as e:
    	print("outside temp, hum read did not work!")
    try:
    	humidity_inside, temperature_inside = Adafruit_DHT.read_retry(sensor, pin_inside)
    except Exception as e:
    	print("outside temp, hum read did not work!")
    	    
    if humidity_outside is not None and temperature_outside is not None and temperature_inside is not None and humidity_inside is not None:
        logging.info(str(i)+"\t"+str(round(temperature_outside,2))+"\t"+str(round(humidity_outside,2))+str(round(temperature_inside,2))+"\t"+str(round(humidity_inside,2)))
        timee = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        #print(timee+"\t"+str(i)+"\t"+str(round(temperature,2))+"\t"+str(round(humidity,2)))
    time.sleep(sleep_secs)


# disable wifi:
# with button click!
# here: http://acoptex.com/project/4006/project-19c-raspberry-pi-zero-w-board-led-and-push-button-at-acoptexcom/#sthash.JAXwnJt6.dpbs
# https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/

# sudo ifconfig wlan0 down
# systemctl disable wpa_supplicant
