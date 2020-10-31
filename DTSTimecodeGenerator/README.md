# DTS Timecode Generator

Given a DTS serial number and reel number, generates a DTS timecode signal on a
given pin, starting at a given DTS frame number. It does not work with the more
modern "encrypted" DTS timecode format (that uses AUE rather than AUD files).

Thanks to Blaine Young, Sean Weitzel and Markus Lemm for the information on the
DTS timecode format.

## Usage
Set the parameters as desired, connect the pin to the DTS timecode pin, and run.

Parameters:
- `DELAY_MICROSECONDS`: Normally set to 694, this defines the delay in
microseconds of the short pulse. 694 is 1,000,000 microseconds (1 second),
divided by 30 (DTS fps), divided by 24 (bits per frame), and divided by 2 (two
short pulses per bit). Adjust this if you want to alter the playback speed.
- `DTS_PIN`: The pin number to output the DTS timecode on
- `SERIAL_NUMBER`: The serial number of the DTS feature to play
- `REEL_NUMBER`: The reel number to play
- `START_FRAME_NUMBER`: The DTS frame to start on


## DTS Timecode
DTS Timecode is Biphase-M (Biphase Mark), meaning that the signal level changes:
  1. at the start of every bit
  2. in the middle of a bit if the bit is 1

This basically means that a 0 is encoded as a long pulse, and a 1 is encoded as
two short pulses of different levels.

DTS runs at 30 frames a second. Between each frame there is a delimiter, which
is a long-long pulse, followed by another long-long pulse. A long-long pulse is
x2 a long pulse, and x4 a short pulse. Each DTS frame is 20 bits, and including
the delimiters, each is 24 bits.

There are two types of DTS frame.

**Serial number** frames start with 0000 and contain the feature serial number
in binary.

**Timecode frames** do not start with 0000, and contain the reel and current
frame number. The frame number is the DTS frame number, so runs at 30fps, and
increments for each new frame.

On features, there is a serial number frame ever 16th frame, and the rest are
timecode frames.
