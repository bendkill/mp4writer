# MP4Writer

A simple Python wrapper around `ffmpeg` for writing MP4 files from Numpy arrays
or matplotlib figures, viewable with QuickTime Player on a recent Mac.

## Installation

`mp4writer` uses Python 3.6 or higher. It also depends on
* numpy
* matplotlib
* ffmpeg

After installing these dependencies, clone this repository and add it to your
`PYTHONPATH` with
```
export PYTHONPATH=PATH_TO_MP4WRITER:$PYTHONPATH
```
And check the output of `env` to make sure the change has been made.

You can also put the above line in your `~/.bash_profile` or other config file
to make this environment change permanent.

Of course, you can also just download the `mp4writer.py` file to wherever you
want to import it.

## Usage

Usage is modeled after the native syntax for writing to files in python. We do
not yet support `with` blocks.

```python
import numpy as np
from mp4writer import MP4Writer

# 150 512x512 frames with gaussian noise in each RGB channel:
frames = np.random.normal(0.5, scale=0.1, size=(150, 512, 512, 3))

# instantiate the writer (but do not open the ffmpeg pipe)
writer = MP4Writer("my_video.mp4", fps=30)

# write the frames
for frame in frames:
  # first call to write opens the ffmpeg pipe
  writer.write(frame)
  
# closes ffmpeg, very important
writer.close()
```
