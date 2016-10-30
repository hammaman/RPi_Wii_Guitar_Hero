#!/usr/bin/python
#
# Raspberry Pi Wii Guitar Hero example
# -- Talk to the Guitar Hero instruments
# Developed by Andrew Hammacott

# GUITAR FUNCTIONS

#Guitar behaviour
#Strum plays a note based on button pressed.  Note continues until button released, or strum again.
#Strum also plays a note even if no button pressed.  Note continues until strum again
#Notes fade gradually (exponentially?)
#Whammy bar changes pitch of note playing
#Code needs to be able to output either sound directly via Pi, or MIDI notes for connection to a MIDI device
#Plus and minus button to change key registers.  Suggest build in delay

#So think need the following states recorded:

#Main buttons (R/G/B/O/Y)
#timepressed
#buttonpressed

#Whammy bar
#timepressed
#whammystrength

#Joystick buttons
#timepressed
#buttonpressed

#Rough logic
#If strummed -> record button pressed information.  Stop playing current note and play new one.
#If button released and playing note -> stop playing current note

#If whammy bar -> warble current note

#If joystick buttons -> change key register (if time since last pressed is not too short)

#Need:
#noteplaying
#timestarted

#If touchbar -> stop playing current note and play new one.  May need to activate ths as may be subject to random signals ...

#Array for notes - 2 dimensional?
#notes[0,0] to notes[5,3]?  So 4 key registers?

#Python code:

def get_guitar_state(GHdata):
    guitar_state = [0,0,0,0,0,0,0]
    guitar_state[0] = GHguitar_button(GHdata)
    guitar_state[1] = GHguitar_strumup(GHdata) - GHguitar_strumdn(GHdata) # i.e. +1 if up, -1 if down and 0 if neither
    guitar_state[2] = GHguitar_whammy(GHdata)
    guitar_state[3] = GHguitartouchbar(GHdata)
    guitar_state[4] = GHjoyx(GHdata)
    guitar_state[5] = GHjoyy(GHdata)
    guitar_state[6] = GHbutplus(GHdata) - GHbutminus(GHdata)
    return guitar_state  

import time

loop_flag = True
last_time = time.time() # get current time

#Loop to find the instrument connected. If not found after 30 seconds, program will stop
while (loop_flag == True):
    time.sleep(1) #Wait 1 second
    Device_Setup()
    instrument = Get_Device_Connected()
    if instrument <> 'Unknown':
        loop_flag = False
    if time.time() > last_time + 30000:
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

         
