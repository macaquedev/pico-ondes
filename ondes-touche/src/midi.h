#include <Arduino.h>
#include <MIDIUSB.h>

// Define the potentiometer pins in an array

/**
 * Helper function to send a Control Change (CC) message.
 *
 * @param channel   The MIDI channel [0-15]
 * @param control   The CC number [0-127]
 * @param value     The CC value [0-127]
 */
void sendControlChange(byte channel, byte control, byte value) {
  // Create a MIDI event package
  midiEventPacket_t event = {
    0x0B,                     // MIDI event type: 0x0B -> Control Change
    byte(0xB0 | channel),     // 0xB0 = CC message for channel 0, add channel offset
    control,                  // CC number
    value                     // CC value
  };

  // Send it
  MidiUSB.sendMIDI(event);
  // Make sure it actually gets sent out right away
  MidiUSB.flush();
}