/*
 * # DTS Timecode Generator
 * 
 * Given a DTS serial number and reel number, generates a DTS timecode signal on
 * a given pin, starting at a given DTS frame number. It does not work with the
 * more modern "encrypted" DTS timecode format (that uses AUE rather than AUD
 * files).
 * 
 * Thanks to Blaine Young, Sean Weitzel and Markus Lemm for the information on
 * the DTS timecode format.
 * 
 * ## Usage
 * Set the parameters as desired, connect the pin to the DTS timecode pin, and
 * run.
 * 
 * Parameters:
 * - `DELAY_MICROSECONDS`: Normally set to 694, this defines the delay in
 * microseconds of the short pulse. 694 is 1,000,000 microseconds (1 second),
 * divided by 30 (DTS fps), divided by 24 (bits per frame), and divided by 2
 * (two short pulses per bit). Adjust this if you want to alter the playback
 * speed.
 * - `DTS_PIN`: The pin number to output the DTS timecode on
 * - `SERIAL_NUMBER`: The serial number of the DTS feature to play
 * - `REEL_NUMBER`: The reel number to play
 * - `START_FRAME_NUMBER`: The DTS frame to start on
 * 
 * 
 * ## DTS Timecode
 * DTS Timecode is Biphase-M (Biphase Mark), meaning that the signal level
 * changes:
 *   1. at the start of every bit
 *   2. in the middle of a bit if the bit is 1
 *   
 * This basically means that a 0 is encoded as a long pulse, and a 1 is encoded
 * as two short pulses of different levels.
 * 
 * DTS runs at 30 frames a second. Between each frame there is a delimiter,
 * which is a long-long pulse, followed by another long-long pulse. A long-long
 * pulse is x2 a long pulse, and x4 a short pulse. Each DTS frame is 20 bits,
 * and including the delimiters, each is 24 bits.
 * 
 * There are two types of DTS frame.
 * 
 * **Serial number* * frames start with 0000 and contain the feature serial
 * number in binary.
 * 
 * **Timecode frames* * do not start with 0000, and contain the reel and current
 * frame number. The frame number is the DTS frame number, so runs at 30fps, and
 * increments for each new frame.
 * 
 * On features, there is a serial number frame ever 16th frame, and the rest are
 * timecode frames.
 *
 */

#define DELAY_MICROSECONDS 694
#define DTS_PIN 8
#define SERIAL_NUMBER 9261
#define REEL_NUMBER 2
#define START_FRAME_NUMBER 0

void invertSignal() {
  digitalWrite(DTS_PIN, !digitalRead(DTS_PIN));
}

// these need to be reset at the start of every new frame!
unsigned long frameTime = 0;
int dtsCount = 0;
void dtsDelay(int dtsLength) {
  // dtsLength is the length to delay for, ie. is this a short,
  // long, or long-long delay.
  // short = x1
  // long = x2
  // long long = x4
  dtsCount += dtsLength;
  unsigned long addAmount = (unsigned long) dtsCount * DELAY_MICROSECONDS;
  unsigned long waitUntilTime = frameTime + addAmount;
  unsigned long waitTime = waitUntilTime - micros();
  while (waitUntilTime > micros()) {}
}

void writeDelimiter() {
  invertSignal();
  dtsDelay(4);
  invertSignal();
  dtsDelay(4);
}

void writeZero() {
  invertSignal();
  dtsDelay(2);
}

void writeOne() {
  invertSignal();
  dtsDelay(1);
  invertSignal();
  dtsDelay(1);
}

int testBit(uint32_t frame, int bitNumber) {
  // bit number ranges from 0 to 19
  bitNumber++;
  return (frame >> (bitNumber - 1)) & 1;
}

void writeFrame(uint32_t frame) {
  for (int i = 0; i < 20; i++) {
    if (testBit(frame, i)) {
      writeOne();
    } else {
      writeZero();
    }
  }
  writeDelimiter();
}

uint32_t generateSerialFrame(uint16_t serialNumber) {
  return 0 | serialNumber;
}

uint32_t generateTimecodeFrame(uint8_t reelNumber, uint16_t frameNumber) {
  uint32_t reelNumberLarge = reelNumber;
  return frameNumber | (reelNumberLarge << 16);
}


/* --------------------- */

uint32_t serialFrame = 0;
int frameNumber = START_FRAME_NUMBER;

void setup() {
  Serial.begin(115200);
  pinMode(DTS_PIN, OUTPUT);
  delay(1000);
  serialFrame = generateSerialFrame(SERIAL_NUMBER);
  frameTime = micros();
}

void loop() {
  uint32_t frame = 0;
  frameTime += (unsigned long) 48 * DELAY_MICROSECONDS;
  //frameTime = micros();
  dtsCount = 0;
  
  if (frameNumber % 16 == 0) {
    // send a serial number frame
    frame = serialFrame;
  } else {
    // send a timecode frame
    frame = generateTimecodeFrame(REEL_NUMBER, frameNumber);
  }

  writeFrame(frame);

  frameNumber++;
}
