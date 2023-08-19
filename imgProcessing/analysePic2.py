
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
	[1, 1, 1, 0, 1, 1, 1],#  0
	[0, 0, 1, 0, 0, 1, 0],#  1
	[1, 0, 1, 1, 1, 0, 1],#  2
	[1, 0, 1, 1, 0, 1, 1],#  3
	[0, 1, 1, 1, 0, 1, 0],#  4
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

def getBoundingRect(countour, smallRect=False):
	# find out if there is a one contained
	oneBigFactor   = 20
	oneSmallFactor = 5
	(x, y, w, h) = cv2.boundingRect(countour)
	if not smallRect and w*h>650 and w*h<800 and h>45 and h<62:
		#print("I found a big Number 1!")
		x -= oneBigFactor
		w += oneBigFactor
	elif smallRect and w*h >185 and w*h<280 and w>5 and w<12: # one small
		#print("I found a small Number 1!")
		x -= oneSmallFactor
		w += oneSmallFactor
	return (x,y,w,h)

def getNumberOfRectangle(rect, img, colorImg, small=False, folder="", saveFig=False, print_=False):
	factor_ = 0.6
	if small: factor_ = 0.53
	(x, y, w, h) = rect
	roi = img[y:y + h, x:x + w]
	saveImg(cv2.rectangle(deepcopy(colorImg),(x,y),(x+w,y+h),(30,255,255),1), "roi", folder=folder, saveFig=saveFig)
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
		if area == 0: # reducing errors!
			area = 0.001
		tmp = cv2.putText(tmp, str(round(total/float(area),2)), (x+xA+10, y+yA+10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0,0,250), 1, cv2.LINE_AA, False)
		saveImg(tmp, "segment"+str(i)+".png", folder=folder, saveFig=saveFig)	
		if total / float(area) > factor_:
			on[i]= 1
	# find on matching in: DIGITS_LOOKUP
	for i,lockup in enumerate(DIGITS_LOOKUP):
		if lockup == on:
			if print_:print(lockup, on, w,h, w*h, "-->", i)
			return str(i)
	if print_:print("No number found: ", on, w*h, w, h)
	return "?"
def cropImg(imgName, folder="", saveFigs=False, print_=False):
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
	return cropped2, xR, yR

def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]
    if center is None:
        center = (w / 2, h / 2)
    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def analyseImgPart(thresh, colorImg, small=False, folder="", saveFigs=False, print_=False):
	thickness_ = 5
	if small:
		thickness_ = 2
	cc, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(thresh, cc, -1, (255, 255, 255), thickness=thickness_)
	saveImg(thresh, "contours", folder=folder, saveFig=saveFigs)

	contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(contours)
	bigCnts = []
	ones_found = []
	digitCntsOnesBig = []
	tmpIMG = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
	digits     = deepcopy(tmpIMG)

	# loop over the digit area candidates
	for c in cnts:
		# compute the bounding box of the contour
		(x, y, w, h) = cv2.boundingRect(c)
		tmpIMG = cv2.rectangle(tmpIMG,(x,y),(x+w,y+h),(0,255,0),1)
		tmpIMG = cv2.putText(tmpIMG, str(w*h), (x+2, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,250), 1, cv2.LINE_AA, False)
	saveImg(tmpIMG, "boundingRect", folder=folder, saveFig=saveFigs)

	# loop over the digit area candidates
	for c in cnts:
		# compute the bounding box of the contour
		(x, y, w, h) = cv2.boundingRect(c)
		if small:
			if w*h>350 or ( w*h>185 and w*h <300 and w>5 and w<12):
				bigCnts.append(c)
				continue
		else:
			if w*h>300:
				if w*h>1500 or (w*h>700 and h>50):
					bigCnts.append(c)
					continue
				else:
					continue
			else:
				if (h>25 and w<15 and w>5 and h<40 and w*h<250): # detect 1s
					ones_found.append(c)

	allContours = []
	digitCntsBig = []
	allContoursSorted = []
	if len(bigCnts)>0:
		digitCntsBig = imutils.contours.sort_contours(bigCnts, method="left-to-right")[0]
	# TODO delete ones merging stuff!
	if len(ones_found)>0:
		digitOnesBig = imutils.contours.sort_contours(ones_found, method="left-to-right")[0]
		if (len(digitOnesBig) % 2) != 0:
			digitOnesBig = digitOnesBig[:-1]

	# merge ones contours:
		for i in range(len(digitOnesBig)-1):
			digitCntsOnesBig.append(vstack([digitOnesBig[i], digitOnesBig[i+1]]))

		for i in digitCntsOnesBig:
			allContours.append(i)
	for i in digitCntsBig:
		allContours.append(i)
	if len(allContours)>0:
		allContoursSorted =  imutils.contours.sort_contours(allContours, method="left-to-right")[0]
	
	rects = []
	# adapt bounding rect for ones:
	for c in allContoursSorted:
		rects.append(getBoundingRect(c, smallRect=small))

	for c in digitCntsBig:
		# extract the digit ROI
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(digits,(x,y),(x+w,y+h),(0,0,255),3)
	for c in digitCntsOnesBig:
		# extract the digit ROI
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(digits,(x,y),(x+w,y+h),(0,255,255),3)
	saveImg(digits, "digits", folder=folder, saveFig=saveFigs)

	result = ""
	for r in rects:
		result+=getNumberOfRectangle(r, thresh, colorImg, small=small, folder=folder, saveFig=saveFigs, print_=print_)

	return result

def checkCorrectness(big,small):
	if len(big) == 5 and len(small) == 3:
		if "?" not in big and "?" not in small:
			if big[0] == big[1] == "0":
				return True # first 2 big numers are 0!
	return False

def analyseImg(imgName, folder="", saveFigs=False, print_=False, skipCrop=False):
	cropped2, xR, yR = None, 0,0

	cropped2 = cv2.imread(imgName)
	rotated = rotate(cropped2, 2)
	xR, yR, c = rotated.shape
	cropped2 = rotated[12:xR-30, 1:yR-1]
	gray = cv2.cvtColor(cropped2, cv2.COLOR_BGR2GRAY)
	blure = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.adaptiveThreshold(blure, 255, 1, 1, 15, 4)
	saveImg(thresh, "thresh", folder=folder, saveFig=saveFigs)

	bigStr   = analyseImgPart(thresh[0:60, 0:195], cropped2[0:60, 0:195], small=False, folder=folder+"/Big", saveFigs=saveFigs, print_=print_)
	smallStr = analyseImgPart(thresh[0:42, 195:thresh.shape[1]], cropped2[0:42, 195:thresh.shape[1]], small=True, folder=folder+"/Small", saveFigs=saveFigs, print_=print_)
	textRes = bigStr+","+smallStr
	colorFinal = (10, 10 , 255)
	correct = (checkCorrectness(bigStr, smallStr))
	if correct:
		colorFinal = (30, 180 , 30)

	tmpIMG = cv2.putText(cropped2, textRes, (int(xR/4) ,int(yR/4)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colorFinal, 2, cv2.LINE_AA, False)
	saveImg(tmpIMG, "finalImg", folder=folder, saveFig=saveFigs)

	return textRes, tmpIMG, correct

def creation_date(path_to_file):
	import datetime
	s = path_to_file[path_to_file.find('cropped'):]
	s = s.replace("cropped", "").replace(".png", "")
	a = datetime.datetime.strptime("2023-08-"+s,"%Y-%m-%d-%H%M%S")
	return a
	# 0_cropped01-000018
	# 0_2023-07-25 21:13:33

def renameCreationDate(dpath):
	import datetime
	import shutil
	for filename in os.listdir(dpath):
		f = os.path.join(dpath, filename)
		t = creation_date(f)
		shutil.copyfile(f, "data/0_"+str(t)+".png")

def analyseFolder(dpath, resultFolder="", breakAfter=10000000):
	i = 0
	correctResults = []
	for filename in sorted(os.listdir(dpath)):
		f = os.path.join(dpath, filename)
		# checking if it is a file
		if os.path.isfile(f):
			text_result, imgResult, correct = analyseImg(f, saveFigs=False, folder="orginalDataResults", print_=False, skipCrop=True)
			saveImg(imgResult, filename, folder="orginalDataResults",saveFig=False)
			if correct:
				correctResults.append(text_result)
				print("Correct result:", filename, text_result, i)
				if len(resultFolder)>0: # save only correct imgs
					saveImg(imgResult, filename, folder="orginalDataResults",saveFig=False)
		i+=1
		if i==breakAfter:
			print("Finish analysing imgs afer", breakAfter)
			break
	print("Analysed", i, "files", "corect:", len(correctResults), str(round(i/len(correctResults),2))+"%")
	return correctResults
# For a single file do:
# text_result, imgResult = analyseImg("general_processingData/orginal2.jpg", folder="general_processingData",print_=True, saveFigs=True)
# print(text_result)

# For an already cropped image do:
#text_result, imgResult, correct = analyseImg("data/0_2023-08-03 20:00:22.png", folder="orginalDataResults",print_=True, saveFigs=True, skipCrop=True)
# print(text_result)


#TODO many errors in rectangle / bounding box detection! requires improvement!
# Analysed 698 files corect: 83 8.41%
analyseFolder("data/", resultFolder="orginalDataResults")


# executed only once to rename all files!
#renameCreationDate("data/")