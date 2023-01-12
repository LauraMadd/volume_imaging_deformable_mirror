import clr

clr.AddReference("System.Runtime.InteropServices")
import sys
# sys.path.append("System.Runtime.InteropServices")
##for 32 
# sys.path.append('C:\Program Files (x86)\Thorlabs\Deformable Mirror')

# #path for 64 bit  
# 
# #sys.path.append('C:\Program Files (x86)\Microsoft.NET\Primary Interop Assemblies') 
# sys.path.append('C:\Program Files\IVI Foundation\VISA\VisaCom64\Primary Interop Assemblies')
# # needed for Thorlabs.TLDFM_64.Interop
##for 32
# sys.path.append('C:\Program Files (x86)\IVI Foundation\VISA\VisaCom\Primary_Interop_Assemblies')
# #needed for Ivi.Visa.Interop
# sys.path.append('C:\Program Files\IVI Foundation\VISA\Win64\Bin')
####paolo lib
sys.path.append('C:\dm_control')
from System import Array,Double,Boolean
import System.Runtime.InteropServices
# from sys import Array,Double,Boolean
# import sys.Runtime.InteropServices
import Thorlabs.TLDFM_64.Interop
import Thorlabs.TLDFM_64.Interop.NativeMethods
import Ivi.Visa.Interop

import numpy
import time



class dm:

    def __init__(self):
	print ("asd")
        rm=Ivi.Visa.Interop.ResourceManager()

        resourcelist=rm.FindRsrc(Thorlabs.TLDFM_64.Interop.TLDFM.FindPattern)

        self.dm=Thorlabs.TLDFM_64.Interop.TLDFM(resourcelist[0],True,True)

        self.dm.reset()

        self.dm.enable_hysteresis_compensation(Thorlabs.TLDFM_64.Interop.DMPTarget.Both,True)


        offsetact=Array[Double]([100.0]*40)

        offsettiptilt=Array[Double]([100.0]*3)

        self.dm.set_voltages(offsetact,offsettiptilt)


    def setvoltages(self,volt):
        """ function to add to each actuator voltage 100. If the  result is
            bigger than 200, put 200: if result less 0 put 0.
        """
        # initialization @ 100 defaulta value
        if volt.shape[0]==40:
            volt=volt+100.0
            # if negative input --> not good
            if volt[volt<0.0].size:
                print "out of bounds"
            volt[volt<0.0]=0.0
            if volt[volt>200.0].size:
                print "out of bounds"
            volt[volt>200.0]=200.0

            voltactarray=Array[Double](volt)
            volttiptiltarray=Array[Double](numpy.zeros(3))
            # why 43????
        elif volt.shape[0]==43:

            voltact=volt[0:40]+100.0
            if voltact[voltact>200.0].size:
                print "out of bounds"
            voltact[voltact>200.0]=200.0
            if voltact[voltact<0.0].size:
                print "out of bounds"
            voltact[voltact<0.0]=0.0

            volttiptilt=volt[40:43]+100.0
            if volttiptilt[volttiptilt>200.0].size:
                print "out of bounds"
            volttiptilt[volttiptilt>200.0]=200.0
            if volttiptilt[volttiptilt<0.0].size:
                print "out of bounds"
            volttiptilt[volttiptilt<0.0]=0.0


            voltactarray=Array[Double](voltact)
            volttiptiltarray=Array[Double](volttiptilt)
        else:
            print "volt array size not correct"

        self.dm.set_voltages(voltactarray,volttiptiltarray)


    def relax(self):
        """ Function to shut off the mirror.
        """
        for i in range(1000):
            volt=100.0*numpy.ones(43)*numpy.exp(-float(i)/200.0)*\
                                        numpy.sin(2*numpy.pi*float(i)/50.0)


            self.setvoltages(volt)

            time.sleep(0.002)






    def getvoltages(self):
        voltact=Array[Double]([0.0]*40)

        volttiptilt=Array[Double]([0.0]*3)

        self.dm.get_voltages(voltact,volttiptilt) # function to read voltages.

        voltages=numpy.zeros(43)

        for i in range(40):
            voltages[i]=voltact[i]

        for i in range(3):
            voltages[40+i]=volttiptilt[i]

        return voltages




if __name__=="__main__":
    thor=dm()
    thor.setvoltages(numpy.ones(43)*0.0)
