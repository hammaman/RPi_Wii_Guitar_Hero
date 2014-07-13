#!/usr/bin/python
#
# Raspberry Pi Wii Guitar Hero example
# -- Talk to the Guitar Hero instruments
# Developed by Andrew Hammacott
#
# Developed from Tod E. Kurt Wii nunchuck library for Arduino
# Supplemented from wiibrew.org:
#    http://www.wiibrew.org/wiki/Wiimote/Extension_Controllers
#
# HOW TO GET STARTED
# 1. Activate I2C on the Raspberry Pi
#    I followed the Adafruit instructions here:
#    https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
#
#    but there are also instructions here:
#    http://www.raspberry-projects.com/pi/pi-operating-systems/raspbian/io-pins-raspbian/i2c-pins
#
#    I2C works using 4 connections:
#      Positive voltage (3v3 which means 3.3 volts - in electronics, decimal points are avoided)
#      Data channel #1 - SDA
#      Data channel #2 - SCL
#      Ground (GND or 0v)
#
#    This is not the place for a wiring diagram!  So you will need to google to find out how to connect 4 leads to the headers 
#
# 2. Connect the Nunchuk end (i.e. the end that goes into a Wiimote) to the Pi
#    I am using an adapter (search for "wii nunchuk arduino adapter" on google)
#    which is a small flat PCB which has one end to go into the nunchuk, and then 4 pins to make the I2C connection 
#
#    An alternative is to simply wedge leads into the Nunchuk connector.  wiibrew.org (see link above) has a wiring diagram for where
#    to attach the 4 leads onto the Nunchuk connector.
#
#
# All Nunchuk type devices are accessible via I2C protocol
# The device has an I2C "location" of 0x52
#
# This can be checked by running in the LXTerminal window (or command prompt if not using X):
#    sudo i2cdetect -y 1
# NOTE: if you have an early Raspberry Pi (like I do), the I2C was setup differently to use 0
# i.e. the command becomes:   sudo i2cdetect -y 0
#
# If connected, you will see a grid with 52 mentioned in the middle
#

# To initialise each device:
# you must first write 0x55 to 0x(4)a400f0 (for the Pi, this is just 0xf0),
# then 0 to 0x(4)a400fb (0xfb)
#

#
#/*
# 
# Wii Guitar Hero Drums
# 
# Send a byte to address 0xfa and the 6 bytes returned should be (in HEX):
# 01 00 A4 20 01 03
# 
# Data format from http://wiibrew.org/wiki/Wiimote/Extension_Controllers/Guitar_Hero_World_Tour_%28Wii%29_Drums
# 
#         Bit 7 |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
# Byte 0:   0       0    <---------------- SX ------------------------->
# Byte 1:   0       0    <---------------- SY ------------------------->
# Byte 2:  HHP    None   <------------ Which ------------------->  ????
# Byte 3: <--- Softness -------> <------- 0110 ----------------->  ????
# Byte 4: ????      1        1      B-      1       B+      1      ????
# Byte 5: Oran     Red     Yell    Gree    Blue    Bass     1       1     
# 
# Red, Blue, and Gree are the drum pads by colour (Red, Blue, and Green).
# Oran and Yell are the cymbals.
# Bass is the pedal.
# B- and B+ are the black - and + buttons behind the Wii Remote. They will be 0 when hit, 1 when not.
#
# SX and SY are the black analog stick behind the Wii Remote. 0x20 means centered.
#
# None will be 0 if there is velocity data, and 1 if there is none.
# If there is none, bytes 2 and 3 will be FF FF and contain no data, and all the ??s will be 1.
#
# If there is velocity data, then "Which" tells you which pad it is for:
#    Pedal  =  11011 = 27 dec, 0x1B
#    Red    =  11001 = 25 dec, 0x19
#    Yellow =  10001 = 17 dec, 0x11
#    Blue   =  01111 = 15 dec, 0x0F
#    Orange =  01110 = 14 dec, 0x0E
#    Green  =  10010 = 18 dec, 0x12
#
# "Softness" is how hard or soft you hit the pad. It ranges from 0 = Very hard to 6 = very soft, with 7 = not hit at all
# "HHP" is 0 if the velocity data is for the hi-hat pedal (unmarked 3.5mm jack above bass pedal jack), and 1 otherwise. When hi-hat pedal data is sent, "Which" is set as it is for the bass drum pedal (ie 11011). The velocity varies according to how far the pedal is pressed. The pedal to connect to the jack is not the same as the bass drum pedal; it must be a some sort of variable resistor (varying between 20k Ohms when down and 40 Ohms when up seems to give a good spread of velocity values from 0 to 7). The messages are not always sent and are delayed by around 35ms (probably due to the home-made pedal I'm using working wrong).
# "0110" is 0110 if there is velocity information, or 1111 if there is not. Its meaning is unknown.
# The data in the "??" bits is also unknown, although they are always 1 if there is no velocity data.
#
# Additional notes by Andrew Hammacott:
# The buttons and analog stick data appear to be common to all instruments.
#
#I've found that the single bits remain triggered for some time after hit, so am using the "Which" information in byte 2
#together with the "Softness" information in byte 3 
#

import smbus
RPI_VERSION = 0  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
bus = smbus.SMBus(RPI_VERSION)

# NEED TO ADD CODE TO MAKE THIS DYNAMIC AND TEST FOR WHICH VERSION

# Set up device

DEVICE_ADDRESS = 0x52      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG1 = 0xF0
DEVICE_REG2 = 0xFB
DEVICE_REGTYPE = 0xFA

def Device_Setup():
	# Set up the device by writing 0x55 to Register 1 and 0x00 to Register 2
	#try
	bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG1, 0x55)
	bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG2, 0x00)
# End of Device_Setup
	
def Get_Device_Connected():
	# Determine the device connected - by sending a byte to Register REGTYPE
	#try
	# Suspect not required : bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REGTYPE, 0x00)
	# Now get the next 6 bytes of data
	for counter in range(1,7):
		device_data[counter] = bus.read_block_data(DEVICE_ADDRESS, DEVICE_REGTYPE) 
	#Create a string version of these 6 bytes
	DEVICE_TYPE = "".join("%02x" % b for b in device_data)
	print "Device type = ", DEVICE_TYPE
# End of Get_Device_Connected

Device_Setup()
while True:
	Get_Device_Connected()
