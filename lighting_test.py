import sys, io, requests, os
from PIL import Image
from  transfer_crop import transfer_crop
# take a csv in the format of (non-RHR_BCC_Name, gx_finals_path) and save GX Final PNGs on the local
csv_file = sys.argv[1] if len(sys.argv)>1 else '/Users/landerson2/Match_Crop/lighting_input.csv'
WIDTH = 4000
MAX_LONG_SIDE = 4000
URL_EXTENSION = '&fmt=png-alpha&qlt=100,1&op_sharpen=0&resMode=sharp2&op_usm=0,0,0,0&iccEmbed=0&printRes=72&bfc=off'


def build_url(file, server = "rhis", rhr = False, width=WIDTH):
	if "rhbc" in file or "rhtn" in file or file[0:2].lower() =='tn' or file[0:2].lower() == "bc":
		server = "rhbcis"
	if rhr:
		url = f"https://media.restorationhardware.com/is/image/{server}/{file}_RHR?wid={width}{URL_EXTENSION}" 
	else:
		url = f"https://media.restorationhardware.com/is/image/{server}/{file}?wid={width}{URL_EXTENSION}"
	return url

def constrain_size(image):
	width, height = image.size
	lside = width if width>height else height
	new_width = round(width * (MAX_LONG_SIDE/lside))
	new_height = round(height * (MAX_LONG_SIDE/lside))
	# print(new_width,new_height)
	image = image.resize((new_width,new_height))
	return image

def trim(im):
	im2 = im.crop(im.getbbox())
	im2 = constrain_size(im2)
	return im2

with open(csv_file) as csv:
	for i,_ in enumerate(csv.readlines()):
		if i==0: continue
		if i > 2 : break ## TESTING
		bcc_name, gx_path = _.replace('"',"").split(",")
		gx_path = f'/Volumes/{gx_path.replace(":","/")}'.strip()
		gx_filename = os.path.basename(gx_path)
		url = build_url(bcc_name)
		response = requests.get(url)
		if response.status_code > 300: continue ## need to log later
		bcc_im = trim(Image.open(io.BytesIO(response.content)))
		bcc_file_path = bcc_im.save(f'/tmp/{bcc_name}.png')
		transfer_crop(bcc_file_path,gx_path,os.path.expanduser('~/Desktop/Output'))
		
		