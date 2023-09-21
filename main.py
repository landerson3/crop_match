from __future__ import print_function
import os
import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
MAX_FEATURES = 70000
GOOD_MATCH_PERCENT = 0.005
 
def alignCrop(im1, im2, name=None):
	# Convert images to grayscale
	im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
	im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
	im1Gray = cv2.convertScaleAbs(im1Gray,1,1.1)
	# im2Gray = cv2.convertScaleAbs(im2Gray,1,1)

	# Detect ORB features and compute descriptors.
	orb = cv2.ORB_create(MAX_FEATURES)
	keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
	keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

	# Match features.
	matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
	matches = list(matcher.match(descriptors1, descriptors2, None)[0:])

	# Sort matches by score
	matches.sort(key=lambda x: x.distance, reverse=False)

	# Remove not so good matches
	numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
	if numGoodMatches < 4: numGoodMatches = 10 # override if less than 4
	matches = matches[:numGoodMatches]

	# find left-most & right-most values of keypoints in im1
	# left = keypoints1[0].pt[0]
	# right = keypoints1[0].pt[0]
	# top = keypoints1[0].pt[1]
	# bottom = keypoints1[0].pt[1]
	# for i,v in enumerate(keypoints1):
	# 	left = v.pt[0] if v.pt[0] < left else left
	# 	right = v.pt[0] if v.pt[0] > right else right
	# 	top = v.pt[1] if v.pt[1] < left else left
	# 	bottom = v.pt[1] if v.pt[1] > right else right
	

	# Draw top matches
	imMatches = cv2.drawMatches(im1Gray, keypoints1, im2Gray, keypoints2, matches, None)
	cv2.imwrite(f"/Users/landerson2/Match_Crop/Matches/{name}_matches.jpg", imMatches)

	# Extract location of good matches
	points1 = np.zeros((len(matches), 2), dtype=np.float32)
	points2 = np.zeros((len(matches), 2), dtype=np.float32)

	for i, match in enumerate(matches):
		points1[i, :] = keypoints1[match.queryIdx].pt
		points2[i, :] = keypoints2[match.trainIdx].pt
	
	

	width,height,_ = im1.shape
	# dummy_image = np.zeros((im2.shape[0], im2.shape[1] , 3), dtype=np.float32)
	
	h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
	print(h)
	# im1Reg = cv2.warpPerspective(dummy_image, h, (width, height))
	# print(im1Reg.shape)
	
	tl = h @ [0,0,1]
	tr = h @ [width,0,1]
	bl = h @ [0,height,1]
	br = h @ [width,height,1]

	# tl = [0,0,1] @ h
	# tr = [width,0,1] @ h
	# bl = [0,height,1] @ h
	# br = [width,height,1] @ h

	top_left = [tl[0]/tl[-1],
				tl[1]/tl[-1]]
	top_right = [tr[0]/tr[-1],
				tr[1]/tr[-1]]
	bottom_left = [bl[0]/bl[-1],
				bl[1]/bl[-1]]
	bottom_right = [br[0]/br[-1],
				br[1]/br[-1]]
	

	# print(top_left, top_right, bottom_left, bottom_right)
	
	min_x = int((top_left[0]+bottom_left[0])/2)
	min_y = int((top_left[1]+top_right[1])/2)
	max_x = int((top_right[0]+bottom_right[0])/2)
	max_y = int((bottom_left[1]+bottom_right[1])/2)

	if min_x > max_x or min_y > max_y:
		return None
		print('break')
		

	crop = [
		min_x, min_y, max_x, max_y
	]
	return crop


	print(im1.shape)
	print(im2.shape)

	if width < im2.shape[1]: width = im2.shape[1]
	# crop = [avg_x, avg_y, avg_x+width,avg_y+height]
	crop = [-left, avg_y, -left+width, avg_y+height]
	return crop

	
	# print(points1)
	# Find homography
	h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

	# Use homography
	height, width, channels = im2.shape
	im1Reg = cv2.warpPerspective(im1, h, (width, height))

	return im1Reg, h

def transfer_crop(refFilename, imFilename, destination = os.path.expanduser("~/Match_Crop/results")):
	# Read reference image
	
	print("Reading reference image : ", refFilename)
	imReference = cv2.imread(refFilename, cv2.IMREAD_COLOR)

	# Read image to be aligned
	print("Reading image to align : ", imFilename)
	im = cv2.imread(imFilename, cv2.IMREAD_COLOR)



	# match aspect ratio
	w,h,_ = imReference.shape
	aspect_ratio = w/h
	# orientation = 'horizontal' if im.shape[0]>im.shape[1] else 'vertical'
	# if orientation = 'horizontal':
		# im = cv2.resize(im, ())
	# else:
	
	im = cv2.resize(im, (int(im.shape[0]*aspect_ratio), int(im.shape[1]*aspect_ratio)))
		
	_crop = alignCrop(im, imReference, os.path.basename(refFilename).split('/')[-1])

	
	
	if _crop == None: return None # skip errors in homography for now.


	old_image = Image.open(refFilename)
	im_res = old_image.crop(_crop)
	# im_res.show()
	if destination != None:
		name =  os.path.basename(refFilename).split('/')[-1]
		try:
			im_res.save(os.path.join(destination,f"{name}"))
		except:
			pass
	else:
		im_res.save(f"{refFilename[0:-4]}_cropped{refFilename[-4:]}")






# total_match_files = {}
# for root, dirs, files in os.walk('/Users/landerson2/Match_Crop/test_files'):
# 	for file in files:
# 		if '_RHR' in file:
# 			if os.path.exists(os.path.join(root,file[0:-8]+".png")):
# 				total_match_files[file[0:-4]] = [os.path.join(root,file), os.path.join(root,file[0:-8]+".png")]



# x = 0
# for item in total_match_files.keys():
# 	x+=1
# 	if x >1000: break
# 	if total_match_files[item] == None: continue
# 	if len(total_match_files[item]) != 2: continue
# 	rhr, original = total_match_files[item]
# 	transfer_crop(rhr, original)