
from dipy.tracking.streamline import Streamlines
import struct
import numpy as np

from dipy.io.streamline import load_trk, save_trk
from dipy.tracking import utils

import os.path   


##
## takes in a streamline object and a filename,
##  appends to that file (or writes if that file does not exist).
##
## if update_num_trk is True, we will also add the to trk header
##  the new number of total streamlines (assumes old number is correct).

def append_to_trk(
  streamlines,
  filename,
  update_num_trk=False,
  vox_to_ras=None,
  send_to_voxmm=None
  ):

  if not os.path.isfile(filename):
    raise FileNotFoundError("append_to_trk called on non-existant file")

  if send_to_voxmm is None:
    raise RuntimeError("append_to_trk:send_to_voxmm not set.\nsend_to_voxmm must be explicitly True or False (otherwise bad things could happen in the trk).")

  if send_to_voxmm and vox_to_ras is not None:
    #this clones behavior from 
    ## https://github.com/nipy/dipy/blob/master/dipy/io/trackvis.py#L27
    zooms = np.sqrt((vox_to_ras * vox_to_ras).sum(0))
    vox_to_trk = np.diag(zooms)
    vox_to_trk[3, 3] = 1
    vox_to_trk[:3, 3] = zooms[:3] / 2.
    streamlines = list(utils.move_streamlines(
      streamlines,
      input_space=vox_to_ras,
      output_space=vox_to_trk
    ))
  elif send_to_voxmm:
    raise RuntimeError("send_to_voxmm set, but no transform passed.")

  with open(filename, mode='r+b') as file:
    ##get header
    hdr = file.read(1000)

    size_idx = 1000-12
    num_trks = struct.unpack("i", hdr[size_idx:(size_idx+4)])[0]

    if num_trks == 0 and update_num_trk:
      print("Error, num_trks set to zero, cannot update num, aborting")
      exit(1)
    elif update_num_trk:
      #move to size_idx in hdr
      file.seek(size_idx,0)
      file.write(struct.pack("i", num_trks + len(streamlines[0])))

    #move to end of file
    file.seek(0,2)

    #iterate through streams and output
    for stream in np.array(streamlines):
      file.write(struct.pack("i",len(stream)))
      for row in stream:
        file.write(struct.pack("fff",row[0],row[1],row[2]))



if __name__ == "__main__":

  import argparse

  parser = argparse.ArgumentParser(description=\
    "Test Function for append_to_trk")

  parser.add_argument("--input")
  parser.add_argument("--test-load")
  args = parser.parse_args()

  streamlines = load_trk( args.test_load )
  streamlines = list(streamlines)[0]

  append_to_trk( list(streamlines), args.input, False, send_to_voxmm=False)




