import numpy as np
from rdkit import Chem
from ase.data import covalent_radii
#------------------------------------------------------------------------------------------
def adjmatrixfromsdfconectivity(rdkitmol):
    natoms=rdkitmol.GetNumAtoms()
    matrixcd=np.zeros(shape=(natoms,natoms),dtype=int)
    for bond in rdkitmol.GetBonds():
       i=bond.GetBeginAtomIdx()
       j=bond.GetEndAtomIdx()
       o=bond.GetBondTypeAsDouble()
       if o > 0.0:
           matrixcd[i][j] = int(1)
           matrixcd[j][i] = int(1)
    return matrixcd
#------------------------------------------------------------------------------------------
def adjmatrixfromsdfpositions(rdkitmol, factor=1.2):
    natoms=rdkitmol.GetNumAtoms()
    conf = rdkitmol.GetConformer()
    matrixc=np.zeros(shape=(natoms,natoms),dtype=int)
    for i in range(natoms):
        si=rdkitmol.GetAtomWithIdx(i).GetSymbol()
        ri=get_covalent_radius(si)
        vi=conf.GetAtomPosition(i)
        xi,yi,zi=float(vi.x), float(vi.y), float(vi.z)
        for j in range(i+1,natoms):
            sj=rdkitmol.GetAtomWithIdx(j).GetSymbol()
            rj=get_covalent_radius(sj)
            vj=conf.GetAtomPosition(j)
            xj,yj,zj=float(vj.x), float(vj.y), float(vj.z)
            xx,yy,zz=xj-xi, yj-yi, zj-zi
            distance = np.sqrt(xx*xx+yy*yy+zz*zz)
            dist = distance/(ri + rj)
            if ( dist <= factor ):
                matrixc[i][j] = int(1)
                matrixc[j][i] = int(1)
    return matrixc
#------------------------------------------------------------------------------------------
def rdkitmol2asemol(rdkitmol):
    symbols=[atom.GetSymbol() for atom in rdkitmol.GetAtoms()] 
    positions=rdkitmol.GetConformer().GetPositions()
    asemol=Atoms(symbols=symbols, positions=positions)
    return asemol
#------------------------------------------------------------------------------------------
def asemol2rdkitmol(molase, factor=1.2):
    natoms=molase.get_global_number_of_atoms()
    symbols=molase.get_chemical_symbols()
    r=[covalent_radii[k] for k in molase.numbers]
    positions=molase.get_positions()
    molrdkit = Chem.RWMol()
    conformer = Chem.Conformer(natoms)
    bond_info=[]
    for i in range(natoms):
        atom = Chem.Atom(symbols[i])
        molrdkit.AddAtom(atom)
        conformer.SetAtomPosition(i, positions[i][:])
        for j in range(i+1,natoms):
            dij=molase.get_distances(i,j)/(r[i] + r[j])
            if ( dij <= factor ):
                bond_info.append((i, j, Chem.rdchem.BondType.SINGLE))
    molrdkit.AddConformer(conformer)
    for bond in bond_info:
        atom1_idx, atom2_idx, bond_type = bond
        molrdkit.AddBond(atom1_idx, atom2_idx, bond_type)
    return molrdkit
#------------------------------------------------------------------------------------------
