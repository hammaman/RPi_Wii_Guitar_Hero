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



import smbus

# The interface is numbered differently depending on the Raspberry Pi model
# We can check this from getting the revision number available in the GPIO library
import RPi.GPIO as GPIO
version = GPIO.RPI_REVISION
if version == 1: 
    RPI_VERSION = 0
else:
    RPI_VERSION = 1

# 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
bus = smbus.SMBus(RPI_VERSION)

import time
SLEEP_TIME = 0.02

# Set up device

DEVICE_ADDRESS = 0x52      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG1 = 0xF0
DEVICE_REG2 = 0xFB
DEVICE_REGTYPE = 0xFA
full_data = [0,0,0,0,0,0,0]
device_data = [0, 0, 0, 0, 0, 0]
device_text = '000000000000'


# To initialise each device:
# you must first write 0x55 to 0x(4)a400f0 (for the Pi, this is just 0xf0),
# then 0 to 0x(4)a400fb (0xfb)
#
def Device_Setup():
    # Set up the device by writing 0x55 to Register 1 and 0x00 to Register 2
    #try
    bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG1, 0x55)
    bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG2, 0x00)

# End of Device_Setup
    
def Get_Device_Connected():
    # Determine the device connected - by sending a byte to Register REGTYPE
    # and look at the 6 bytes of data returned
    
    bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REGTYPE, 0x00)
    time.sleep(SLEEP_TIME)
    result = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REGTYPE)
    full_data = bus.read_i2c_block_data(DEVICE_ADDRESS, DEVICE_REGTYPE) 

    #Extract first 6 bytes and store as a string in hex format
    device_text = ''
    for i in range(0,6):
        device_text = device_text + ("%02x" % full_data[i])
    #next i

    if device_text == '0000a4200103':
        device_connected = 'Guitar'
    elif device_text == '0100a4200103':
        device_connected = 'Drums'
    else:
        device_connected = 'Unknown'
    #end if

    return device_connected

#End of Get_Device_Connected

def MyReadData(MY_DEVICE_ADDRESS, MY_DEVICE_REG, Debugmode):
    # this is my function to read only 6 bytes of data returned over I2C
    # instead of reading 256 bytes!
    # and is equivalent to read_i2c_block_data
    # Returns a list of 6 bytes

    # First send a byte of data to request the information

    bus.write_byte_data(MY_DEVICE_ADDRESS, MY_DEVICE_REG, 0x00)
    time.sleep(SLEEP_TIME)
    full_data = bus.read_i2c_block_data(MY_DEVICE_ADDRESS, MY_DEVICE_REG) 

    #Extract first 6 bytes
    device_text = ''
    for i in range(0,6):
        device_data[i] = full_data[i]
        device_text = device_text + ("%02x" % full_data[i])
    #next i

    # Print the output to screen if Debugmode set to True
    if (Debugmode == True):
        print "Device type = ", device_text
    #endif
        
    return device_data

# End of MyReadData

# ------------------------------------------------------------------------------
#
# General functions for all instruments
#

# Returns x position of joystick 0x20 is centered
def GHjoyx(data_received):
    return (data_received[0] & 0x3F)

# Returns y position of joystick 0x20 is centered
def GHjoyy(data_received):
    return (data_received[1] & 0x3F)

# Returns 1 if button plus is pressed
def GHbutplus(data_received):
    return (1 - ((data_received[4] >> 4) & 0x01))

# Returns 1 if button minus is pressed
def GHbutminus(data_received):
    return (1 - ((data_received[4] >> 2) & 0x01))

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


# Guitar Hero Drum functions

GH_DRUMPED = 0x1B
GH_DRUMRED = 0x19
GH_DRUMYEL = 0x11 
GH_DRUMBLU = 0x0F
GH_DRUMORA = 0x0E
GH_DRUMGRE = 0x12
 
def GHdrumhit(received_data):
    return ((received_data[2] >> 1) & 0x1F)


def GHdrumhitstrength(received_data):
    return ((received_data[3] >> 5) & 0x07)

#
# 
# Wii Guitar Hero Guitar
# 
# Send a byte of address 0xfa and the 6 bytes returned should be (in HEX):
# 00 00 A4 20 01 03
# 
# Data format from http://wiibrew.org/wiki/Wiimote/Extension_Controllers/Guitar_Hero_%28Wii%29_Guitars
# 
#         Bit 7 |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
# Byte 0:  GH3     GH3   <---------------- SX ------------------------->
# Byte 1:  GH3     GH3   <---------------- SY ------------------------->
# Byte 2:   0       0       0    <------------  Touchbar -------------->
# Byte 3:   0       0       0    <------------  Whammy bar ------------>
# Byte 4:   1    StrumDn    1       B-      1       B+      1       1
# Byte 5: Oran     Red     Blue    Gree    Yell     1       1    StrumUp     
# 
# StrumUp and StrumDn are up and down on the strum bar
# Whammy bar is the analog whammy bar
#
# Touchbar is the analog touchbar on the neck of GH World Tour guitars:
#   Not touching it  -  0F
#   1st (top) fret   -  04
#   1st AND 2nd      -  07
#   2nd              -  0A
#   2nd AND 3rd      -  0C/0D (keeps changing)
#   3rd              -  12/13
#   3rd AND 4th      -  14/15
#   4th              -  17/18
#   4th and 5th      -  1A
#   5th (bottom)     -  1F
# You can hold two (touchbar) frets at once, as long as those two (touchbar) frets are adjacent,
# otherwise it will take the value of the lowest fret held (Eg, if you hold the highest and lowest fret, it reads 1F)
# Note that high/low means physically on the guitar neck (in musical terms I think it's the other way around, so I thought I'd better specify) 
# 
# B- and B+ are the black - and + buttons behind the Wii Remote. They will be 0 when hit, 1 when not.
# SX and SY are the black analog stick behind the Wii Remote. 0x20 means centered.
# 
# My notes:
# The whammy bar is centred on 0x00 and rises as pressed down?

GH_GUITORA = 0x10
GH_GUITRED = 0x08
GH_GUITBLU = 0x04
GH_GUITGRE = 0x02
GH_GUITYEL = 0x01

GH_GUITFRT1 = 0x10
GH_GUITFRT2 = 0x08
GH_GUITFRT3 = 0x04
GH_GUITFRT4 = 0x02
GH_GUITFRT5 = 0x01
 
def GHguitar_button(data_received):
    return ((data_received[5] >> 3) & 0x1F)

def GHguitar_strumup(data_received):
    return (data_received[5] & 0x01)

def GHguitar_strumdn(data_received):
    return ((data_received[4] >> 6) & 0x01)

def GHguitar_whammy(data_received):
# Whammy bar seems to fluctuate around B01111 and B10000 at rest
# and increases to B11001 when fully pressed
# so instead of reading 5 bits, I am just reading the last 4
# and setting B1111 to zero
    if ((data_received[3] & 0x0F) == 0x0F):
        return 0
    else:
        return (data_received[3] & 0x0F)


def GHguitartouchbar(data_received):
    GHguitartb = (data_received[2] & 0x1F)
    if (GHguitartb == 0x04):
        return GH_GUITFRT1
    elif (GHguitartb == 0x07):
        return (GH_GUITFRT1 + GH_GUITFRT2)
    elif (GHguitartb == 0x0A):
        return GH_GUITFRT2
    elif (GHguitartb == 0x0C):
        return (GH_GUITFRT2 + GH_GUITFRT3)
    elif (GHguitartb == 0x0D):
        return (GH_GUITFRT2 + GH_GUITFRT3)
    elif (GHguitartb == 0x0F):
        return 0
    elif (GHguitartb == 0x12):
        return GH_GUITFRT3
    elif (GHguitartb == 0x13):
        return GH_GUITFRT3
    elif (GHguitartb == 0x14):
        return (GH_GUITFRT3 + GH_GUITFRT4)
    elif (GHguitartb == 0x15):
        return (GH_GUITFRT3 + GH_GUITFRT4)
    if (GHguitartb == 0x17):
        return GH_GUITFRT4
    elif (GHguitartb == 0x18):
        return GH_GUITFRT4
    elif (GHguitartb == 0x1A):
        return (GH_GUITFRT4 + GH_GUITFRT5)
    elif (GHguitartb == 0x1F):
        return GH_GUITFRT5
    else:
        return 0
#End of GHguitartouchbar

# END OF GH FUNCTIONS

