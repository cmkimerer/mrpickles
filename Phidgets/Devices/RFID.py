"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.4'
__date__ = 'May 02 2008'

from threading import *
from ctypes import *
from Phidgets.Phidget import *
from Phidgets.PhidgetException import *
import sys

class RFID(Phidget):
    """This class represents a Phidget RFID Reader.
    
    All methods to read tags and set outputs on the RFID reader are implemented in this class.
    
    The Phidget RFID reader can read one tag at a time. Both tag and tagloss event handlers are provided,
    as well as control over the antenna so that multiple readers can exists in close proximity without interference.
    
    Extends:
        Phidget
    """
    def __init__(self):
        """The Constructor Method for the RFID Class
        """
        Phidget.__init__(self)
        
        hexArray = c_char*16
        self.__hexLookup = hexArray('0', '1', '2', '3', '4', 
            '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
        
        self.__outputChange = None
        self.__tagGain = None
        self.__tagLoss = None
        
        self.__onTagHandler = None
        self.__onTagLostHandler = None
        self.__onOutputChange = None
        
        self.dll.CPhidgetRFID_create(byref(self.handle))
        
        if sys.platform == 'win32':
            self.__OUTPUTCHANGEHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__TAGHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, POINTER(c_ubyte))
            self.__TAGLOSTHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, POINTER(c_ubyte))
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__OUTPUTCHANGEHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int)
            self.__TAGHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, POINTER(c_ubyte))
            self.__TAGLOSTHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, POINTER(c_ubyte))

    def getOutputCount(self):
        """Returns the number of outputs.
        
        These are the outputs provided by the terminal block. Older RFID readers do not have these outputs, and this method will return 0.
        
        Returns:
            The number of outputs available <int>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        outputCount = c_int()
        result = self.dll.CPhidgetRFID_getOutputCount(self.handle, byref(outputCount))
        if result > 0:
            raise PhidgetException(result)
        else:
            return outputCount.value

    def getOutputState(self, index):
        """Returns the state of an output.
        
        True indicated activated, False deactivated, which is the default.
        
        Parameters:
            index<int>: index of the output.
        
        Returns:
            The state of the output <boolean>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, of the index is out of range.
        """
        outputState = c_int()
        result = self.dll.CPhidgetRFID_getOutputState(self.handle, c_int(index), byref(outputState))
        if result > 0:
            raise PhidgetException(result)
        else:
            if outputState.value == 1:
                return True
            else:
                return False

    def setOutputState(self, index, state):
        """Sets the state of a digital output.
        
        True indicated activated, False deactivated, which is the default.
        
        Parameters:
            index<int>: the index of the output.
            state<boolean>: the state of the output.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or the index or state value are out of range.
        """
        if state == True:
            value = 1
        else:
            value = 0
        result = self.dll.CPhidgetRFID_setOutputState(self.handle, c_int(index), c_int(value))
        if result > 0:
            raise PhidgetException(result)

    def __nativeOutputChangeEvent(self, handle, usrptr, index, value):
        if self.__outputChange != None:
            if value == 1:
                state = True
            else:
                state = False
            self.__outputChange(OutputChangeEventArgs(index, state))
        return 0

    def setOnOutputChangeHandler(self, outputChangeHandler):
        """Sets the OutputChange Event Handler.
        
        The output change handler is a method that will be called when an output has changed.
        
        Parameters:
            outputChangeHandler: hook to the outputChangeHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__outputChange = outputChangeHandler
        self.__onOutputChange = self.__OUTPUTCHANGEHANDLER(self.__nativeOutputChangeEvent)
        result = self.dll.CPhidgetRFID_set_OnOutputChange_Handler(self.handle, self.__onOutputChange, None)
        if result > 0:
            raise PhidgetException(result)

    def getAntennaOn(self):
        """Returns the state of the antenna.
        
        True indicated that the antenna is active, False indicated inactive.
        
        Returns:
            The state of the antenna <boolean>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        antenna = c_int()
        result = self.dll.CPhidgetRFID_getAntennaOn(self.handle, byref(antenna))
        if result > 0:
            raise PhidgetException(result)
        else:
            if antenna.value == 1:
                return True
            else:
                return False

    def setAntennaOn(self, state):
        """Sets the state of the antenna.
        
        True turns the antenna on, False turns it off.
        The antenna if by default turned off, and needs to be explicitely activated before tags can be read.
        
        Control over the antenna allows multiple readers to be used in close proximity, as multiple readers will
        interfere with each other if their antenna's are activated simultaneously.
        
        Parameters:
            state<boolean>: desired state of the antenna.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or if the desired state is out of range.
        """
        if state == True:
            value = 1
        else:
            value = 0
        result = self.dll.CPhidgetRFID_setAntennaOn(self.handle, c_int(value))
        if result > 0:
            raise PhidgetException(result)

    def getLEDOn(self):
        """Returns the state of the onboard LED.
        
        This LED is by default turned off.
        
        Returns:
            The state of the LED <boolean>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        ledStatus = c_int()
        result = self.dll.CPhidgetRFID_getLEDOn(self.handle, byref(ledStatus))
        if result > 0:
            raise PhidgetException(result)
        else:
            if ledStatus.value == 1:
                return True
            else:
                return False

    def setLEDOn(self, state):
        """Sets the state of the onboard LED.
        
        True turns the LED on, False turns it off. The LED is by default turned off.
        
        Parameters:
            state<boolean>: the desired LED state.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached, or if the desired state value is out of range.
        """
        if state == True:
            value = 1
        else:
            value = 0
        result = self.dll.CPhidgetRFID_setLEDOn(self.handle, c_int(value))
        if result > 0:
            raise PhidgetException(result)

    def getLastTag(self):
        """Returns the last tag read.
        
        This method will only return a valid tag after a tag has been seen.
        This method can be used even after a tag has been removed from the reader.
        
        Returns:
            The last tage read <unsigned byte>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        lastTag = c_ubyte()
        result = self.dll.CPhidgetRFID_getLastTag(self.handle, byref(lastTag))
        if result > 0:
            raise PhidgetException(result)
        else:
            return lastTag.value

    def getTagStatus(self):
        """Returns the state of whether or not a tag is being read by the reader.
        
        True indicated that a tag is on (or near) the reader, False indicates that one is not.
        
        Returns:
            The tag read state <int>.
        
        Exceptions:
            PhidgetException: If this Phidget is not opened and attached.
        """
        tagStatus = c_int()
        result = self.dll.CPhidgetRFID_getTagStatus(self.handle, byref(tagStatus))
        if result > 0:
            raise PhidgetException(result)
        else:
            if tagStatus.value == 1:
                return True
            else:
                return False

    def __nativeTagGainEvent(self, handle, usrptr, tagValue):
        str = ""
        for i in range(5):
            str += self.__hexLookup[tagValue[i] / 16]
            str += self.__hexLookup[tagValue[i] % 16]
        
        if self.__tagGain != None:
            self.__tagGain(TagEventArgs(str))
        return 0

    def setOnTagHandler(self, tagHandler):
        """Sets the Tag Gained Event Handler.
        
        The tag gained handler is a method that will be called when a new tag is seen by the reader.
        The event is only fired one time for a new tag, so the tag has to be removed and then replaced before another tag gained event will fire.
        
        Parameters:
            tagHandler: hook to the tagHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__tagGain = tagHandler
        self.__onTagHandler = self.__TAGHANDLER(self.__nativeTagGainEvent)
        result = self.dll.CPhidgetRFID_set_OnTag_Handler(self.handle, self.__onTagHandler, None)
        if result > 0:
            raise PhidgetException(result)

    def __nativeTagLossEvent(self, handle, usrptr, tagValue):
        str = ""
        for i in range(5):
            str += self.__hexLookup[tagValue[i] / 16]
            str += self.__hexLookup[tagValue[i] % 16]
        
        if self.__tagLoss != None:
            self.__tagLoss(TagEventArgs(str))
        return 0

    def setOnTagLostHandler(self, tagLostHandler):
        """Sets the Tag Lost Event Handler.
        
        The tag lost handler is a method that will be called when a tag is removed from the reader.
        
        Parameters:
            tagLostHandler: hook to the tagLostHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__tagLoss = tagLostHandler
        self.__onTagLostHandler = self.__TAGLOSTHANDLER(self.__nativeTagLossEvent)
        result = self.dll.CPhidgetRFID_set_OnTagLost_Handler(self.handle, self.__onTagLostHandler, None)
        if result > 0:
            raise PhidgetException(result)
