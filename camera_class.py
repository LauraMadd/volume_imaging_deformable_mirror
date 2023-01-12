import sys
sys.path.append('C:\Program Files\Micro-Manager-1.4')
import MMCorePy
# import cv2
import time
import numpy as np
import hands_on_image as hoi
reload(hoi)
from PySide import QtGui, QtCore
import math_library as mtm
reload(mtm)
from datetime import datetime

#
# INFOS
# There is a minimum ROI dimension for te IDS uEye.
# defined by two global variables at the start, so pay attention to this detail
# . . . . . . . . . . . . . . . .  . . . . . . . . . . . . . . . . . . . . . . .
# ROI minimum dimension:
_min_height = 3
_min_width = 257
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

class camera(object):
    def __init__(self, initialization):
        self.mmc = MMCorePy.CMMCore()
        self.name = initialization[0]
        self.mmc.loadDevice(*initialization)
        self.mmc.initializeDevice(self.name)
        self.mmc.setCameraDevice(self.name)
        self.mmc.setProperty('uEye', 'Trigger', 'off')
        self.mmc.setProperty('uEye', 'Gain', '100')
        # no trigger present, can be changed

        # vectorial notation: x = number of rows, y = num. of col
        self.x = self.mmc.getImageHeight()
        self.y = self.mmc.getImageWidth()

        self.stack = np.zeros((1, self.x, self.y))
        self.roi_width = int(self.mmc.getImageHeight())
        self.roi_height = int(self.mmc.getImageWidth())
        self.roi_x0 = 0
        self.roi_y0 = 0
        self.iter_roi_x0 = 0
        self.iter_roi_y0 = 0
        self.snapped = np.zeros((1,1))
        self.converted_flag = True

    def print_properties(self):
        ''' print all properties. Change the mutable ones with:
            self.mmc.setProperty('device_name', '' property_name'. 'value')
        '''
        prop_ro = list()
        print '\nDEVICE PROPERTIES LIST:\n'
        for prop in self.mmc.getDevicePropertyNames(self.name):
            if self.mmc.isPropertyReadOnly(self.name, prop):
                prop_ro.append(prop)
            else:
                low = self.mmc.getPropertyLowerLimit(self.name, prop)
                up =self.mmc.getPropertyUpperLimit(self.name, prop)
                available_vals=\
                ', '.join(self.mmc.getAllowedPropertyValues(self.name, prop))
                if(available_vals):
                    print(str(prop) +'= '+ \
                                    self.mmc.getProperty(self.name, prop)+\
                                    ' --> possibe values from this set: {' \
                                                    + available_vals + '}\n')
                else:
                    print(str(prop) +'= '+ \
                                    self.mmc.getProperty(self.name, prop)\
                                    + ', choose from '+ \
                                            str(low)+ ' to ' + str(up) +' \n')
        print '\nRead-only prop:\n', prop_ro
        return None

    def select_roi(self):
        # proportion for tight measures
        if (self.converted_flag == False):
            self.roi_y0 = self.iter_roi_x0 + self.faino.xStart
            self.roi_x0 = self.iter_roi_y0 + self.faino.yStart
            width = self.faino.yEnd - self.faino.yStart
            height = self.faino.xEnd - self.faino.xStart
            print self.roi_x0,self.roi_y0, width, height
            self.mmc.setROI(int(self.roi_x0), int(self.roi_y0), \
                                                        int(width), int(height))
            self.roi_height = height
            self.roi_width = width
            self.iter_roi_x0 = self.roi_x0
            self.iter_roi_y0 = self.roi_y0
        else:
            self.roi_y0 = self.iter_roi_x0 + self.faino.xStart * 2
            self.roi_x0 = self.iter_roi_y0 + self.faino.yStart * 2
            width = (self.faino.yEnd - self.faino.yStart) *2
            height = (self.faino.xEnd - self.faino.xStart) *2
            print self.roi_x0,self.roi_y0, width, height
            self.mmc.setROI(int(self.roi_x0), int(self.roi_y0), \
                                                        int(width), int(height))
            self.roi_height = height
            self.roi_width = width
            self.iter_roi_x0 = self.roi_x0
            self.iter_roi_y0 = self.roi_y0

        return None

    def clear_roi(self):
        self.mmc.clearROI()
        self.roi_width = self.y
        self.roi_height = self.x
        self.roi_x0, self. roi_y0 = 0, 0
        self.converted_flag = False
        self.iter_roi_x0 = 0
        self.iter_roi_y0 = 0
        return None


    def snap(self, show = True, snap_label = 'default'):
        ''' Snap an image. If show == True (default) it shows a PyQt label with
        the image, eventually resized if too big; on this panel, a ROI can be
        selected: just draw a rectangle and the call the method select_roi().
        '''
        self. mmc.snapImage()
        self.snapped = self.mmc.getImage()

        if(show):
            # careful: from 16 to 8bit conversion just to use PyQt
            # the actual image remain 16bit
            if (self.roi_width > 1000 or self.roi_height > 1000):
                print '\nmore than 1000 pixels:\n\
                                preview downsized to be seen comfortably.\n'
                converted = mtm.rebin(self.snapped, [self.snapped.shape[0]/2, \
                                        self.snapped.shape[1]/2])
                self.converted_flag = True
                converted  =((converted- converted.min()) /\
                    (converted.ptp() / 255.0)).astype(np.uint8)
                result = QtGui.QImage(converted.data, converted.shape[1], \
                        converted.shape[0], QtGui.QImage.Format_Indexed8)
                # call classe hands_on_image, basically a modified PyQt label,
                # to hold an the image and select a roi.
                self.faino = hoi.hands_on_image(result)
                self.faino.resize(converted.shape[1],converted.shape[0])
                self.faino.show()
            else:
                converted  =((self.snapped - self.snapped.min()) /\
                    (self.snapped.ptp() / 255.0)).astype(np.uint8)
                result = QtGui.QImage(converted.data, converted.shape[1], \
                        converted.shape[0], QtGui.QImage.Format_Indexed8)
                self.faino = hoi.hands_on_image(result)
                self.faino.resize(converted.shape[1],converted.shape[0])
                self.faino.show()
                self.converted_flag = False
        return None
# 
#     def show_video(self):
#         """It shows a video until kwy is pressed
#         """
#         cv2.namedWindow('Press any key to close', cv2.WINDOW_NORMAL)
#         cv2.resizeWindow('Press any key to close', 800, 600)
#         self.mmc.startContinuousSequenceAcquisition(1)
#         while (True):
#             frame = self.mmc.getLastImage()
#             if self.mmc.getRemainingImageCount() > 0:
#                 frame = self.mmc.getLastImage()
#                 cv2.imshow('Press any key to close', frame)
#             else:
#                 print('No frame')
#             if cv2.waitKey(20) >= 0:
#                 break
#         cv2.destroyAllWindows()
#         self.mmc.stopSequenceAcquisition()
#         return None

    def record_video(self, frames_number = 10):
        """
        -- as fast as Exposure allows
        -- time is not perfect...
        """
        count = 0
        if (self.roi_width != 0):
            self.stack = np.zeros((frames_number, \
                                            self.roi_width, self.roi_height ))
        else:
            self.stack = np.zeros((frames_number, self.y, self.x))
            #never in this
        self.mmc.clearCircularBuffer()
        self.mmc.prepareSequenceAcquisition(self.name)
        self.mmc.startContinuousSequenceAcquisition(1)
        while (count < frames_number):
            start = time.time()
            while self.mmc.getBufferTotalCapacity()==\
                                            self.mmc.getBufferFreeCapacity():
                pass
            self.stack[count, :, :] = self.mmc.popNextImage()
            count +=1
            if (time.time()-start > 0.):
                print 'fps: ', 1./(time.time()-start), '\n'
                sys.stdout.flush()
        self.mmc.stopSequenceAcquisition()

        return None

    def record_video_2(self, frames_number, interval = 1.):
        '''
        Probably works as fast as possible with the Exposure,
        waiting as it should between acquisitions. But I cna-t measure
        a real frame rate
        '''
        count = 0
        if (self.roi_width != 0):
            self.stack = np.zeros((frames_number, \
                                            self.roi_height, self.roi_width))
        else:
            self.stack = np.zeros((frames_number, self.x, self.y))
        self.mmc.clearCircularBuffer()
        self.mmc.prepareSequenceAcquisition(self.name)
        self.mmc.startContinuousSequenceAcquisition(1)
        while (count < frames_number):
            start = time.time()
            while ((time.time()-start) < interval):
                pass
            start2 = datetime.now().microsecond
            self.mmc.clearCircularBuffer()
            while self.mmc.getBufferTotalCapacity()==\
                                            self.mmc.getBufferFreeCapacity():
                pass
            stop = datetime.now().microsecond
            self.stack[count, :, :] = self.mmc.popNextImage()
            count +=1
            #if (stop-start2 > 0.):
            print 'ms: ', (stop-start2)/1000., '\n'
            sys.stdout.flush()
        self.mmc.stopSequenceAcquisition()

        return None

    def close(self):
        self.mmc.reset()
        return None

#-------------------------------------------------------------------------------
#test --> comment-out to use this as external library
#-------------------------------------------------------------------------------
# cam = camera(['uEye', 'IDS_uEye', 'IDS uEye'])
# # cam.mmc.setExposure(1.)
# cam.print_properties()
#video = cam.record_video()
#cam.close()
