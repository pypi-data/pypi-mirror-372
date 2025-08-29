import os
import random
import numpy as np
from ase import Atom, Atoms
from ase.data import covalent_radii, chemical_symbols
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
#------------------------------------------------------------------------------------------
### MINIMUN DISTANCE BETWEEN ALL THE ATOM OBJECTS OF TWO ATOMS OBJECTS 
def distance_atoms2atoms(atoms1, atoms2):
    min_distance = float('inf')
    for atom1 in atoms1:
        r1=covalent_radii[atom1.number]
        for atom2 in atoms2:
            r2=covalent_radii[atom2.number]
            distance = np.linalg.norm(atom1.position - atom2.position)/(r1+r2)            
            if distance < min_distance:
                min_distance = distance
    return min_distance
#------------------------------------------------------------------------------------------
### MINIMUM DISTANCE BETWEEN A SINGLE ATOM (atom1) AND THE ATOMS IN AN ATOMS OBJECT (atoms2)
def distance_atom2atoms(atom1, atoms2):
    min_distance = float('inf')    
    r1=covalent_radii[atom1.number]
    for atom2 in atoms2:
        r2=covalent_radii[atom2.number]
        distance = np.linalg.norm(atom1.position - atom2.position)/(r1+r2)
        if distance < min_distance:
            min_distance = distance
    return min_distance
#------------------------------------------------------------------------------------------
### MINIMUM DISTANCE BETWEEN ALL THE ATOM OBJECT IN THE SAME ATOMS OBJECT
def distance_interatom(atoms):
    min_distance = float('inf')
    num_of_atoms = len(atoms)
    for ii in range(num_of_atoms):
        r1=covalent_radii[atoms[ii].number]
        for jj in range(ii+1, num_of_atoms):
            r2=covalent_radii[atoms[jj].number]
            distance = np.linalg.norm(atoms[ii].position - atoms[jj].position)/(r1+r2)
            if distance < min_distance:
                min_distance = distance
    return min_distance
#------------------------------------------------------------------------------------------
def centroid(atoms):
    posiciones = atoms.get_positions()
    centroide = np.mean(posiciones, axis=0)
    return centroide
#------------------------------------------------------------------------------------------
def radius_max(atoms):
    ctd=centroid(atoms)
    r=[np.linalg.norm(iatom.position - ctd) + covalent_radii[iatom.number] for iatom in atoms]
    r.sort()
    rmax=r[-1]
    return rmax
#------------------------------------------------------------------------------------------
def scale_coords(atoms, factor):
    rcoords = atoms.positions - atoms.get_center_of_mass()
    atomsout=atoms.copy()
    atomsout.positions = rcoords*factor
    return atomsout
#------------------------------------------------------------------------------------------
def adjacency_matrix(atoms, factor=1.2):
    natoms=len(atoms)
    matrixc=np.zeros(shape=(natoms,natoms),dtype=np.int64)
    for iatom in range(natoms):
        ri=covalent_radii[atoms[iatom].number]
        ipos=atoms[iatom].position
        for jatom in range(iatom+1,natoms):
            rj=covalent_radii[atoms[jatom].number]
            jpos = atoms[jatom].position
            distance = np.linalg.norm(jpos - ipos)/(ri+rj)
            if ( distance <= factor ):
                matrixc[iatom][jatom] = 1
                matrixc[jatom][iatom] = 1
    return matrixc
#------------------------------------------------------------------------------------------
def degree_matrix(atoms, factor=1.2):
    adj=adjacency_matrix(atoms, factor)    
    degrees = np.sum(adj, axis=1)
    degreematrix = np.diag(degrees)
    return degreematrix
#------------------------------------------------------------------------------------------
def connected_graph(atoms, factor=1.2):
    matrixadj=adjacency_matrix(atoms,factor)
    matrixadjp=matrixadj.copy()
    nd=len(matrixadjp)
    vectord=np.zeros(shape=(nd),dtype=np.int64)
    vectordp=np.array(vectord)
    vectord[0]=int(1)
    sumd=1
    while sumd != 0:
        vectord = np.dot(matrixadjp, vectord)
        vectord = vectord + vectordp
        for i, element in enumerate(vectord):
            if element > 1:
                vectord[i] = int(1)
        sumd=sum(vectord - vectordp)
        vectordp = vectord
    scg = 1 if ( nd==sum(vectord) ) else 0
    return scg
#------------------------------------------------------------------------------------------
def rand_unit_vector():
    ##SPHERE DISTRIBUTION
    phi=float(random.uniform(0.0, 2.0*(np.pi)))
    theta=float(random.uniform(0.0,(np.pi)))
    xu=np.sin(theta) * np.cos(phi)
    yu=np.sin(theta) * np.sin(phi)
    zu=np.cos(theta)
    return np.array([xu, yu, zu])
#------------------------------------------------------------------------------------------
def random_deg_angles():
    qmin,qmax=0,360
    qdegx=random.randint(qmin,qmax)
    qdegy=random.randint(qmin,qmax)
    qdegz=random.randint(qmin,qmax)
    return qdegx, qdegy, qdegz
#------------------------------------------------------------------------------------------
def euler_matrix(qdegx, qdegy, qdegz):
    qradx=float(qdegx)*(np.pi)/180.0
    qrady=float(qdegy)*(np.pi)/180.0
    qradz=float(qdegz)*(np.pi)/180.0
    ##qradz=np.deg2rad(qdegz)
    cx,cy,cz=np.cos(qradx),np.cos(qrady),np.cos(qradz)
    sx,sy,sz=np.sin(qradx),np.sin(qrady),np.sin(qradz)
    row1=[cy*cz,-cy*sz,sy]
    row2=[cx*sz+cz*sx*sy,cx*cz-sx*sy*sz,-cy*sx]
    row3=[sx*sz-cx*cz*sy,cz*sx+cx*sy*sz, cx*cy]
    eulerm=np.array([row1,row2,row3])
    return eulerm
#------------------------------------------------------------------------------------------
def rotate_matrix(moleculein, matrixr):
    moleculein.set_positions(np.dot(moleculein.get_positions(),matrixr.T))
    return moleculein
#------------------------------------------------------------------------------------------
def rotate_deg(moleculein, qdegx, qdegy, qdegz):
    eulerm=euler_matrix(qdegx, qdegy, qdegz)
    rotate_matrix(moleculein, eulerm)
    return moleculein
#------------------------------------------------------------------------------------------
def rotate_random(moleculein):
    qdegx, qdegy, qdegz=random_deg_angles()
    rotate_deg(moleculein, qdegx, qdegy, qdegz)
    return moleculein
#------------------------------------------------------------------------------------------
def rodrigues_rotation_matrix(kvector, qdeg):
    qrad=float(qdeg)*np.pi/180.0
    kvec=np.array(kvector)
    kuv=kvec/np.linalg.norm(kvec)
    kmat1 = np.array([[0.0, -kuv[2], kuv[1]], [kuv[2], 0.0, -kuv[0]], [-kuv[1], kuv[0], 0.0]])
    kmat2 = np.matmul(kmat1,kmat1)
    rodriguesrm = np.eye(3) + np.sin(qrad)*kmat1 + (1.0 - np.cos(qrad))*kmat2
    return rodriguesrm
#------------------------------------------------------------------------------------------
def rotate_vector_angle_deg(moleculein, kvector, qdeg):
    rodriguesrm=rodrigues_rotation_matrix(kvector, qdeg)
    rotate_matrix(moleculein, rodriguesrm)
    return moleculein
#------------------------------------------------------------------------------------------
def align(atoms):
    #vref=atoms.get_center_of_mass()
    vref=centroid(atoms)
    atoms.translate(-vref)
    evals,evec=atoms.get_moments_of_inertia(vectors=True)
    atoms.set_positions(np.dot(atoms.get_positions(), evec.T))
    #atoms.translate(+vref)
    return atoms
#------------------------------------------------------------------------------------------
def KuhnMunkres(mol1, mol2, use_elements=True):
    mol1_centered = mol1.positions - mol1.get_center_of_mass()
    mol2_centered = mol2.positions - mol2.get_center_of_mass()
    cost_matrix = cdist(mol1_centered, mol2_centered)
    if use_elements:
        symbols1 = mol1.get_chemical_symbols()
        symbols2 = mol2.get_chemical_symbols()
        for i in range(len(mol1)):
            for j in range(len(mol2)):
                if symbols1[i] != symbols2[j]:
                    cost_matrix[i, j] = 1e10
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    new_positions = mol2.positions[col_ind]
    new_symbols = [mol2.get_chemical_symbols()[i] for i in col_ind]
    aligned_mol2 = mol2.copy()
    aligned_mol2.symbols = new_symbols
    aligned_mol2.set_positions(new_positions)
    return aligned_mol2
#------------------------------------------------------------------------------------------
def rmsd(mol1, mol2):
    mol1_centered = mol1.positions - mol1.get_center_of_mass()
    mol2_centered = mol2.positions - mol2.get_center_of_mass()
    RMSD=np.sqrt(np.mean(np.sum((mol1_centered - mol2_centered)**2, axis=1)))    
    return RMSD
#------------------------------------------------------------------------------------------
def align_two(atoms1, atoms2):
    mol1=atoms1.copy()
    mol2=atoms2.copy()
    align(mol1)
    align(mol2)
    min_rms = float('inf')
    diccionario_matrix={}
    diccionario_matrix[0]=np.array([[+1.0,+0.0,+0.0], [+0.0,+1.0,+0.0], [+0.0,+0.0,+1.0]])
    diccionario_matrix[1]=np.array([[-1.0,+0.0,+0.0], [+0.0,-1.0,+0.0], [+0.0,+0.0,+1.0]])
    diccionario_matrix[2]=np.array([[+1.0,+0.0,+0.0], [+0.0,-1.0,+0.0], [+0.0,+0.0,-1.0]])
    diccionario_matrix[3]=np.array([[-1.0,+0.0,+0.0], [+0.0,+1.0,+0.0], [+0.0,+0.0,-1.0]])
    for i in diccionario_matrix.keys():
        mi=diccionario_matrix[i]
        mol2x=mol2.copy()
        mol2x.set_positions(np.dot(mol2x.get_positions(), mi.T))
        mol2_aligned = KuhnMunkres(mol1, mol2x)
        rms=rmsd(mol1, mol2_aligned)
        if rms < min_rms:
            imin=i
            min_rms = rms
            mol2sol=mol2_aligned.copy()
    print(imin)
    return mol1, mol2sol
#------------------------------------------------------------------------------------------
def align_list(atomlist):
    if len(atomlist) == 1:
        return [align(atomlist[0])]
    elif len(atomlist) == 2:
        mol1, mol2=align_two(atomlist[0], atomlist[1])
        return [mol1, mol2]
    elif len(atomlist) > 2:
        out_list=[align(atomlist[0])]
        for i in range(1,len(atomlist)):
            mol1, mol2=align_two(atomlist[i-1], atomlist[i])
            out_list.extend([mol2])
        return out_list
#------------------------------------------------------------------------------------------
def planarity_index(atoms):
    evals = atoms.get_moments_of_inertia()
    ia, ib, ic = evals[0], evals[1], evals[2]
    planarity = ic/(ia + ib)
    return planarity
#------------------------------------------------------------------------------------------
def merge_atoms(atoms_list):
    atomsout = atoms_list[0].copy()
    for index in range(1, len(atoms_list)):
        for iatom in atoms_list[index]:
            atomsout.append(iatom)
    return atomsout
#------------------------------------------------------------------------------------------
def is_number(s):
    try:
        float(s).is_integer()
        return True
    except ValueError:
        pass
#------------------------------------------------------------------------------------------
def readxyzs(filename):
    if not os.path.isfile(filename):
        print("The file",filename,"does not exist.")
    file=open(filename,'r')
    imol=-1
    moleculeout=[]
    for line in file:
        ls=line.split()
        if len(ls)==1:
            natoms=int(ls[0])
            count=0
            imol=imol+1
            line=file.readline()
            ls=line.split()
            if len(ls)==0: name,energy='unknown', float(0.0)
            if len(ls)==1: name,energy=str(ls[0]),float(0.0)
            if len(ls)>=2: name,energy=str(ls[1]),float(ls[0])
            mol = Atoms()
            mol.info['e'] = energy
            mol.info['i'] = name
        if len(ls)==4:
            sym=str(ls[0])
            si = chemical_symbols[int(sym)] if is_number(sym) else sym
            xc,yc,zc=float(ls[1]),float(ls[2]),float(ls[3])
            ai=Atom(symbol=si, position=(xc, yc, zc))
            mol.append(ai)
            count=count+1
            if count==natoms: moleculeout.extend([mol])
    file.close()
    return moleculeout
#------------------------------------------------------------------------------------------
def writexyzs(atoms_list, filename):
    if not isinstance(atoms_list, list): atoms_list = [atoms_list]
    fh=open(filename,"w")
    for atoms in atoms_list:
        print(len(atoms), file=fh)
        print("%12.8f     %s" %(atoms.info['e'], atoms.info['i']), file=fh)
        for atom in atoms:
            symbol = atom.symbol
            xc, yc, zc = atom.position
            print("%-2s %16.9f %16.9f %16.9f" %(symbol, xc, yc, zc), file=fh)
    fh.close()
    #if silence: print("Writing %s" %(filename))
#------------------------------------------------------------------------------------------
def rename(atoms_list, basename, ndigist):
    nnn=len(atoms_list)
    for imol in range(nnn):
        atoms_list[imol].info['i'] = basename+'_'+str(imol+1).zfill(ndigist)
    return atoms_list
#------------------------------------------------------------------------------------------
def sort_by_energy(atoms_list, opt=0):
    atoms_list_out=[]
    if len(atoms_list) == 0: return atoms_list_out
    s=[[imol,atoms.info['e']] for imol, atoms in enumerate(atoms_list)]
    t = sorted(s, key=lambda x: float(x[1]))
    energy_ref = t[0][1] if (opt==0) else float(0.0)
    for ii in t:
        atoms_tmp=atoms_list[ii[0]].copy()
        atoms_tmp.info['e']=ii[1] - energy_ref
        atoms_list_out.extend([atoms_tmp])
    return atoms_list_out
#------------------------------------------------------------------------------------------
def cutter_nonconnected(atoms_list, factor=1.2):
    moleculeout = []
    for imol in atoms_list:
        ans=connected_graph(imol, factor)
        if ( ans == 1 ):
            moleculeout.extend([imol])
    return moleculeout
#------------------------------------------------------------------------------------------
def cutter_energy(atoms_list, enemax):
    moleculesort=sort_by_energy(atoms_list, 1)
    emin0=moleculesort[0].info['e']
    moleculeout = []
    for imol in atoms_list:
        de=imol.info['e'] - emin0
        if ( de < float(enemax) ):
            moleculeout.extend([imol])
    return moleculeout
#------------------------------------------------------------------------------------------
def listflatten(ntotal,nproc):
    return [1]*ntotal if ntotal <= nproc else [int(ntotal/nproc)+int((ntotal%nproc)>ii) for ii in range(nproc)]
#------------------------------------------------------------------------------------------
def prepare_folders(poscarlist, nproc, base_name):
    ntot=len(poscarlist)
    lista=listflatten(ntot, nproc)
    li=0
    folderlist=[]
    for ii,ni in enumerate(lista):
        basename=base_name+'proc'+str(ii+1).zfill(3)
        folderlist.append(basename)
        if not os.path.exists(basename):
            os.system('mkdir %s' %(basename))
    return folderlist
#------------------------------------------------------------------------------------------
def split_poscarlist(poscarlist, nproc):
    ntot=len(poscarlist)
    lista=listflatten(ntot, nproc)
    li=0
    poscar_split_list=[]
    for ii,ni in enumerate(lista):
        ls=li+ni
        poscars=poscarlist[li:ls]
        poscar_split_list.append(poscars)
        li=ls
    return poscar_split_list
#------------------------------------------------------------------------------------------
