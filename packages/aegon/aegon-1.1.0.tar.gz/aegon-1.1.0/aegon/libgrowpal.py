import os
import time
import numpy as np
from ase import Atom
from multiprocessing import Process
from aegon.libpymatgen import inequivalent_finder
from aegon.libutils import rename, adjacency_matrix, readxyzs, writexyzs, prepare_folders, split_poscarlist
#from aegon.libdiscusr import molin_sim_molref
#------------------------------------------------------------------------------------------
def neighbor_finder(atoms, dtol=1.2):
    '''
    This function builds a dictionary that contains the neighbors of all atoms
    
    in: adj_mtx (list); a list of list elements that represent the adjacency matrix 
        of the molecule as a graph.
    out: dict_neig (dict); a dictionary containing as keys the position of the atom 
        in the molecule.atoms list, and as values a list of all its neighbors.
        ({0:[1,3,7,11], 1:[0,7],...})
    '''
    dict_neig = {}
    conta = 0
    adj_mtx = adjacency_matrix(atoms, dtol)
    for i in adj_mtx:
        neig = []
        contb = 0
        for j in i:
            if j == 1:
                neig.append(contb)
            contb = contb + 1
        dict_neig[conta] = neig
        conta = conta + 1
    return dict_neig
#------------------------------------------------------------------------------------------
def triangle_finder(neighbors_dict,atom):
    '''
    This function finds the triangles formed by the binded atoms in a molecule
    in: neighbors_dict (Dict), the keys are position of the atom in the Molecule.atoms list, 
        and the values are a list of all their neighbors
        atom (int), the atom whose triangles are to be found
    out: triangles (list), a list of all 3 atoms that form each triangle 
    '''
    triangles = []
    # For this atom find its neighbors
    neiga = neighbors_dict[atom]
    for n in neiga:
        # For every neighbor find its own neighbors
        neigb = neighbors_dict[n]
        for n2 in neigb:
            # Check if this neighbor is in common with the original and if so save it
            if n2 in neiga:
                auxlist = [atom,n,n2]
                auxlist.sort()
                if auxlist in triangles:
                    continue
                triangles.append(auxlist)
    return triangles
#------------------------------------------------------------------------------------------
def focused_expansion(molin, vector):
    molout = molin.copy()
    rcoords=[]
    for a in molout.positions:
        r = np.array(a) - vector
        delta = np.linalg.norm(r)
        rnorm = r/delta
        edel = np.exp(-delta)*1.2
        a = np.array(a) + rnorm*edel
        rcoords.append(a)
    molout.positions =rcoords
    return molout
#------------------------------------------------------------------------------------------
def add_all_interstitial_atoms(original_molecule, neighbors_dict, specie):
    visited_t = []
    xxx_mol = original_molecule.copy()
    atom_list = range(len(original_molecule))
    for a in atom_list:
        # find the triangles composed by each atom in the list
        triangles = triangle_finder(neighbors_dict,a)
        for t in triangles:
            if t in visited_t:
                continue
            add_mol = original_molecule.copy()
            # get all the three vectors and its middle point
            atm1 = add_mol[t[0]].position
            atm2 = add_mol[t[1]].position
            atm3 = add_mol[t[2]].position
            v1 = np.array(atm1)
            v2 = np.array(atm2)
            v3 = np.array(atm3)
            mid_vect = (v1 + v2 + v3) / 3
            add_atom = Atom(symbol=specie, position=(mid_vect[0],mid_vect[1],mid_vect[2]))
            xxx_mol.append(add_atom)
            visited_t.append(t)
    return xxx_mol
#------------------------------------------------------------------------------------------
def add_ineq_interstitial_atoms_with_expansion(original_molecule, atom_list):
    molist_out = []
    for add_atom in atom_list:
        mid_vect = np.array(add_atom.position)
        add_mol = original_molecule.copy()
        exp_mol = focused_expansion(add_mol, mid_vect)
        exp_mol.append(add_atom)
        molist_out.append(exp_mol)
    return molist_out
#------------------------------------------------------------------------------------------
def growpal(molist_in, specie, dtol=1.2):
    '''
    This function masters all the above to add a new atom to each of the inequivalent atoms that belong
    to the outter layer of the molecule. It uses two types of addition: a.- Directly above of the atoms and 
    b.- in between two adjacent neighbors.
    in: molist_in (list[Molecule]); all the molecules that will receive an extra atom
        species (str); the species of the atom to be additioned
    out: molist_out (list[Molecule]);  a list that contains all the molecules with the extra atom 
    '''
    molist_out = []
    for imol in molist_in:
        org_nnn = len(imol)
        org_mol = imol.copy()
        org_mol.info['e'] = 0.0
        org_mol.translate(-org_mol.get_center_of_mass())
        ##FIND A DICT WITH ALL THE NEIGHBORS
        all_neighbors = neighbor_finder(org_mol, dtol)
        ##ADD specie IN ALL POSSIBLE TRIANGLES. WITHOUT ANY EXPANSION
        xxx_mol = add_all_interstitial_atoms(org_mol, all_neighbors, specie)
        inequivalent = inequivalent_finder(xxx_mol)
        ##BUILD THE LIST OF ADDED-INEQUIVALENT atom OBJECTS
        elegible_atoms=[xxx_mol[i] for i in inequivalent if i >= org_nnn]
        ##STRUCTURE WITH EXPANSIONS FOR THE ADDED-INEQUIVALENT ATOMS
        mod_mol=add_ineq_interstitial_atoms_with_expansion(org_mol, elegible_atoms)
        mod_mol=rename(mod_mol, imol.info['i'], 4)
        molist_out.extend(mod_mol)
    return molist_out
#------------------------------------------------------------------------------------------
def growpal_serial(poscarlist, specie, dtol=1.2):
    start = time.time()
    atoms1=growpal(poscarlist, specie, dtol)
    end = time.time()
    print('GrowPal generation at %5.2f s' %(end - start))
    return atoms1
#------------------------------------------------------------------------------------------
def make_growpal(ifolder, specie, dtol=1.2):
    atoms0=readxyzs(ifolder+'/'+ifolder+'.xyz')
    atoms1=growpal(atoms0, specie, dtol)
    writexyzs(atoms1,ifolder+'/'+ifolder+'_growpal.xyz')
    return 0
#------------------------------------------------------------------------------------------
def growpal_parallel(poscarlist, specie, nproc, base_name, dtol=1.2, tol=0.95):
    start = time.time()
    if not isinstance(poscarlist, list): poscarlist = [poscarlist]
    folderlist=prepare_folders(poscarlist, nproc, base_name)
    poscar_split_list=split_poscarlist(poscarlist, nproc)
    procs = []
    for ifolder, iposcars in zip(folderlist, poscar_split_list):
        writexyzs(iposcars, ifolder+'/'+ifolder+'.xyz')
        proc = Process(target=make_growpal, args=(ifolder,specie,dtol,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    moleculeout=[]
    for ifolder in folderlist:
        molx=readxyzs(ifolder+'/'+ifolder+'_growpal.xyz')
        #molx=molin_sim_molref(molx,moleculeout, tol)
        moleculeout=moleculeout+molx
    end = time.time()
    print('GrowPal (parallel) at %5.2f s [%d]' %(end - start, len(moleculeout)))
    os.system('rm -rf %sproc[0-9][0-9]' %(base_name))
    return moleculeout
#------------------------------------------------------------------------------------------
#from aegon.libsyva  import sym_syva
#from aegon.libutils import readxyzs, writexyzs
#mol1=readxyzs('b16.xyz')
#mol1=sym_syva(mol1)
#mol2=make_many_rand(mol1, 'Be')
#writexyzs(mol2,'out.xyz')
