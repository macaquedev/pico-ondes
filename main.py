import time 
import board 
import digitalio
import analogio
import usb_midi
import adafruit_midi

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.control_change import ControlChange

from collections import deque

class DynamicSmoothingFilter:
    def __init__(self, stationary_alpha=0.1, fast_alpha=0.8):
        self.stationary_alpha = stationary_alpha
        self.fast_alpha = fast_alpha
        self.current_value = None
        self.previous_value = None

    def add_reading(self, new_reading):
        if self.current_value is None:
            self.current_value = new_reading
            self.previous_value = new_reading
            return self.current_value

        # Calculate rate of change
        rate_of_change = abs(new_reading - self.previous_value)

        # Dynamically adjust alpha based on movement speed
        alpha = self.fast_alpha if rate_of_change > 300 else self.stationary_alpha
        self.current_value = alpha * new_reading + (1 - alpha) * self.current_value
        self.previous_value = new_reading
        return round(self.current_value)

class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.readings = []  # Use a list to store the readings

    def add_reading(self, new_reading):
        """Add a new reading and return the smoothed average."""
        self.readings.append(new_reading)
        # Keep only the last `window_size` readings
        if len(self.readings) > self.window_size:
            self.readings.pop(0)
        
        # Return the average of the current readings
        return self._average(self.readings)

    def _average(self, data):
        """Calculate the mean of a list of numbers."""
        if not data:
            return 0  # Handle empty lists gracefully
        return round(sum(data) / len(data))


class MedianFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.readings = []  # Use a list to store the readings

    def add_reading(self, new_reading):
        # Add the new reading to the list
        self.readings.append(new_reading)
        # Keep only the last `window_size` readings
        if len(self.readings) > self.window_size:
            self.readings.pop(0)
        # Return the median of the current readings
        return self._median(self.readings)

    def _median(self, data):
        # Sort the data and calculate the median
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            # Even number of elements: average the middle two
            return (sorted_data[mid - 1] + sorted_data[mid]) // 2
        else:
            # Odd number of elements: return the middle one
            return sorted_data[mid]

class RobustMeanFilter:
    def __init__(self, window_size=5, mad_threshold=3):
        self.window_size = window_size
        self.mad_threshold = mad_threshold
        self.readings = []  # Use a list to store the readings

    def add_reading(self, new_reading):
        """Add a new reading and return the robust mean of the current readings."""
        self.readings.append(new_reading)
        # Keep only the last `window_size` readings
        if len(self.readings) > self.window_size:
            self.readings.pop(0)
        
        # Return the robust mean of the current readings
        return int(self._robust_mean(self.readings))

    def _robust_mean(self, data):
        """Calculate the robust mean, discarding outliers based on MAD."""
        medians = self._median(data)
        mad = self._mad(data, medians)

        # Filter out readings that deviate significantly from the median
        cleaned_data = []
        for value in data:
            if abs(value - medians) <= self.mad_threshold * mad:
                cleaned_data.append(value)

        # Return the mean of the cleaned data
        return self._mean(cleaned_data)

    def _median(self, data):
        """Calculate the median of a list of numbers."""
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]

    def _mad(self, data, medians):
        """Calculate the Median Absolute Deviation (MAD)."""
        absolute_deviation = [abs(x - medians) for x in data]
        return self._median(absolute_deviation)

    def _mean(self, data):
        """Calculate the mean of a list of numbers."""
        if not data:
            return 0  # Handle empty lists gracefully
        return sum(data) / len(data)

octave_active = False

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

ANALOG_READ_DELAY = 0.01

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

keyboard_vib = analogio.AnalogIn(board.A0)
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


#ribbon_filter = MovingAverageFilter(window_size = 40)
ribbon_filter = DynamicSmoothingFilter(0.05, 0.95)
while True:
    #time.sleep(ANALOG_READ_DELAY)
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
    
    keyboard_vib_val =  15175 - (keyboard_vib.value//4)
    ribbon_val = ribbon.value // 3
    filtered_ribbon = ribbon_filter.add_reading(min(16383, ribbon_val))

    midi.send(PitchBend(filtered_ribbon))
    midi.send(ControlChange(2, keyboard_vib_val // 128))

    #midi.send(PitchBend(keyboard_vib_val))
    #time.sleep(ANALOG_READ_DELAY)



