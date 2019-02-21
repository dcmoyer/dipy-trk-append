
from dipy.tracking.streamline import Streamlines
import struct
import numpy as np

from dipy.io.streamline import load_trk, save_trk
    

##
## takes in a streamline object and a filename,
##  appends to that file (or writes if that file does not exist).
##
## if update_num_trk is True, we will also add the to trk header
##  the new number of total streamlines (assumes old number is correct).

def append_to_trk( streamlines, filename, update_num_trk=False ):

  #TODO: check if file exists, if not write out like normal...

  print(len(streamlines[0]))

  with open(filename, mode='r+b') as file:
    ##get header
    hdr = file.read(1000)

    size_idx = 1000-12
    num_trks = struct.unpack("i", hdr[size_idx:(size_idx+4)])[0]
    #print(num_trks)

    if num_trks == 0 and update_num_trk:
      print("Error, num_trks set to zero, cannot update num, aborting")
      exit(1)
    elif update_num_trk:
      #move to size_idx in hdr
      file.seek(size_idx,0)
      file.write(struct.pack("i", num_trks + len(streamlines[0])))

    #move to end of file
    file.seek(0,2)

    #print(np.array(streamlines)[0][0])
    for stream in np.array(streamlines)[0]:
      file.write(struct.pack("i",len(stream)))
      #print(stream[0])
      #exit()
      for row in stream:
        file.write(struct.pack("fff",row[0],row[1],row[2]))
      #print(len(stream))
      #print(stream[0])



if __name__ == "__main__":

  import argparse

  parser = argparse.ArgumentParser(description=\
    "Test Function for append_to_trk")

  parser.add_argument("--input")
  parser.add_argument("--test-load")
  args = parser.parse_args()

  streamlines = load_trk( args.test_load )

  append_to_trk( streamlines, args.input, False)




