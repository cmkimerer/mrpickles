#!/usr/bin/env python

"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.4'
__date__ = 'May 02 2008'

#Basic imports
from ctypes import *
import sys
from time import sleep
#Phidget specific imports
from Phidgets.PhidgetException import *
from Phidgets.Events.Events import *
from Phidgets.Devices.Servo import Servo

#Create an servo object
servo = Servo()

#Information Display Function
def DisplayDeviceInfo():
    print "|------------|----------------------------------|--------------|------------|"
    print "|- Attached -|-              Type              -|- Serial No. -|-  Version -|"
    print "|------------|----------------------------------|--------------|------------|"
    print "|- %8s -|- %30s -|- %10d -|- %8d -|" % (servo.isAttached(), servo.getDeviceType(), servo.getSerialNum(), servo.getDeviceVersion())
    print "|------------|----------------------------------|--------------|------------|"
    print "Number of motors: %i" % (servo.getMotorCount())
    return 0

#Event Handler Callback Functions
def ServoAttached(e):
    attached = e.device
    print "Servo %i Attached!" % (attached.getSerialNum())
    return 0

def ServoDetached(e):
    detached = e.device
    print "Servo %i Detached!" % (detached.getSerialNum())
    return 0

def ServoError(e):
    print "Phidget Error %i: %s" % (e.eCode, e.description)
    return 0

def ServoPositionChanged(e):
    print "Motor %i Current Position: %f" % (e.index, e.position)
    return 0

#Main Program Code
try:
    servo.setOnAttachHandler(ServoAttached)
    servo.setOnDetachHandler(ServoDetached)
    servo.setOnErrorhandler(ServoError)
    servo.setOnPositionChangeHandler(ServoPositionChanged)
except PhidgetException, e:
    print "Phidget Exception %i: %s" % (e.code, e.message)
    print "Exiting...."
    exit(1)

print "Opening phidget object...."

try:
    servo.openPhidget()
except PhidgetException, e:
    print "Phidget Exception %i: %s" % (e.code, e.message)
    print "Exiting...."
    exit(1)

print "Waiting for attach...."

try:
    servo.waitForAttach(10000)
except PhidgetException, e:
    print "Phidget Exception %i: %s" % (e.code, e.message)
    try:
        servo.closePhidget()
    except PhidgetException, e:
        print "Phidget Exception %i: %s" % (e.code, e.message)
        print "Exiting...."
        exit(1)
    print "Exiting...."
    exit(1)
else:
    DisplayDeviceInfo()

try:
    print "Move to position 10.00"
    servo.setPosition(0, 10.00)
    sleep(1)    
    print "Move to position 50.00"
    servo.setPosition(0, 50.00)
    sleep(1)
    print "Move to position 100.00"
    servo.setPosition(0, 100.00)
    sleep(1)
    print "Move to position 150.00"
    servo.setPosition(0, 150.00)
    sleep(1)
    print "Move to position 200.00"
    servo.setPosition(0, 200.00)
    sleep(1)
    print "Move to position 0.00"
    servo.setPosition(0, 0.00)
except PhidgetException, e:
    print "Phidget Exception %i: %s" % (e.code, e.message)
    print "Exiting...."
    exit(1)

print "Press Enter to quit...."

chr = sys.stdin.read(1)

print "Closing..."

try:
    servo.closePhidget()
except PhidgetException, e:
    print "Phidget Exception %i: %s" % (e.code, e.message)
    print "Exiting...."
    exit(1)

print "Done."
exit(0)
