
import time 
import board 
import digitalio
import analogio
import usb_midi
import adafruit_midi

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.pitch_bend import PitchBend

octave_active = False

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

num_outputs = 8
num_inputs = 9

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT 

inputs = [digitalio.DigitalInOut(board.GP0),
          digitalio.DigitalInOut(board.GP1),
          digitalio.DigitalInOut(board.GP2),
          digitalio.DigitalInOut(board.GP3),
          digitalio.DigitalInOut(board.GP4),
          digitalio.DigitalInOut(board.GP5),
          digitalio.DigitalInOut(board.GP6),
          digitalio.DigitalInOut(board.GP7),
          digitalio.DigitalInOut(board.GP8),
          digitalio.DigitalInOut(board.GP9)]

pots = [analogio.AnalogIn(board.A0), analogio.AnalogIn(board.A1)]
ribbon = analogio.AnalogIn(board.A2)

for pin in inputs:
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP


outputs = [digitalio.DigitalInOut(board.GP10),
           digitalio.DigitalInOut(board.GP11),
           digitalio.DigitalInOut(board.GP12),
           digitalio.DigitalInOut(board.GP13),
           digitalio.DigitalInOut(board.GP14),
           digitalio.DigitalInOut(board.GP15),
           digitalio.DigitalInOut(board.GP16),
           digitalio.DigitalInOut(board.GP17)]

curr_button_states = [False] * (num_outputs * num_inputs + 1)
prev_button_states = [False] * (num_outputs * num_inputs + 1)

for pin in outputs:
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = True

while True:
    for current_output in range(num_outputs):
        outputs[current_output].value = False
        for current_input in range(num_inputs):
            curr_button = (current_output * num_inputs) + current_input
            curr_button_states[curr_button] = not inputs[current_input].value
            if curr_button_states[curr_button] != prev_button_states[curr_button]:
                prev_button_states[curr_button] = curr_button_states[curr_button]
                note_num = 24 + (octave_active * 12) + (current_output * num_inputs) + current_input
                if curr_button_states[curr_button]:
                    midi.send(NoteOn(note_num, 127))
                else:
                    midi.send(NoteOff(note_num, 127))
            
                #result += f"({current_output}, {current_input}) "
        outputs[current_output].value = True
    curr_button_states[-1] = not inputs[-1].value 
    if curr_button_states[-1] != prev_button_states[-1]:
        prev_button_states[-1] = curr_button_states[-1]
        if curr_button_states[-1]:
            midi.send(NoteOn(96 + (octave_active * 12), 127))
        else:
            midi.send(NoteOff(96 + (octave_active * 12), 127))
    
    pot_val =  15175 - ((pots[0].value + pots[1].value)//8)
    pot_val = ribbon.value // 3
    midi.send(PitchBend(pot_val))
    #print(result)
    #time.sleep(0.1)
# import board
# import digitalio
# import pwmio
# import time
# import usb_midi
# import adafruit_midi
# 
# from adafruit_midi.note_on import NoteOn
# from adafruit_midi.note_off import NoteOff
# 
# midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
# 
# print("MacroPad MIDI Board")
# 
# 
# # Set Initial Duty Cycles to 0 for each LED
# duty_cycles = [0 for _ in led_pins]
# 
# # Key and trigger states
# pressed_keys = [False for _ in button_pins]
# triggered_keys = [False for _ in button_pins]
# while True:
#     midi.send(NoteOn("C4", 127))
#     time.sleep(0.5)
#     midi.send(NoteOff("C4", 127))
#     time.sleep(0.5)
    
