import os.path
import numpy as np
from ase import Atom, Atoms
from ase.data import chemical_symbols
#------------------------------------------------------------------------------------------
hartree2eV = 27.211386245981 #NIST
bohr2angstrom=0.529177210544 #NIST
eVtokcalpermol=23.060548012069496
hartree2kcalmol=627.5094738898777
#------------------------------------------------------------------------------------------
def get_termination_gaussian(pathfilename):
    if os.path.isfile(pathfilename):
        normal=0
        gaufile=open(pathfilename,'r')
        for line in gaufile:
            if "Normal termination" in line: normal=normal+1
        gaufile.close()
        return normal
    else:
        return -1
#------------------------------------------------------------------------------------------
def get_energy_gaussian(filename):
    enehartree=float(0.0)
    gaufile=open(filename,'r')
    for line in gaufile:
        if "SCF Done" in line:
            scf=line.split()
            enehartree=float(scf[4])
    gaufile.close()
    enekcalmol=enehartree*hartree2kcalmol
    #eneeV = enehartree * hartree2eV
    return enekcalmol
#------------------------------------------------------------------------------------------
def get_geometry_gaussian(pathfilename):
    nt=get_termination_gaussian(pathfilename)
    if nt==-1: return False
    energy=get_energy_gaussian(pathfilename)
    filename = os.path.basename(pathfilename)
    namein=filename.split('.')[0] 
    gaufile=open(pathfilename,'r')
    for line in gaufile:
        if line.strip() in ("Input orientation:", "Standard orientation:"):
            moleculeout = Atoms()
            moleculeout.info['c'] = nt
            moleculeout.info['e'] = energy
            moleculeout.info['i'] = namein
            for ii in range(4): line=gaufile.readline()
            line=gaufile.readline()
            while not line.startswith(" --------"):
                ls = line.split()
                if (len(ls) == 6 and ls[0].isdigit() and ls[1].isdigit() and ls[2].isdigit()):
                    numero_atomico=int(ls[1])
                    ss = chemical_symbols[numero_atomico]
                    xc,yc,zc = float(ls[3]), float(ls[4]), float(ls[5])
                    ai=Atom(symbol=ss, position=(xc, yc, zc))
                    moleculeout.append(ai)
                else:
                    break
                line=gaufile.readline()
                ls = line.split()
    gaufile.close()
    return moleculeout
#------------------------------------------------------------------------------------------
def get_traj_gaussian(pathfilename, force=False):
    nt=get_termination_gaussian(pathfilename)
    if nt==-1: return False
    filename=os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    start, end, ene, start_2, end_2 = [], [], [], [], []
    openold = open(pathfilename,"r")
    rline = openold.readlines()
    for i in range(len(rline)):
        if "Standard orientation:" in rline[i]:
            start.append(i+5)
            for j in range(i+5, len(rline)):
                if rline[j].strip().startswith("-"):
                    end.append(j - 1)
                    break
        if "Forces (Hartrees/Bohr)" in rline[i] and force:
            start_2.append(i+3)
            for j in range(i + 3, len(rline)):
                if rline[j].strip().startswith("-"):
                    end_2.append(j - 1)
                    break
        if "SCF Done" in rline[i]:
            eneline = rline[i].split()
            ene.append(eneline[4])      
    moleculeout=[]
    for i,iStart in enumerate(start[:-1]):
        enehartree=float(ene[i])
        eneeV = enehartree * hartree2eV
        singlemol = Atoms()
        singlemol.info['e'] = eneeV
        singlemol.info['c'] = nt
        singlemol.info['i'] = namein+'_'+str(i+1).zfill(3)
        for line in rline[start[i] : end[i]+1]:
            words = line.split() 
            numero_atomico = int(words[1])
            ss = chemical_symbols[numero_atomico]
            xc,yc,zc = float(words[3]), float(words[4]), float(words[5])
            ai=Atom(symbol=ss,position=(xc, yc, zc))
            singlemol.append(ai)
        if force:           
            forces_list_by_group = []
            for line in rline[start_2[i] : end_2[i]+1]:
                words = line.split()
                fx,fy,fz = float(words[2]), float(words[3]), float(words[4])
                fx=fx*hartree2eV/bohr2angstrom
                fy=fy*hartree2eV/bohr2angstrom
                fz=fz*hartree2eV/bohr2angstrom
                #IN ev/A
                forces_list_by_group.append([fx,fy,fz])
            singlemol.arrays['forces'] = np.array(forces_list_by_group)
        moleculeout.extend([singlemol])
    openold.close()
    return (moleculeout)
#------------------------------------------------------------------------------------------
def get_freqneg_gaussian(pathfilename):
    gaufile=open(pathfilename,'r')
    freq_negative=0
    freq_neg_list=[]
    for line in gaufile:
        if "Frequencies" in line:
            freq=line.split()[2:]
            for ifreq in freq:
                if float(ifreq) < 0.0:
                    freq_negative=freq_negative+1
                    freq_neg_list.append(float(ifreq))
    gaufile.close()
    freq_neg_list.sort()
    freq_sample= freq_neg_list[0] if (freq_negative > 0) else 0.0
    return freq_negative, freq_sample
#------------------------------------------------------------------------------------------
def get_freqlist(pathfilename):
    filename = os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    cfreq=0
    freq_list=[]
    grupo_atoms = {}
    gaufile=open(pathfilename,'r')
    for line in gaufile:
        if "Frequencies" in line:
            freq=line.split()[2:]
            nfreq=len(freq)
            freq_list = freq_list + [float(ifreq) for ifreq in freq]
            for ii in range(5): line=gaufile.readline()
            while len(line.split()) > 3:
                coords=line.split()
                ss=chemical_symbols[int(coords[1])]
                for jj, jfreq in enumerate(range(cfreq, nfreq+cfreq)):
                    xyz=coords[3*jj+2:3*jj+3+2]
                    dxc,dyc,dzc=float(xyz[0]),float(xyz[1]),float(xyz[2])
                    ai=Atom(symbol=ss, position=(dxc, dyc, dzc))
                    grupo_atoms.setdefault(jfreq, []).append(ai)
                line=gaufile.readline()
            cfreq=cfreq+nfreq
    gaufile.close()
    moleculeout = [Atoms(atomos) for atomos in grupo_atoms.values()]
    for i in range(len(moleculeout)):
        moleculeout[i].info['e'] = freq_list[i]
        moleculeout[i].info['i'] = namein+str(i+1).zfill(3)
    return moleculeout
#------------------------------------------------------------------------------------------
def operador_pm(moleculein, moleculedt, amplitud):
    moleculeout=moleculein.copy()
    moleculeout.set_positions(moleculeout.get_positions() + amplitud*moleculedt.get_positions())
    return moleculeout
#------------------------------------------------------------------------------------------
def displace_along_imaginary_mode(pathfilename, amplitud=0.4):
    mol0=get_geometry_gaussian(pathfilename)
    mold=get_freqlist(pathfilename)
    if mold[0].info['e'] < float(0.0):
        #SE TOMA LA MAS NEGATIVA
        molpm=operador_pm(mol0, mold[0], amplitud)
        return molpm
    else:
        return False
#from aegon.libcodegaussian import displace_along_imaginary_mode
#from aegon.libutils import writexyzs
#molx=displace_along_imaginary_mode('smi012.out')
#writexyzs([molx],'tmp.xyz')
#------------------------------------------------------------------------------------------
def make_a_input(singlemol, level='#WB97XD def2TZVP OPT SCF=(XQC) FREQ' , folder='./'):
    nameinp=singlemol.info['i']+'.inp'
    fh=open(folder+nameinp,"w")
    print("%NprocShared=13", file=fh)
    print("%MEM=16GB", file=fh)
    print("%s\n" %(level), file=fh)
    print("Comment: %s\n" %(singlemol.info['i']), file=fh)
    print("%d %d" %(singlemol.info['q'],singlemol.info['m']), file=fh)
    for iatom in singlemol:
        sym = iatom.symbol
        xc, yc, zc = iatom.position
        print ("%-2s %16.9f %16.9f %16.9f" % (sym,xc,yc,zc), file=fh)
    fh.write("\n")
    fh.close()
#------------------------------------------------------------------------------------------
