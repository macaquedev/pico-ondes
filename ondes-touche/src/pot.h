const int numPots = 8;                                  // Number of potentiometers
const int potPins[] = {A0, A1, A2, A3, A6, A7, A8, A9}; // Modify these pin numbers as needed
int prevReadings[numPots] = {0, 0, 0, 0, 0, 0, 0, 0};
const byte midiChannels[] = {2, 2, 2, 2, 2, 2, 2, 2};

const int touchePin = A10;
int prevToucheReading = 0;
const byte toucheChannel = 2;
const int toucheCorrection = 5;

int convertToMidiValue(int value)
{
    return map(value, 0, 1023, 0, 127);
}

int convertToucheToMidiValue(int value)
{
    long long x = map(value, 1023, 60, 0, 1023);
    x = (x * x) / 1023;
    int k = x / 8;
    return min(max(k - toucheCorrection, 0), 127);
}

void initialisePots()
{
    for (int i = 0; i < numPots; i++)
    {
        int potValue = analogRead(potPins[i]);
        prevReadings[i] = potValue;
    }
    prevToucheReading = analogRead(touchePin);
}

void updatePot(int x)
{
    int potValue = analogRead(potPins[x]);
    int midiValue = convertToMidiValue(potValue);
    int prevValue = prevReadings[x];
    if (abs(midiValue - prevValue) > 1)
    {
        sendControlChange(midiChannels[x], x+5, midiValue);
        prevReadings[x] = midiValue;
    }
}

void updateTouche()
{
    int toucheValue = analogRead(touchePin);
    int midiValue = convertToucheToMidiValue(toucheValue);
    int prevValue = prevToucheReading;
    if (abs(midiValue - prevValue) > 1)
    {
        sendControlChange(toucheChannel, 4, midiValue);
        prevToucheReading = midiValue;
    }
}