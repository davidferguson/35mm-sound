# DTS SBT File Format

## Context
The DTS CSS (Cinema Subtitling System) uses DTS Access disks rather than the standard DTS audio disks. A XD10 with CSS license, or the specially designed DTS CSS would load these disks in the same way as the XD10 loaded audio disks. These disks contain two types of files, the first being a single `.sbt` subtitle file for the film, and the second being a set of `.nar` narration files, one for each reel. This will focus on the subtitle files.

The DTS subtitling system involved either a projector to project the subtitles on top of (or sometimes slightly underneath) the 35mm projection, so that viewers could see the subtitles, or alternatively displaying the subtitles on a LED display on the rear wall of the auditorium, and viewers who wanted to see the subtitle would use a small mirror to be able to see them.

## File Format
### Overview
The subtitle file is broken up into three sections. The first of these is a header which contains information such as the serial number, studio code, language, etc. The second of these is an index of timecodes and offsets in the file, where the offset points to a subtitle image that should be displayed at that timecode. The last section is the images themselves. It should be noted that the subtitle files do not store the subtitle as text, but rather as an image of text, which was probably so that different character sets could be handled easily.

### Header
The file header is 202 bytes long, and contains the following information:

| Field           | Start Byte Offset | Length | Format       |
|-----------------|-------------------|--------|--------------|
| Header          | 0                 | 3      |              |
| DTS             | 6                 | 3      | ASCII        |
| Film name       | 9                 | 18     | ASCII        |
| Studio code     | 69                | 3      | ASCII        |
| DTS serial code | 79                | 2      | Integer, LSB |
| Language        | 85                | 3      | ASCII        |
| Zoom?           | 96                | 1      | ASCII        |
| Unknown1        | 91                | 1      |              |
| Unknown2        | 113               | 3      |              |

An example header for How to Train Your Dragon (code 9261) is given below:
```
CA 00 01 00 00 00 44 54 53 48 6F 77 54 6F 54 72 61 69 6E 59 6F 75 72 44 72 61 67 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 4A 45 52 00 00 00 00 00 00 00 2D 24 00 00 01 00 45 4E 47 00 00 00 01 00 00 00 00 64 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 AD 72 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

### Index
The index section of the file starts at byte 202. This contains a number of index entries, each 16 bytes long, where each index entry contains the following information:

| Field        | Description                                             | Start Byte Offset | Length | Format       |
|--------------|---------------------------------------------------------|-------------------|--------|--------------|
| Header       | Always 0x10000400                                       | 0                 | 4      |              |
| Image offset | The offset in bytes of the subtitle image in the file   | 4                 | 4      | Integer, LSB |
| Start Frame  | The DTS frame number (30 fps) when to show the subtitle | 8                 | 3      | Integer, LSB |
| Start Reel   | The reel number the Start Frame corresponds to          | 11                | 1      | Integer, LSB |
| End Frame    | The DTS frame number (30 fps) when to hide the subtitle | 12                | 3      | Integer, LSB |
| End Reel     | The reel number the End Frame corresponds to            | 15                | 1      | Integer, LSB |

Some example index entries from How to Train Your Dragon are given below:
```
10 00 04 00 7A 47 00 00 0B 04 00 01 4A 04 00 01
10 00 04 00 F8 BF 00 00 6E 05 00 01 D0 05 00 01
10 00 04 00 90 3E 04 00 31 0F 00 01 4E 0F 00 01
```

### Subtitle Images
The images section contains the subtitle images to display. These are stored as black and white, and a bit depth of 1, with variable height and width. Each image is preceded by a 38 byte header which contains a copy of the index information, as well as other information. The information stored in the header is given below, where a `*` denotes that the field is duplicated from the index entry.

| Field         | Description                                                      | Start Byte Offset | Length | Format       |
|---------------|------------------------------------------------------------------|-------------------|--------|--------------|
| Header        | Always 0x26000200                                                | 0                 | 4      |              |
| Image Name    | A name of the image. I don't think this is needed.               | 4                 | 12     | ASCII        |
| Image Offset  | The offset in bytes of the subtitle image in the file            | 16                | 4      | Integer, LSB |
| \*Start Frame | The DTS frame number (30 fps) when to show the subtitle          | 20                | 3      | Integer, LSB |
| \*Start Reel  | The reel number the Start Frame corresponds to                   | 23                | 1      | Integer, LSB |
| \*End Frame   | The DTS frame number (30 fps) when to hide the subtitle          | 24                | 3      | Integer, LSB |
| \*End Reel    | The reel number the End Frame corresponds to                     | 27                | 1      | Integer, LSB |
| Horizontal    | Horizontal offset from left side of screen to left edge of image | 28                | 2      | Integer, LSB |
| Vertical      | Vertical offset from top of screen to top edge of image          | 30                | 2      | Integer, LSB |
| Height        | Height of the image in pixels                                    | 32                | 2      | Integer, LSB |
| Width         | Width of the image in pixels                                     | 34                | 2      | Integer, LSB |
| Count         | Number of bytes of the image                                     | 36                | 2      | Integer, LSB |

Note there are some peculiarities with some of these fields:
* The `Image Offset` refers to the start of the image data, not the start of this header. It is the size of this header (38) plus 4 - see the note below regarding this.
* `Image Name` gives a name of the format `CL610001.bmp`, with incrementing numbers where 610001 is the first. I can't think of any reason this is needed, and it is probably something left over from the encoding process. It is curious why they dedicated 12 bytes of the header to it though, when I can't think of a use for it.
* The `Vertical` offset *must* be between 0x0100 and 0x0300, regardless of the image height. If not, then it over/underflows and returns to being in the centre of the display.
* The `Vertical` offset isn't actually from the top of the screen, but a few inches down. I don't know why this is.
* The `Width` isn't actually the width of the image. The real width should be calculated by dividing `Count` by `Height`. The `Width` is usually less than this calculated width, and appears to be so that the right side of the image can be cropped. I don't know why this would ever be useful.
* The `Count` is always a multiple of 256, ie byte 36 is always 0x00.

After this header, there is 4 bytes of information, and then the image data starts. Initially I thought these 4 bytes may be part of the header, but because the `Image Offset` field points to them, I'm not so sure. I also had a look at a decompiled version of the DTS program that runs on the XD10, and it seems to read 38 bytes for a header, which aligns with these 4 bytes not being part of the header. Sadly the decompilation is incomplete and I cannot see what the 4 bytes is used for. The format of these bytes seems to be 0x04XX0600, where XX is byte 37 from the header.

Some example headers are given below. The four bytes that follow after the header have been left on.
```
26 00 02 00 43 4C 36 31 30 30 33 35 2E 62 6D 70 34 84 04 00 94 10 00 01 31 11 00 01 3D 00 68 02 80 00 86 03 00 3A 04 3A 06 00
26 00 02 00 43 4C 36 31 30 30 33 36 2E 62 6D 70 5E BE 04 00 32 11 00 01 8B 11 00 01 EE 00 68 02 80 00 24 02 00 24 04 24 06 00
26 00 02 00 43 4C 36 31 30 30 33 37 2E 62 6D 70 88 E2 04 00 8C 11 00 01 D0 11 00 01 29 00 A8 02 40 00 B0 03 00 1E 04 1E 06 00
26 00 02 00 43 4C 36 31 30 30 33 39 2E 62 6D 70 DC 36 05 00 51 12 00 01 9C 12 00 01 D7 00 68 02 80 00 54 02 00 26 04 26 06 00
26 00 02 00 43 4C 36 31 30 30 30 34 2E 62 6D 70 1E C0 00 00 6E 05 00 01 D0 05 00 01 9A 00 A8 02 40 00 CE 02 00 17 04 17 06 00
```
