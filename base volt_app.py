import sys
if "C:\Micro-Manager-1.4" not in sys.path:
    sys.path.append("C:\Micro-Manager-1.4")
    # sys.path.append("C:\dm_control")
#Useful classes
import camera_class as cam 
import dmctr # class for DM control
# import MMCorePy
#useful libraries
from PIL import Image
import numpy as np
import dmctr # class for DM control
import matplotlib.pyplot as plt
import random as rnd
from time import sleep
import pickle


#--------------- Functions------------------------------------------------------
def centroid(image,threshold):
    """Calculation of cemtroids weighted on the illumination intensity (see eq 3.2)
    """
   
    # threshold image
    image[image<threshold] = 0.
    #meshgrid with subregions SH
    h,w = image.shape
    y = np.linspace(0,h-1,h)
    x = np.linspace(0,w-1,w)
    x,y = np.meshgrid(x,y)
    #Calculation of centroid coord (weighted on illumination see eq 3.2 report)
    avg_x = np.sum(x*image)/np.sum(image)
    avg_y = np.sum(y*image)/np.sum(image)

    return avg_x,avg_y

def secondmoment(image,threshold):
    """Calculation of second moment of the image
    """
# put as x y shape image 

    centx,centy = centroid(image,threshold)
    h,w = image.shape
    y = np.linspace(0,h-1,h)-centy
    x = np.linspace(0,w-1,w)-centx
    x,y = np.meshgrid(x,y)
    second = np.sum(image*(x**2+y**2))/np.sum(image)

    return second

#---------------------Camera initialization-------------------------------------
uEye = cam.camera(['uEye', 'IDS_uEye', 'IDS uEye'])
uEye.mmc.setProperty('uEye', 'Gain', '100')
uEye.mmc.setProperty('uEye', 'Trigger', 'off')

uEye.mmc.setProperty('uEye', 'Exposure', '0.1')

#----------------------Mirror init----------------------------------------------
dm = dmctr.dm()
sleep(2)
print str('mirror init'), dm.getvoltages()
#relazation
dm.relax()
sleep(2)
print str('mirror relax'), dm.getvoltages()
dm.setvoltages(np.zeros((43)))
sleep(2)
print str('mirror zero'), dm.getvoltages()
#-------------------------Set folder for data-----------------------------------
semi_path ='C:\\dm_control\\calibration_2018_11_19\\'
#------------------------------Check on image acquisition-----------------------
# sleep(.5)

uEye.mmc.clearCircularBuffer()
uEye.mmc.snapImage()
image = uEye.mmc.getImage()

image = np.asarray(image)
fig = plt.figure('Image total FOV')
plt.imshow(image, interpolation='none')
plt.show()

#set ROI 

ROI = np.asarray([845,883,1080,1100])
roi_image = image[ROI[0]:ROI[1],ROI[2]:ROI[3]]
fig = plt.figure('Image ROI')
plt.imshow(roi_image, interpolation='none')
plt.show() 


#-------------------Acquisition start image-------------------------------------
threshold=5
average=3
height = int(uEye.mmc.getImageHeight())
width =  int(uEye.mmc.getImageWidth())
image = np.zeros((height, width), dtype = np.float64)


for k in range (average):
    uEye.mmc.clearCircularBuffer()
    sleep(.5)
    uEye.mmc.snapImage()
    image += uEye.mmc.getImage()/float(average)
image = np.asarray(image)
im_start = image 


roi_image = image[ROI[0]:ROI[1],ROI[2]:ROI[3]]
fig = plt.figure('Image ROI')
plt.imshow(roi_image, interpolation='none')
plt.show()




# calculation start second moment
start_secondmoment = secondmoment(roi_image,threshold)
print str('start second_moment'),start_secondmoment




#-----------------------------Set base voltages_________________________________
base_voltages = pickle.load(open(semi_path+"optim_voltages.p", "rb"))   
dm.setvoltages(base_voltages)
sleep(2)
#---------------------Image acquisition-----------------------------------------

for k in range (average):
    uEye.mmc.clearCircularBuffer()
    sleep(.5)
    uEye.mmc.snapImage()
    image += uEye.mmc.getImage()/float(average)
image = np.asarray(image)
im_calibrated = image 

# save and show calibrated image
fig = plt.figure(' Calibrated ')
plt.imshow(im_calibrated, interpolation='none')
plt.show()

im=Image.fromarray(im_calibrated)
im.save(semi_path+'im_calibrated.tif')    

#select ROI
calibrated_roi=im_calibrated[ROI[0]:ROI[1],ROI[2]:ROI[3]]
fig = plt.figure('Calibrated ROI')
plt.imshow(calibrated_roi, interpolation='none')
plt.show() 


# calculation final second moment
final_secondmoment = secondmoment(calibrated_roi,threshold)
print str('final second_moment'), final_secondmoment
uEye.close()