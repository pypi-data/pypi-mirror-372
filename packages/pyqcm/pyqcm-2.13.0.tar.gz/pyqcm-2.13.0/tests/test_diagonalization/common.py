import numpy as np


def extract_GS_energy(f_in):
    src = open(f_in, 'r')
    gs_energy = {} #sector, energy
    for line in src.readlines():
        if 'GS_energy:' in line:
            data = line.split()
            gs_energy[data[-1]] = float(data[1])
    src.close()
    return gs_energy

def extract_pole(f_in):
    src = open(f_in, 'r')
    lines = src.readlines()
    src.close()
    data = []
    for i,line in enumerate(lines):
        if line[0:2] == "w\t":
            n_pole = int(line.split()[-1])
            values = [np.fromstring(x,sep="\t",dtype='f8').tolist() for x in lines[i+1:i+n_pole+1]]
            data.append(np.array(values, dtype='f8'))
    return data
