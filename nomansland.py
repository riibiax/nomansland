#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
  import os, cv, Image, urllib2
  from reportlab.pdfgen import canvas
  from reportlab.lib.units import inch, cm
  from bs4 import BeautifulSoup
except ImportError:
  print "You should install some modules\n"

###open_url##########################################################
def open_url(urlname):
    return urllib2.urlopen(urllib2.Request(urlname)).read()

###wget_image########################################################
def wget_image(image, src, directory):
  string = "wget -O "+ directory+"/" +image+" " + src
  os.system(string)

###check_exist#######################################################
def check_exist(file_name):
  try:
    with open(file_name) as f:
    	return True
  except IOError as e:
    return False

###scan_image########################################################
def scan_image(picture):

	capture= cv.CaptureFromFile("images/"+picture)

	#width = capture.width
	#height = capture.height


	#cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,width)    

	#cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,height) 

	#result = cv.CreateImage((width,height),cv.IPL_DEPTH_8U,3) 


	def HumanDetection(image):
		files_haar = [cv.Load("haarcascade_frontalface_alt.xml"),cv.Load("haarcascade_fullbody.xml"),cv.Load("haarcascade_lowerbody.xml"), cv.Load("haarcascade_profileface.xml"), cv.Load("haarcascade_upperbody.xml")]
		min_size = (10,10)
		image_scale = 2
		haar_scale = 1.2
		min_neighbors = 2
		haar_flags = 0

		# Allocate the temporary images
		gray = cv.CreateImage((image.width, image.height), 8, 1)
		smallImage = cv.CreateImage((cv.Round(image.width / image_scale),cv.Round (image.height / image_scale)), 8 ,1)

		# Convert color input image to grayscale
		cv.CvtColor(image, gray, cv.CV_BGR2GRAY)

		# Scale input image for faster processing
		cv.Resize(gray, smallImage, cv.CV_INTER_LINEAR)

		# Equalize the histogram
		cv.EqualizeHist(smallImage, smallImage)

		for file_haar in files_haar:
		# Detect the faces

			humans = cv.HaarDetectObjects(smallImage, file_haar, cv.CreateMemStorage(0),
			haar_scale, min_neighbors, haar_flags, min_size)

			if humans:
				return True
	
		return False

	img = cv.QueryFrame(capture)
	result = HumanDetection(img)

	return result
###removeNonAscii####################################################
def removeNonAscii(s):
 return "".join(i for i in s if ord(i)<128)

###Main##############################################################
os.system('clear')
c = canvas.Canvas('poster.pdf')
image_width = 105
image_height = 77
x = 0
y = 0
limit =24
total_height=4620

print "\n\n*** Welcome to the No Man Landscape script ***\n"
print "\n** Loading.. **\n"  
number = 0
print "\n connecting to the website\n"
html_doc = open_url("http://fr.swisswebcams.ch/verzeichnis/Toutes/suisse/ort")
print "\n first soup\n"
soup = BeautifulSoup(html_doc)
print "\n finding elements in menu\n"
menu = soup.find_all(id="VERZEICHNIS-pagination_top")
print "\n finding links in menu\n"
top_menu = menu[0].find_all("a")
for a in top_menu: 
	url_a = a.get('href')
	print "\nTop menu page "+ url_a+"\n"

	if not url_a.startswith("http"):
	 	url_a = "http://fr.swisswebcams.ch" + url_a
	print url_a
	html_a = open_url(url_a)
	soup_a = BeautifulSoup(html_a)
	links = soup_a.find_all("a", class_="thumbnail")
	for link in links:
		number = number +1
	  	url = link.get('href')
 	  	if not url.startswith("http"):
   		 	url = "http://fr.swisswebcams.ch" + url
   		print "\nURL " + url +"\n"
	 	html_link = open_url(url)
	 	soup_link = BeautifulSoup(html_link)
		images = soup_link.find_all(id="WEBCAM-bild")

		for found in images:
			skip=False
			alt = found.get('alt')
			alt= alt.replace(" ", "")
			alt= alt.replace("/", "")
			alt= alt.replace(".", "")
			alt= alt.replace(":", "")
			alt= alt.replace(";", "")
			alt= alt.replace("(", "")
			alt= alt.replace(")", "")
			alt= alt.replace("`", "")
			alt= alt.replace("&", "")
			alt= alt.replace("'", "")
			alt= alt.replace(",", "")
			alt = removeNonAscii(alt)
			alt= alt[:30]
 			file_image = alt+str(number)
 			print "\nSaved\n" + file_image +"\n"
 			print "\nURL IMAGE\n" + found.get('src') +"\n"
			wget_image(file_image, found.get('src'),"images")

      		if not check_exist("good_images/"+file_image):
      				present = scan_image(file_image)
      				if not present:
      					string = "cp images/"+file_image+" good_images/"+file_image
      					os.system(string)
      					print "\nNot present\n" + file_image +"\n"
      				else:
      					string = "cp images/"+file_image+" bad_images/"+file_image
      					os.system(string)
      					print "\nHuman presence on \n" + file_image +"\n"
      					skip=True
      		else:
      			print "\nAlready present\n" + file_image +"\n"

      		if not skip:
      			c.drawImage("good_images/"+file_image, x*image_width, y*image_height, image_width, image_height)
      			if x<limit:
      				x = x + 1
      			else:
      				y = y + 1
      				x = 0
      				total_height= y*image_height

total_height= (y-1)*image_height
c.setPageSize((2520, total_height))
c.showPage()
c.save()
print "\n\n*** END ***\n"
