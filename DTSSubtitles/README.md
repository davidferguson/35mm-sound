# DTS Subtitles

Part of the DTS system was the CSS - Cinema Subtitling System. This allowed for
subtitles to be displayed in sync with the film, as well as descriptive voice
narration for the visually impaired.

Given a DTS SBT subtitle file, this program can read the metadata, as well as
show, save and export the subtitle images stored within it. A [description of
the DTS SBT file format is also given](sbt-format.md). Currently only reading
from the SBT file is supported, not writing/creating new SBT files.

## Usage
Run `pip install -r requirements.txt` to install the required libraries. Then
run `python run.py --help` to see a list of commands and options.

Commands:
- `info`: Prints information about the provided SBT file
- `show`: Displays the subtitle image at a given reel and frame number
- `save`: Saves the subtitle image at a given reel and frame number
- `export`: Exports all subtitle images between a start and end point
