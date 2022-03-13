# This is with the new Lib!
import adafruit_dht
import board
import time

dht_device = adafruit_dht.DHT22(board.D4)
sleep_secs = 2

while True:
	try:
		temp = dht_device.temperature
		hum  = dht_device.humidity
		print(temp, hum)
	except Exception as e:
		print(e)
	time.sleep(sleep_secs)
