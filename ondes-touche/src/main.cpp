#include "midi.h"
#include "pot.h"
#include "trills.h"

void setup() {
  initialisePots();
  initialiseTrills();
}

void loop() {
  // Read and print the value of each potentiometer
  for (int i = 0; i < numPots; i++) {
    updatePot(i);
  }

  updateTouche();
  updateTrills();
}
