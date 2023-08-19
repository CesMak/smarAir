import cv2
from gpiozero import LED #imports the LED functions from gpiozero library
from picamera2 import Picamera2
import time
picam2 = Picamera2()
INDEX = 0
PIC_NAME = "test.jpg"

def takePicture(pic_name ="test.jpg"):
	led = LED(27) #declared gpio pin 10
	led.on() #turn on led
	picam2.configure(picam2.create_preview_configuration())
	picam2.start()

	# Run for a second to get a reasonable "middle" exposure level.
	time.sleep(1)
	metadata = picam2.capture_metadata()
	exposure_normal = metadata["ExposureTime"]
	gain = metadata["AnalogueGain"] * metadata["DigitalGain"]
	picam2.stop()
	controls = {"ExposureTime": exposure_normal, "AnalogueGain": gain}
	capture_config = picam2.create_preview_configuration(main={"size": (1024, 768),
															"format": "RGB888"},
														controls=controls)

	exposure_long = int(exposure_normal * 5)
	picam2.set_controls({"ExposureTime": exposure_long, "AnalogueGain": gain})
	picam2.start()
	camera_config = picam2.create_still_configuration(main={"size": (2592, 1944)})
	time.sleep(2)
	picam2.switch_mode_and_capture_file("still", pic_name)
	picam2.stop()
	time.sleep(1)
	led.off()
	print("Finished taking a picture: ", pic_name)

def saveImg(img, name="_", use_date=False):
	global INDEX
	img_name = "/home/pitwo/imgReader/imgs/"+str(INDEX)+"_"+name+".png"
	if use_date:
		img_name = "/home/pitwo/imgReader/imgs/"+str(INDEX)+"_"+name+str(time.strftime("%d-%H%M%S"))+".png"		
	cv2.imwrite(img_name, img)
	print("saved image: ", img_name)
	INDEX+=1

def processImg(img_name="tmp.jpg"):
	print("processing the image now....")
	image = cv2.imread(img_name)
	#saveImg(image, name="orginal")
	
	# pre-process the image by resizing it, converting it to
	# graycale, blurring it, and computing an edge map
	rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
	#saveImg(rotated, name="rotated")

	# Cropping an image
	cropped = rotated[1094:1210 , 563:825]
	saveImg(cropped, name="cropped", use_date=True)
	gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
	#saveImg(gray, name="gray")
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	#saveImg(blurred, name="blurred")
	edged = cv2.Canny(blurred, 5, 25, 10)
	#saveImg(edged, name="edged")
	print("finished processing the images!")


print("TAKE PICTURE")
takePicture(PIC_NAME)
processImg(PIC_NAME)