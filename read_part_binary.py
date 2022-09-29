import numpy as np
from scipy.io import FortranFile
import glob
import sys

datadir = sys.argv[1]

files = glob.glob(datadir+"/output_0*/part_0*")
if (len(files) == 0):
    files = glob.glob(datadir+"/part_0*")
    
if (len(files) == 0):
    print("No files found.")
    sys.exit()

fileDict = {}
for f in files:
    snapshot = int(f[-14:-9])
    if (snapshot in fileDict): ## Python 3 adjustment
        fileDict[snapshot].append(f)
    else:
        fileDict[snapshot] = [f]

ncpus = len(fileDict[list(fileDict.keys())[0]]) ## Python 3 adjustment

fileDict = dict(sorted(fileDict.items())) #Read files in numerical order (optional)

print("Found "+str(len(fileDict.keys()))+" snapshots, on "+str(ncpus)+" cpus.")

for snapshot in fileDict.keys():
    xpos, ypos, zpos = np.array([],dtype=np.float64), np.array([],dtype=np.float64), np.array([],dtype=np.float64)
    xvel, yvel, zvel = np.array([],dtype=np.float64), np.array([],dtype=np.float64), np.array([],dtype=np.float64)
    mp, idvals, levels = np.array([],dtype=np.float64), np.array([],dtype=np.int32), np.array([],dtype=np.int32)
    age, metallicity = np.array([],dtype=np.float64), np.array([],dtype=np.float64)
    for filename in fileDict[snapshot]:
        #print f
        f = FortranFile(filename,'r')

        ### Read header information
        ncpu = f.read_record(dtype=np.int32) #4 byte int
        ndim = f.read_record(dtype=np.int32) #4 byte int
        npartp = f.read_record(dtype=np.int32) #4 byte int
        localseed = f.read_record(dtype=np.int32) #4 4 byte integers
        nstar_tot = f.read_record(dtype=np.int32) #4 byte integer
        mstar_tot = f.read_record(dtype=np.float64) #8 byte float
        mstar_lost = f.read_record(dtype=np.float64) #8 byte float
        nsink = f.read_record(dtype=np.int32) #4 byte integer

        ### Read data
        if (npartp > 0):
            xpos = np.append(xpos, f.read_record(dtype=np.float64))
            if (ndim > 1):
                ypos = np.append(ypos, f.read_record(dtype=np.float64))
            if (ndim > 2):
                zpos = np.append(zpos, f.read_record(dtype=np.float64))
            xvel = np.append(xvel, f.read_record(dtype=np.float64))
            if (ndim > 1):
                yvel = np.append(yvel, f.read_record(dtype=np.float64))
            if (ndim > 2):
                zvel = np.append(zvel, f.read_record(dtype=np.float64))
            mp = np.append(mp, f.read_record(dtype=np.float64))
            idvals = np.append(idvals, f.read_record(dtype=np.int32))
            levels = np.append(levels, f.read_record(dtype=np.int32))
            if (nstar_tot > 0):
                age = np.append(age, f.read_record(dtype=np.float64))
                metallicity = np.append(metallicity, f.read_record(dtype=np.float64))

        f.close()

    ### Write snapshot as NumPy recarray
    ### THIS IS NON-GENERAL CODE THAT ASSUMES 3D DATA AND DOES NOT WRITE STELLAR AGES OR METALLICITY
    recarray_types = [('x','<f8'),('y','<f8'),('z','<f8'),('vx','<f8'),('vy','<f8'),('vz','<f8'),('m','<f8'),('id','<i4'),('l','<i4')]
    data = np.rec.fromarrays((xpos,ypos,zpos,xvel,yvel,zvel,mp,idvals,levels),dtype=recarray_types)

    inds = np.argsort(data['id']) #Sort particles by ID value, because multiple MPI outputs are read in arbitrary order
    sorted_data = data[inds]

    outfile = datadir+"/p_"+str(snapshot).zfill(5)
    np.save(outfile,sorted_data)
    print("Written snapshot "+str(snapshot)+" to NumPy binary file.")
    
