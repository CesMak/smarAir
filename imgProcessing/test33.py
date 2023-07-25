
#see: https://pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
# import the necessary packages
# from imutils.perspective import four_point_transform
# from imutils import contours
import imutils
import cv2
# define the dictionary of digit segments so we can identify
# each digit on the thermostat
DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 1, 0): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}

image = cv2.imread("tmp.jpg")
# pre-process the image by resizing it, converting it to
# graycale, blurring it, and computing an edge map

rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite("0.png", rotated)
# Cropping an image
copped2 = rotated[1094:1210 , 563:825]
cv2.imwrite("1.png", copped2)
gray = cv2.cvtColor(copped2, cv2.COLOR_BGR2GRAY)
cv2.imwrite("2.png", gray)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
cv2.imwrite("3.png", blurred)



edged = cv2.Canny(blurred, 5, 25, 10)
cv2.imwrite("4.png", edged)

contours, hierarchy = cv2.findContours(edged, 
    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = cv2.drawContours(copped2, contours, -1, (0, 255, 0), 2)
  
cv2.imwrite("5.png", copped2)
# cnts = imutils.grab_contours(cnts)
# digitCnts = []
# # loop over the digit area candidates
# for c in cnts:
# 	# compute the bounding box of the contour
# 	(x, y, w, h) = cv2.boundingRect(c)


import pytesseract
from PIL import Image
img = Image.open('/home/markus/Desktop/4.png')
print(pytesseract.image_to_string(img))
