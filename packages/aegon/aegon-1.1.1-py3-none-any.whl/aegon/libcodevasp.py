import os.path
import numpy as np
from ase.io import read
from ase import Atom, Atoms
#------------------------------------------------------------------------------------------
def get_termination_vasp(pathfilename):
    if os.path.isfile(pathfilename):
        file=open(pathfilename,'r')
        normal=0
        for line in file:
            if "General timing and accounting informations for this job" in line: normal=normal+1
        file.close()
        return normal
    else:
        return False
#------------------------------------------------------------------------------------------
#Provides the minimum energy structure of the optimization process, regardless of whether it converged correctly
def get_geometry_vasp_old(pathfilename):
    nt=get_termination_vasp(pathfilename)
    if nt==False: return False
    filename=os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    trajectory = read(pathfilename, index=':', format='vasp-out')
    enemin = float('inf')
    for i, atoms in enumerate(trajectory):
        energy=atoms.get_potential_energy()
        if energy < enemin:
            enemin=energy
            poscar=atoms.copy()
            poscar.info['c']=nt
            poscar.info['e']=energy
            poscar.info['i']=namein
    return poscar
#------------------------------------------------------------------------------------------
def get_geometry_vasp(pathfilename):
    nt=get_termination_vasp(pathfilename)
    if nt==False: return False
    filename=os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    trajectory = get_traj_vasp(pathfilename,False)
    enemin = float('inf')
    for i, atoms in enumerate(trajectory):
        energy=atoms.info['e']
        if energy < enemin:
            enemin=energy
            poscar=atoms.copy()
            poscar.info['c']=nt
            poscar.info['e']=energy
            poscar.info['i']=namein
    return poscar
#------------------------------------------------------------------------------------------
def get_traj_vasp_old(pathfilename, force=False):
    nt=get_termination_vasp(pathfilename)
    if nt==False: return False
    filename=os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    trajectory = read(pathfilename, index=':', format='vasp-out')
    atoms_list_out=[]
    for i, atoms in enumerate(trajectory):
        if force: atoms.arrays['forces']=atoms.get_forces()
        energy=atoms.get_potential_energy()
        atoms.info['c']=nt
        atoms.info['e']=energy
        atoms.info['i']=namein+str(i+1).zfill(3)
        atoms_list_out.extend([atoms])
    return atoms_list_out
#------------------------------------------------------------------------------------------
def get_traj_vasp(filename, force=False):
    namein=filename.split('.')[0]
    start, end, ene, elements,counts,matrices  = [], [], [], [], [], []
    openold = open(filename,"r")
    rline = openold.readlines()
    for i in range(len(rline)):
        if "direct lattice vectors" in rline[i]:
            matrix = np.zeros((3, 3))
            matrix[0,0],matrix[0,1],matrix[0,2]= float(rline[i+1].split()[0]),float(rline[i+1].split()[1]),float(rline[i+1].split()[2])
            matrix[1,0],matrix[1,1],matrix[1,2]= float(rline[i+2].split()[0]),float(rline[i+2].split()[1]),float(rline[i+2].split()[2])
            matrix[2,0],matrix[2,1],matrix[2,2] = float(rline[i+3].split()[0]),float(rline[i+3].split()[1]),float(rline[i+3].split()[2])
            matrices.append(matrix)
        elif "POSITION" in rline[i]:
            start.append(i+2)
            for j in range(i + 2, len(rline)):
                if set(rline[j].strip()) == {"-"}:
                    end.append(j - 1)
                    break
        elif "FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)" in rline[i]:
            ene.append(rline[i+2].split()[4])  # ELECTROVOLTS -EV
        elif "VRHFIN =" in rline[i]:
            elements.append(str(rline[i].split('=')[1].split(':')[0].strip()))
        elif "ions per type =" in rline[i]:
            counts = list(map(int, rline[i].split('=')[1].split()))
    elements_per_atoms = []
    for elem, count in zip(elements, counts):
        elements_per_atoms.extend([elem] * count)
    moleculeout=[]
    for i,iStart in enumerate(start):
        singlemol = Atoms()
        singlemol.info['e'] = float(ene[i])
        singlemol.info['i'] = namein+'_'+str(i+1).zfill(3)
        singlemol.cell = matrices[i]
        singlemol.pbc = True
        atom_index = 0
        for line in rline[start[i] : end[i]+1]:
            words = line.split()
            ss =  elements_per_atoms[atom_index]
            xc,yc,zc = float(words[0]), float(words[1]), float(words[2])
            ai=Atom(symbol=ss,position=(xc, yc, zc))
            singlemol.append(ai)
            atom_index += 1
        if force:
            forces_list_by_group = []
            for line in rline[start[i] : end[i]+1]:
                words = line.split()
                fx,fy,fz = float(words[3]), float(words[4]), float(words[5]) #eV/Angst
                forces_list_by_group.append([fx,fy,fz])
            singlemol.arrays['forces'] = np.array(forces_list_by_group)
        moleculeout.extend([singlemol])
    openold.close()
    return(moleculeout)
#------------------------------------------------------------------------------------------
