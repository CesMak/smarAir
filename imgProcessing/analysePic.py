
#see: https://pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
# import the necessary packages
# from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
from numpy import vstack
from copy import deepcopy
import os

INDEX = 0
# define the dictionary of digit segments so we can identify
# each digit on the thermostat
DIGITS_LOOKUP = [
	[1, 1, 1, 0, 1, 1, 1],
	[0, 0, 1, 0, 0, 1, 0],
	[1, 0, 1, 1, 1, 1, 0],
	[1, 0, 1, 1, 0, 1, 1],
	[0, 1, 1, 1, 0, 1, 0],
	[1, 1, 0, 1, 0, 1, 1],#: 5,
	[1, 1, 0, 1, 1, 1, 1],#: 6,
	[1, 0, 1, 0, 0, 1, 0],#: 7,
	[1, 1, 1, 1, 1, 1, 1],#: 8,
	[1, 1, 1, 1, 0, 1, 1],#: 9
]

def saveImg(img, name="_", folder="", print_=False, saveFig=False):
	if saveFig:
		global INDEX
		img_name = str(INDEX)+"_"+name+".png"
		cv2.imwrite(folder+"/"+img_name, img)
		INDEX+=1

def getBoundingRect(countour, bigNumber=False, isOne=False):
	oneBigFactor   = 20
	oneSmallFactor = 5
	(x, y, w, h) = cv2.boundingRect(countour)
	if w*h >550 and w*h <1000: # one big
		x -= oneBigFactor
		w += oneBigFactor
	elif w*h <500: # one small
		x -= oneSmallFactor
		w += oneSmallFactor
	return (x,y,w,h)

def getNumberOfRectangle(rect, img, colorImg, folder="", saveFig=False, print_=False):
	colorImg = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB) # COLOR_BGR2GRAY
	(x, y, w, h) = rect
	# corrector factor!
	y=y+2
	h=h-4
	x+=2
	w-=4
	roi = img[y:y + h, x:x + w]
	saveImg(cv2.rectangle(deepcopy(colorImg),(x,y),(x+w,y+h),(30,255,255),1), "roi", folder=folder)
	(roiH, roiW) = roi.shape
	(dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
	dHC = int(roiH * 0.05)

	# define the set of 7 segments
	segments = [
		((0, 0), (w, dH)),	# top
		((0, 0), (dW, h // 2)),	# top-left
		((w - dW, 0), (w, h // 2)),	# top-right
		((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
		((0, h // 2), (dW, h)),	# bottom-left
		((w - dW, h // 2), (w, h)),	# bottom-right
		((0, h - dH), (w, h))	# bottom
	]
	on = [0] * len(segments)

	# loop over the segments
	for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
		# extract the segment ROI, count the total number of
		# thresholded pixels in the segment, and then compute
		# the area of the segment
		segROI = roi[yA:yB, xA:xB]
		total = cv2.countNonZero(segROI)
		area = (xB - xA) * (yB - yA)
		# if the total number of non-zero pixels is greater than
		# 50% of the area, mark the segment as "on"
		#print(i, round(total/float(area),2))
		tmp = cv2.rectangle(deepcopy(colorImg),(x+xA,y+yA),(x+xB,y+yB),color=(20*i,240,0),thickness=1)
		tmp = cv2.putText(tmp, str(round(total/float(area),2)), (x+xA+10, y+yA+10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0,0,250), 1, cv2.LINE_AA, False)
		saveImg(tmp, "segment"+str(i)+".png", folder=folder, saveFig=saveFig)	
		if total / float(area) > 0.75:
			on[i]= 1
	# find on matching in: DIGITS_LOOKUP
	for i,lockup in enumerate(DIGITS_LOOKUP):
		if lockup == on:
			if print_:print(lockup, on, w*h, "-->", i)
			if w*h>1000:
				return "B"+str(i) # Big Number!
			else:
				return "S"+str(i) # Small Number!
	if print_:print("No number found: ", on, w*h)
	if w*h>1000:
		return "B?"# Big Number!
	else:
		return "S?"# Small Number!


def analyseImg(imgName, folder="", saveFigs=False, print_=False):
	image = cv2.imread(imgName)
	# pre-process the image by resizing it, converting it to
	# graycale, blurring it, and computing an edge map

	rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
	saveImg(rotated, "rotated", folder=folder, saveFig=saveFigs)
	gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
	saveImg(gray, "gray", folder=folder, saveFig=saveFigs)

	# circle / ellipse detection
	rows = gray.shape[0]
	circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=250, maxRadius=300)
	if len(circles[0])>1 and print_:print("ERROR found too many circles!!!")
	x = int(circles[0][0][0])
	y= int(circles[0][0][1])
	radius = int(circles[0][0][2])
	cv2.circle(rotated, (x,y), int(radius), (255, 0, 255), 3)
	saveImg(rotated, "rotated", folder=folder, saveFig=saveFigs)
	cropped = rotated[y-radius:y+radius, x-radius:x+radius]
	saveImg(cropped, "cropped", folder=folder, saveFig=saveFigs)
	gray2 = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray2, (5, 5), 0)
	saveImg(blurred, "blurred", folder=folder, saveFig=saveFigs)
	edged = cv2.Canny(blurred, 5, 25, 10)
	saveImg(edged, "edged", folder=folder, saveFig=saveFigs)

	contours = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(contours)
	xR, yR, wR, hR, cR = 0,0,0,0, []
	# loop over the digit area candidates
	for c in cnts:
		# compute the bounding box of the contour
		(xR, yR, wR, hR ) = cv2.boundingRect(c)
		if wR >250 and hR <150 and hR>60:
			cR = c
			cv2.rectangle(cropped,(xR,yR),(xR+wR,yR+hR),(30,0,90),2)
			break
	saveImg(cropped, "cropped", folder=folder, saveFig=saveFigs)
	offset = 2 # reducing the rectangle!
	cropped2 = cropped[yR+offset:yR+hR-offset*15, xR+offset:xR+wR-offset*2]
	saveImg(cropped2, "cropped2", folder=folder, saveFig=saveFigs)

	gray3 = cv2.cvtColor(cropped2, cv2.COLOR_BGR2GRAY)
	edged2 = cv2.Canny(gray3, 40, 80, 255)
	saveImg(edged2, "edged2", folder=folder, saveFig=saveFigs)


	cc, hir = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = cv2.findContours(edged2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(cropped2, cc, -1, (0, 0, 0), thickness=5)
	saveImg(cropped2, "cropped2", folder=folder, saveFig=saveFigs)

	cnts = imutils.grab_contours(contours)
	bigCnts = []
	digitCnts = []
	ones_foundBig = []
	tmpIMG = deepcopy(cropped2)

	# loop over the digit area candidates
	for c in cnts:
		# compute the bounding box of the contour
		(x, y, w, h) = cv2.boundingRect(c)
		tmpIMG = cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(255,255,255),1)
		tmpIMG = cv2.putText(tmpIMG, str(w*h), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,250), 1, cv2.LINE_AA, False)
	saveImg(tmpIMG, "boundingRect", folder=folder, saveFig=saveFigs)

	# loop over the digit area candidates
	for c in cnts:
		# compute the bounding box of the contour
		(x, y, w, h) = cv2.boundingRect(c)
		if w*h>400:
			if w*h<600 and w<20:
				digitCnts.append(c) # small digits on the right
				continue
			elif w*h>1500:
				bigCnts.append(c)
				continue
			else:
				continue
		else:
			if (h>25 and w<15 and w>5 and h<40 and w*h<250): # detect 1s
				ones_foundBig.append(c)

	allContours = []
	digitCntsSmall = imutils.contours.sort_contours(digitCnts, method="left-to-right")[0]
	digitCntsBig = imutils.contours.sort_contours(bigCnts, method="left-to-right")[0]
	if len(ones_foundBig)>0:
		digitOnesBig = imutils.contours.sort_contours(ones_foundBig, method="left-to-right")[0]
		if (len(digitOnesBig) % 2) != 0:
			digitOnesBig = digitOnesBig[:-1]

		# merge ones contours:
		digitCntsOnesBig = []
		for i in range(len(digitOnesBig)-1):
			digitCntsOnesBig.append(vstack([digitOnesBig[i], digitOnesBig[i+1]]))

		for i in digitCntsOnesBig:
			allContours.append(i)
	for i in digitCntsSmall:
		allContours.append(i)
	for i in digitCntsBig:
		allContours.append(i)
	allContoursSorted =  imutils.contours.sort_contours(allContours, method="left-to-right")[0]
	rects = []
	for c in allContoursSorted:
		rects.append(getBoundingRect(c))

	tmpIMG = cropped2
	# for c in digitCntsSmall:
	# 	# extract the digit ROI
	# 	(x, y, w, h) = cv2.boundingRect(c)
	# 	cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(255,0,0),3)
	# for c in digitCntsBig:
	# 	# extract the digit ROI
	# 	(x, y, w, h) = cv2.boundingRect(c)
	# 	cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(0,0,255),3)
	# for c in digitCntsOnesBig:
	# 	# extract the digit ROI
	# 	(x, y, w, h) = cv2.boundingRect(c)
	# 	cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(0,255,255),3)
	for c in rects:
		(x, y, w, h) = c
		cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(26,25,255),2)		
	saveImg(tmpIMG, "boundingRect2", folder=folder, saveFig=saveFigs)

	# convert 2 white !
	gray4 = cv2.cvtColor(cropped2, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(gray4, 0, 255,	cv2.THRESH_BINARY_INV)
	saveImg(thresh, "thresh", folder=folder, saveFig=saveFigs)
	saveImg(cropped2, "cropped2", folder=folder, saveFig=saveFigs)

	result = ""
	for r in rects:
		result+=getNumberOfRectangle(r, thresh, cropped2,folder=folder, saveFig=saveFigs, print_=print_)

	if sum(char == 'S' for char in result) == 3:
		result = result.replace("S", ',', 1) # replace first S
		result = result.replace("S", "")
		result = result.replace("B", "")

	# Final Image:
	tmpIMG = cv2.putText(cropped2, result, (int(xR/2) ,int(yR/3)+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,250), 2, cv2.LINE_AA, False)
	saveImg(tmpIMG, "finalImg", folder=folder, saveFig=saveFigs)

	return result, tmpIMG
	#getNumberOfRectangle(rects, thresh, cropped2)
	# # # import pytesseract
	# # # from PIL import Image
	# # # img = Image.open('/home/markus/Desktop/4.png')
	# # # print(pytesseract.image_to_string(img))

def analyseFolder(dpath, resultFolder=""):
	for filename in os.listdir(dpath):
		f = os.path.join(dpath, filename)
		# checking if it is a file
		if os.path.isfile(f):
			text_result, imgResult = analyseImg(f, saveFigs=False, print_=False)
			print(text_result)
			if len(resultFolder)>0:
				saveImg(imgResult,f,folder=resultFolder)

# For a single file do:
text_result, imgResult = analyseImg("general_processingData/orginal2.jpg", folder="general_processingData",print_=True, saveFigs=True)
print(text_result)

#analyseFolder("orginalDataStorage/", resultFolder="orginalDataResults")
