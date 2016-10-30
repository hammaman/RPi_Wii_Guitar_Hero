#!/usr/bin/python
#
# Raspberry Pi Wii Guitar Hero example
# -- Talk to the Guitar Hero instruments
# Developed by Andrew Hammacott

import time
import WiiGHMainLibrary As GHMain
import WiiGHGuitarLibrary As GHguitar

loop_flag = True
last_time = time.time() # get current time

#Loop to find the instrument connected. If not found after 5 seconds, program will stop
while (loop_flag == True):
    time.sleep(1) #Wait 1 second
    GHMain.Device_Setup()
    instrument = GHMain.Get_Device_Connected()
    if instrument <> 'Unknown':
        loop_flag = False
    if time.time() > last_time + 5000:
        loop_flag = False
# Loop round until an instrument is found
    
if (instrument == 'Unknown'):
    print "No instrument found - check connections"
    #stop   

# Define variables
last_state = [0, 0, 0, 0, 0, 0]
button_pressed = 0
last_button_pressed = 0
playing_notes = [0, 0, 0, 0, 0]
notes_to_play = [0, 0, 0, 0, 0]
note_playing = False
last_time = time.time() # get current time
loop_flag = True

while (loop_flag == True):
    currentstate = MyReadData(DEVICE_ADDRESS, DEVICE_REGTYPE, False)
    if instrument == 'Guitar':
         instr_state = get_guitar_state(currentstate)
         
         #Firstly need to check if playing a note and released the button
         if ((instr_state[0] <> last_state[0]) and (last_button_pressed == last_state[0])):
             #stop playing the note and set last_button_pressed to zero
             if (Debugmode == True):
                 print "Stopping playing note"
             last_button_pressed = 0
             last_state[0] = 0
             
         #Next need to check if guitar is being strummed - only reacting on up or down (not central)
         # also need to check that guitar is being strummed together with a button press
         if (instr_state[1] <> 0) and (instr_state[0] <> 0):
             if (Debugmode == True):
                 print "Strum and button press - play note"
             last_button_pressed = instr_state[0]
             last_state[0] = instr_state[0]

         
