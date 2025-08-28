import os
import numpy as np 
from ase import Atom, Atoms
from ase.calculators.singlepoint import SinglePointCalculator
#------------------------------------------------------------------------------------------
hartree2eV = 27.211386245981 #NIST
bohr2angstrom=0.529177210544 #NIST
eVtokcalpermol=23.060548012069496
hartree2kcalmol=627.5094738898777
#------------------------------------------------------------------------------------------
def get_termination_orca(pathfilename):
    if os.path.isfile(pathfilename):
        normal=0
        file=open(pathfilename,'r')
        for line in file:
            if "ORCA TERMINATED NORMALLY" in line: normal=normal+1
        file.close()
        return normal
    else:
        return -1
#------------------------------------------------------------------------------------------
def get_energy_orca(pathfilename):
    eneinEh=0.0
    file = open(pathfilename,'r')
    for line in file:
        if 'Total Energy' in line:
            ls = line.split()
            if ls[4]=='Eh': eneinEh = float(ls[3])
    file.close()
    return eneinEh
#------------------------------------------------------------------------------------------
def get_geometry_orca(pathfilename):
    nt=get_termination_orca(pathfilename)
    if nt==False: return False
    filename=os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    ene=get_energy_orca(pathfilename)
    file=open(pathfilename,'r')
    for line in file:
        if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
            singlemol = Atoms()
            singlemol.info['e'] = ene #ENERGY IN Eh
            singlemol.info['i'] = namein
            line=file.readline()
            line=file.readline()
            ls = line.split()
            while len(ls)>0:
                ss,xc,yc,zc = ls[0],float(ls[1]), float(ls[2]), float(ls[3])
                ai=Atom(symbol=ss,position=(xc, yc, zc))
                singlemol.append(ai)
                line=file.readline()
                ls = line.split()
    file.close()
    return singlemol
#------------------------------------------------------------------------------------------
def get_traj_orca(pathfilename, force=False):
    filename = os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    N = 0
    start, end, ene, start_2, end_2 = [], [], [], [], []
    openold = open(pathfilename,"r")
    rline = openold.readlines()
    for i in range(len(rline)):
        if "GEOMETRY OPTIMIZATION CYCLE" in rline[i]:
            N +=1
        if "CARTESIAN COORDINATES (ANGSTROEM)" in rline[i]:
            start.append(i+2)
            for j in range(i + 2, len(rline)):
                if rline[j].strip() == "":
                    end.append(j - 1)
                    break
        if "TOTAL SCF ENERGY" in rline[i]:
            eneline = rline[i+3].split()
            ene.append(eneline[3])   #ENERGY IN Eh
        if "CARTESIAN GRADIENT" in rline[i] and force:
            start_2.append(i+3)
            for j in range(i + 3, len(rline)):
                if rline[j].strip() == "":
                    end_2.append(j - 1)
                    break
    moleculeout=[]
    for i in range(N):
        singlemol = Atoms()
        singlemol.info['e'] = float(ene[i]) #ENERGY IN Eh
        singlemol.info['i'] = namein+'_'+str(i+1).zfill(3)
        for line in rline[start[i] : end[i]+1]:
            words = line.split()
            ss = str(words[0])
            xc,yc,zc = float(words[1]), float(words[2]), float(words[3])
            ai=Atom(symbol=ss,position=(xc, yc, zc))
            singlemol.append(ai)
        if force:
            forces_list_by_group = []
            for line in rline[start_2[i] : end_2[i]+1]:
                words = line.split()
                fx,fy,fz = float(words[3]), float(words[4]), float(words[5])
                fx=-fx/bohr2angstrom #Eh/A
                fy=-fy/bohr2angstrom #Eh/A
                fz=-fz/bohr2angstrom #Eh/A
                forces_list_by_group.append([fx,fy,fz])
            singlemol.arrays['forces'] = np.array(forces_list_by_group)
        moleculeout.extend([singlemol])
    openold.close()
    return (moleculeout)
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
def read_traj_coords(pathfilename_coordinates):
    file=open(pathfilename_coordinates,'r')
    moleculeout=[]
    unicos=[]
    for line in file:
        ls=line.split()
        if len(ls)==1:
            natoms=int(ls[0])
            count=0
            line=file.readline()
            ls=line.split()
            k=int(ls[5].split(',')[0])
            mol = Atoms()
        if len(ls)==4:
            ss = str(ls[0])
            xc,yc,zc = float(ls[1]), float(ls[2]), float(ls[3])        #Angstrom
            ai=Atom(symbol=ss, position=(xc, yc, zc))
            mol.append(ai)
            count=count+1
            if (count==natoms) and k not in unicos:
                moleculeout.extend([mol])
                unicos.append(k)
    file.close()
    return moleculeout
#------------------------------------------------------------------------------------------
def read_traj_forces(pathfilename_forces):
    file=open(pathfilename_forces,'r')
    allforces=[]
    unicos=[]
    for line in file:
        ls=line.split()
        if len(ls)==1:
            natoms=int(ls[0])
            count=0
            line=file.readline()
            if "Unit is kJ mol^-1 Angstrom^-1" in line:
                hartree2joule=4.359744722206
                avogadro=6.02214076
                factor=1.0/(hartree2joule*avogadro*100.0)
            elif "Unit is Hartree/Angstrom" in line:
                factor=1.0
            else:
                print(pathfilename_forces, "ERROR Units")
            ls=line.split()
            k=int(ls[5].split(',')[0])
            forces_list_by_group = []
        if len(ls)==4:
            ss = str(ls[0])
            fx,fy,fz = float(ls[1]), float(ls[2]), float(ls[3])
            fx=-fx*factor   #FORCE IN Eh/A
            fy=-fy*factor   #FORCE IN Eh/A
            fz=-fz*factor   #FORCE IN Eh/A
            forces_list_by_group.append([fx,fy,fz])
            count=count+1
            if (count==natoms) and k not in unicos:
                allforces.append(forces_list_by_group)
                unicos.append(k)
    file.close()
    return allforces
#------------------------------------------------------------------------------------------
def read_traj_enes(pathfilename_out):
    energy_list = []
    openold_e = open(pathfilename_out,"r")
    for line in openold_e:
        if "Step |  Sim. Time | Iter |  t_Ener |  t_Grad |     Temp |     E_Kin |         E_Pot |         E_Tot |      Cons.Qty | E.Drift" in line:
            line=openold_e.readline()
            line=openold_e.readline()
            line=openold_e.readline()
            while line.startswith(" "):
                ls = line.split()
                ene=float(ls[6]) if ls[0]=='0' else float(ls[7]) #ENERGY IN Eh
                energy_list.append(ene)
                line=openold_e.readline()
    return energy_list
#------------------------------------------------------------------------------------------
def get_extxyz(pathfilename_coordinates, pathfilename_forces, pathfilename_out):
    ene=read_traj_enes(pathfilename_out)
    frc=read_traj_forces(pathfilename_forces)
    xyz=read_traj_coords(pathfilename_coordinates)
    #filename_one = os.path.basename(pathfilename_out)
    #namein_one = filename_one.split('.')[0]
    atoms_list_out=[]
    if len(ene) == len(frc) == len(xyz):
        for i in range(len(ene)):
            imol=xyz[i]
            atoms = Atoms(imol.symbols, positions=imol.positions, cell=[0, 0, 0], pbc=False)
            atoms.calc = SinglePointCalculator(atoms, energy=ene[i])
            atoms.arrays['forces']=np.array(frc[i])
            #atoms.info['i']=namein_one+'_'+str(i+1).zfill(3)
            atoms_list_out.extend([atoms])
    else: print('length error in %s' %(pathfilename_out))
    return atoms_list_out
#------------------------------------------------------------------------------------------
def example():
    import glob
    from ase.io import read, write
    files=sorted(glob.glob('*.out'))
    atoms_list_out=[]
    for ifile in files:
        basename=ifile.split('.')[0]
        traj=get_extxyz(basename+'.traj.xyz', basename+'.frc.xyz', basename+'.out')
        write(basename+'_ext.xyz', traj, format="extxyz")
        atoms_list_out=atoms_list_out+traj
    write('traj_ext.xyz', atoms_list_out, format="extxyz")
#example()
