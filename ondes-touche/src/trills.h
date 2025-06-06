#include <Arduino.h>

const int numTrills = 6;
const int trillPins[] = {0, 1, 2, 3, 5, 7}; // Modify these pin numbers as needed
const int octavePin = 15;
const int modeSelectPin = 14;
int trillChannel = 3;
int trillCC = 3;
int modeCC = 25;

int currOctave = 0;
int previousOctaveButtonState = 0;
int previousOctavePressedTime = 0;

bool currMode = 0; // 0: Keyboard 1: Ribbon
bool previousModeButtonState = 0;
bool previousModePressedTime = 0;

byte prevReading = 0;
bool prevMode = 0;

void initialiseTrills()
{
    pinMode(octavePin, INPUT_PULLUP);
    pinMode(modeSelectPin, INPUT_PULLUP);
    previousModeButtonState = !digitalRead(modeSelectPin);
    for (int i = 0; i < numTrills; i++)
    {
        pinMode(trillPins[i], INPUT_PULLUP);
        prevReading |= (!digitalRead(trillPins[i])) << i;
    }
}

void updateOctave()
{
    int currOctaveReading = !digitalRead(octavePin);
    int currModeReading = !digitalRead(modeSelectPin);
    if (previousOctaveButtonState)
    {
        if (currOctaveReading == 0)
        {
            previousOctaveButtonState = 0;
        }
        else
        {
            previousOctavePressedTime = millis();
        }
    }
    else
    {
        if (currOctaveReading != 0 and millis() - previousOctavePressedTime >= 100)
        {
            previousOctaveButtonState = 1;
            currOctave = (currOctave + 1) % 2;
        }
    }

    if (previousModeButtonState)
    {
        if (currModeReading == 0)
        {
            previousModeButtonState = 0;
        }
        else
        {
            previousModePressedTime = millis();
        }
    }
    else
    {
        if (currModeReading != 0 and millis() - previousModePressedTime >= 100)
        {
            previousModeButtonState = 1;
            currMode = !currMode;
        }
    }
}

void updateTrills()
{
    updateOctave();
    byte reading = 0;
    for (int i = 0; i < numTrills; i++)
    {
        reading |= (!digitalRead(trillPins[i])) << i;
    }

    reading |= currOctave << 6;

    if (reading != prevReading)
    {
        prevReading = reading;
        sendControlChange(trillChannel, trillCC, reading);
    }

    if (currMode != prevMode)
    {
        prevMode = currMode;
        sendControlChange(trillChannel, modeCC, currMode);
    }
}