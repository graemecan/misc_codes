from scipy.io import FortranFile
import glob
import numpy as np

def read_ramses_part(output_dir):
    """Reads RAMSES particle data into NumPy arrays.
       Inputs: output_dir - directory containing particle data.
       Outputs: npart*3 NumPy array containing x, y, z positions.

       Note that all particle files are found in the directory.
    """

    list_of_files = glob.glob(output_dir+"/part_*")

    xpos_total = np.array([])
    ypos_total = np.array([])
    zpos_total = np.array([])

    npart_total = 0

    for filename in list_of_files:
        print("Reading file "+filename+"\n")
        f = FortranFile(filename, 'r')
        
        ncpu = f.read_record('<i4')
        ndim = f.read_record('<i4')
        npart = f.read_record('<i4')
        localseed = f.read_record('<i4')
        nstar_tot = f.read_record('<i4')
        mstar_tot = f.read_record('<f8')
        mstar_lost = f.read_record('<f8')
        nsink = f.read_record('<i4')

        xpos = f.read_record('<f8')
        ypos = f.read_record('<f8')
        zpos = f.read_record('<f8')

        f.close()

        #xvel = f.read_record('<f8')
        #yvel = f.read_record('<f8')
        #zvel = f.read_record('<f8')

        #mass = f.read_record('<f8')

        np.append(xpos_total, xpos)
        np.append(ypos_total, ypos)
        np.append(zpos_total, zpos)
        npart_total += npart
    
    pos = np.zeros((3,npart_total))

    pos[0,:] = xpos_total
    pos[1,:] = ypos_total
    pos[2,:] = zpos_total

    return pos
