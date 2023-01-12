#Paths
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

    centx,centy = centroid(image,threshold) # neglecting tip tilt 
    h,w = image.shape
    y = np.linspace(0,h-1,h)-centy
    x = np.linspace(0,w-1,w)-centx
    x,y = np.meshgrid(x,y)
    second = np.sum(image*(x**2+y**2))/np.sum(image)

    return second
#-----Some checks -----------
#----------------
minimi=[]
better = []
volt_buoni = []
volt_buoni_set = []

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
semi_path ='C:\\dm_control\\calibration_2018_11_22\\'
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
#ROI=np.asarray([357,394,1397,1421])
#ROI = np.asarray([844,868,1060,1070])
# ROI = np.asarray([845,865,1090,1110])
# ROI = np.asarray([830,880,1050,1090])
# ROI = np.asarray([839,874,1088,1108])
ROI = np.asarray([1010,1050,1099,1145])
roi_image = image[ROI[0]:ROI[1],ROI[2]:ROI[3]]
fig = plt.figure('Image ROI')
plt.imshow(roi_image, interpolation='none')
plt.show() 

#-----------------------------------original image acquisition------------------
# average on frames
threshold=0
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
original = image 

# save and show original image
fig = plt.figure(' Original Image ')
plt.imshow(original, interpolation='none')
plt.show()

im=Image.fromarray(original)
im.save(semi_path+'original.tif')    

#select ROI
start_image=original[ROI[0]:ROI[1],ROI[2]:ROI[3]]
fig = plt.figure('Start image')
plt.imshow(start_image, interpolation='none')
plt.show() 

#save ROI start
roi_start=Image.fromarray(original[ROI[0]:ROI[1],ROI[2]:ROI[3]])
roi_start.save(semi_path+'roi_start.tif')

#----------------------Voltage variables, min_secondmoment init-----------------
voltages = np.zeros(43)
voltages_max = np.zeros(43)
iterations= 300

min_secondmoment = secondmoment(start_image,threshold)
print str('secondmoment start'), min_secondmoment

#-----------------------------------Base voltages calculation-------------------

for i in range(iterations):

    voltages = np.copy(voltages_max)
    actuator = rnd.randint(0,39)

    #boolean = rnd.randint(0,1)
    #step = step_size[boolean]
    step = 10*(rnd.randint(0,1)-0.5) # step smaller that 5 volts 
    #volt=step*(rnd.random()-0.5)

    voltages[actuator] = voltages[actuator]+step
    dm.setvoltages(voltages)
    sleep(2)
    
    temp_image = np.zeros((height, width), dtype = np.float64)
    for k in range (average):
        uEye.mmc.clearCircularBuffer()
        sleep(.5)
        uEye.mmc.snapImage()
        temp_image += uEye.mmc.getImage()/float(average)
    temp_image=np.asarray(temp_image)
    temp_image = temp_image[ROI[0]:ROI[1],ROI[2]:ROI[3]]
    
    
    
    # sleep(.5)
    # uEye.mmc.clearCircularBuffer()
    # uEye.mmc.snapImage()
    # image = uEye.mmc.getImage()
    # image = image[342:394,1372:1421]

    min_secondmoment_new = secondmoment(temp_image,threshold)
    minimi.append(min_secondmoment_new)
    print str('for'), i, dm.getvoltages(), min_secondmoment_new

    #save in valtages max the optimized voltage (corresponds to reduced psf )
    if(min_secondmoment_new < min_secondmoment):
        min_secondmoment = min_secondmoment_new
        voltages_max = np.copy(voltages)
        # print  str('cond 1'),  i,  min_secondmoment, voltages_max
        better.append(temp_image)
        volt_buoni.append(voltages_max)
        volt_buoni_set.append(dm.getvoltages())
        # if(i>10):
        #     break
        
        
    #back to old voltages (since the new one corresponds to increased psf )
    else:
        
        dm.setvoltages(voltages_max)
        sleep(2)
        # new_image = np.zeros((height, width), dtype = np.float64)
        # for k in range (average):
        #     uEye.mmc.clearCircularBuffer()
        #     sleep(.5)
        #     uEye.mmc.snapImage()
        #     new_image += uEye.mmc.getImage()/float(average)
        # new_image = np.asarray(new_image)
        # new_image = new_image[ROI[0]:ROI[1],ROI[2]:ROI[3]]
        # min_secondmoment_new = secondmoment(new_image,threshold)

        # print  str('cond 2'), i, min_secondmoment_new, dm.getvoltages()
        # print  str('cond 2'),dm.getvoltages()
##        if min_secondmoment_new > min_secondmoment:
##            min_secondmoment=min_secondmoment_new

#--------------------------------Save base voltages-----------------------------
 # set voltage to have a flat DM
pickle.dump(voltages_max, open(semi_path+"optim_voltages.p", "wb"))
# dm.relax()
# sleep(2)
# dm.setvoltages(voltages_max)
# sleep(2)
#--------------------------------Acquire and save final image-------------------


for k in range (average):
    uEye.mmc.clearCircularBuffer()
    sleep(.5)
    uEye.mmc.snapImage()
    image += uEye.mmc.getImage()/float(average)
final = np.asarray(image)


fig = plt.figure(' Final Image ')
plt.imshow(final,interpolation='none')
plt.show()

im = Image.fromarray(final)
im.save(semi_path+'final.tif')

#some checks 
final_secondmoment = secondmoment(final[ROI[0]:ROI[1],ROI[2]:ROI[3]],threshold)
print str('final second_moment'), final_secondmoment

final_volt = dm.getvoltages()
print str('final volt'), final_volt



fig = plt.figure(' Final ROI ')
plt.imshow(final[ROI[0]:ROI[1],ROI[2]:ROI[3]],interpolation='none')
plt.show()

#save ROI final
roi_final=Image.fromarray(final[ROI[0]:ROI[1],ROI[2]:ROI[3]])
roi_final.save(semi_path+'roi_final.tif')

uEye.close()

plt.figure('minimi')
plt.plot(minimi, 'bs-')
plt.show()