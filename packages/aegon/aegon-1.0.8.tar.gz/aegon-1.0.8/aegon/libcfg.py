import os
import numpy as np
from ase import Atom, Atoms
from ase.data import chemical_symbols
from aegon.libposcar import tag
#------------------------------------------------------------------------------------------
def readcfgs(filename):
    if not os.path.isfile(filename):
        print(f"El archivo {filename} no existe.")
        return []
    moleculas = [] 
    singlemol = None  
    natom = 0 
    with open(filename, 'r') as contcarfile:
        for line in contcarfile:
            line = line.strip()
            if line == "BEGIN_CFG":
                if singlemol: 
                    moleculas.append(singlemol)
                singlemol = Atoms()  
            elif "Size" in line:
                size_line = contcarfile.readline().strip()
                natom = int(size_line)
            elif "AtomData" in line:
                for _ in range(natom):
                    coord_line = contcarfile.readline().strip()
                    ls = coord_line.split()
                    numero_atomico = int(5) #Escribir ls[1]  
                    ss = chemical_symbols[numero_atomico] 
                    xc, yc, zc = float(ls[2]), float(ls[3]), float(ls[4])
                    ai = Atom(symbol=ss, position=(xc, yc, zc))
                    singlemol.append(ai)
                    #print(f"tomo aadido: {ai}") 
            elif line == "Energy":
                energy_line = contcarfile.readline().strip()
                energy = float(energy_line)
                singlemol.info['e'] = energy
                singlemol.info['i'] = '_'
                #print(f"Energa registrada: {energy}")
        if singlemol:
            moleculas.append(singlemol)
    return moleculas
#------------------------------------------------------------------------------------------
def writecfgs(poscarlist, file, force=False):
    if not isinstance(poscarlist, list): poscarlist = [poscarlist]
    f=open(file,"w")
    poscarlist=tag(poscarlist)
    for atoms in poscarlist:
        print("BEGIN_CFG", file=f)
        print(" Size", file=f)
        natoms=len(atoms)
        print("    %d" %(natoms), file=f)
        if np.any(atoms.pbc):
            print(" Supercell", file=f)
            matrix=atoms.cell
            print("       %10.6f    %10.6f    %10.6f" %(matrix[0,0],matrix[0,1],matrix[0,2]), file=f)
            print("       %10.6f    %10.6f    %10.6f" %(matrix[1,0],matrix[1,1],matrix[1,2]), file=f)
            print("       %10.6f    %10.6f    %10.6f" %(matrix[2,0],matrix[2,1],matrix[2,2]), file=f)
        if force:
            print(" AtomData:  id type       cartes_x      cartes_y      cartes_z           fx          fy          fz",file=f)
            forces=atoms.arrays['forces']
            for k, atom in enumerate(atoms):
                xc, yc, zc = atom.position
                fx, fy, fz=forces[k]
                tipo = atom.tag
                print("            %2d    %d     %10.6f    %10.6f    %10.6f    %9.6f   %9.6f   %9.6f" %(k+1,tipo,xc,yc,zc,fx,fy,fz), file=f)
        else:
            print(" AtomData:  id type       cartes_x      cartes_y      cartes_z", file=f)
            for k, atom in enumerate(atoms):
                xc, yc, zc = atom.position
                tipo = atom.tag
                print("             %d    %d     %10.6f    %10.6f    %10.6f" %(k+1,tipo,xc,yc,zc), file=f)
        print(" Energy", file=f)
        energy=atoms.info['e']
        print("        %12.8f" %(energy), file=f)
        print(" Feature   EFS_by    VASP", file=f)
        print("END_CFG\n", file=f)
    f.close()
#------------------------------------------------------------------------------------------
