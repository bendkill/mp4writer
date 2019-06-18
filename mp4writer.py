"""A video writer class for feeding in numpy frames or even matplotlib figures
(which are converted to numpy). Writes video in grayscale or rgba uint8 format."""

import numpy as np
import subprocess as sp
import logging
import os
import matplotlib.pyplot as plt

logger = logging.getLogger('mp4writer')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s:mp4writer:%(message)s'))
logger.addHandler(handler)

logger.debug(f"Use Python{3.6} or higher.")

class MP4Writer:
  def __init__(self, fname, shape=None, fps=30, bitrate=40000):
    """Write frames to a video.

    If shape is provided, opens the process here. Otherwise, process is opened
    on the first call to `write()`.

    :param fname: file to write the mp4 to
    :param shape: (optional) shape of the video. For rgb, include number of channels.
    :param fps: frames per second. Default is 30.
    :param bitrate: bitrate in kilobits, controlling compression. Higher bitrate 
    means less compression. Default is 40000, which is pretty detailed.

    """
    self.fname = fname
    self.fps = fps
    self.shape = shape
    self.bitrate = int(bitrate)
    if shape is not None:
      self.open(shape)
      
  def open(self, shape):
    """FIXME! briefly describe function

    :param shape: 
    :returns: 
    :rtype: 

    """
    self.shape = tuple(shape)
    if len(self.shape) == 2:
      fmt = 'gray'
    elif len(self.shape) == 3 and self.shape[2] == 1:
      fmt = 'gray'
    elif len(self.shape) == 3 and self.shape[2] == 3:
      fmt = 'rgba'
    elif len(self.shape) == 3 and self.shape[2] == 4:
      fmt = 'rgba'
    else:
      raise ValueError(f"Unrecognized shape: {self.shape}.")

    cmd = [
      'ffmpeg',
      '-y',                     # overwrite existing file
      '-f', 'rawvideo',
      '-vcodec', 'rawvideo',
      '-s', f'{self.shape[1]}x{self.shape[0]}', # WxH
      '-pix_fmt', fmt,                          # byte format
      '-r', str(self.fps),                      # frames per second
      '-i', '-',                                # input from pipe
      '-an',                                    # no audio
      '-b', f'{self.bitrate}k',                 # bitrate, controls compression
      '-vcodec', 'mpeg4',
      self.fname]

    logger.info(' '.join(cmd))
    self.log = open(self.fname.split('.')[0] + '.log', 'w')
    self.proc = sp.Popen(cmd, stdin=sp.PIPE, stderr=self.log)
    
  def write(self, frame):
    """Write the frame to video.

    If shape was not provided on instantiation, and this is the first call to
    write, opens a ffmpeg process.

    Converts frame to uint8. If an integer type, performs a simple cast. If a
    float type, assumes the image is in range [0,1] and quantizes values to this
    range.

    :param frame: a numpy array of the proper shape.
    :returns: nothing

    """
    
    if self.shape is None:
      self.open(frame.shape)
    frame = self.as_uint(frame)
    if frame.shape[2] == 3:
      frame = np.insert(frame, 3, np.zeros((frame.shape[:2])), axis=2)
    self.proc.stdin.write(frame.tobytes())

  def write_fig(self, fig, close=True):
    """Write the matplotlib figure to the feed.

    :param fig: matplotlib figure
    :param close: close the figure when done with it.

    """
    fig.canvas.draw()
    self.write(np.array(fig.canvas.renderer._renderer))
    if close:
      plt.close()
    
  def close(self):
    self.proc.stdin.close()
    self.proc.wait()
    self.log.close()
    del self

  @staticmethod
  def as_uint(image):
    """Scale to uint8, clipping values outside the valid range. Assumes that
    float frames are in range [0,1].

    :param image: 
    :returns: 
    :rtype: 
    
    """
    if image.dtype == np.uint8:
      return image
    elif image.dtype in [np.float32, np.float64]:
      image = (255*np.clip(image, 0, 1.0)).astype(np.uint8)
    elif image.dtype in [np.int32, np.int64]:
      image = np.clip(image, 0, 255).astype(np.uint8)
    else:
      raise ValueError(f"image dtype '{image.dtype}' not allowed")
    return image

