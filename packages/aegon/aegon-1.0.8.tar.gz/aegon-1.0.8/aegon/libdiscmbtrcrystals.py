import os
import time
import numpy as np
from multiprocessing import Process
from dscribe.descriptors import MBTR, ValleOganov
from aegon.libposcar import readposcars, writeposcars
from aegon.libutils import prepare_folders, split_poscarlist
#------------------------------------------------------------------------------------------
def find_similar_elements(similarity_matrix, threshold):
    similar_elements_indices = []
    num_elements = similarity_matrix.shape[0]
    for i in range(num_elements):
        for j in range(i+1,num_elements):
            if similarity_matrix[i, j] >= threshold:
                similar_elements_indices.append(j)
    return similar_elements_indices
#------------------------------------------------------------------------------------------
def disc_MBTR(atoms, threshold, nproc=1):
    num_molecules = len(atoms)
    num_atomsxmol = len(atoms[0])
    species = set(atoms[0].get_chemical_symbols())
    r_cut=10
    geometry={"function": "distance"}
    grid={"min": 0, "max": r_cut, "sigma": 1E-5, "n" : 100}
    weighting = {"function": "inverse_square", "r_cut": r_cut,  "threshold": 1E-3}
    opt="none"
    #mbtr=MBTR(species=species, geometry=geometry, weighting=weighting,  grid=grid, periodic=True, normalization=opt, normalize_gaussians=True, sparse=False, dtype="float64")
    mbtr=ValleOganov(species=species,function='distance',n=100,sigma=1E-5,r_cut=10)
    n_features=mbtr.get_number_of_features()
    if nproc ==1:
        descriptors=[mbtr.create(imol) for imol in atoms]
    elif nproc > 1:
        descriptors=mbtr.create(atoms, n_jobs=nproc)
    similar_elements_indices = []
    similarity_matrix = np.zeros((num_molecules, num_molecules))
    for i in range(num_molecules):
        vi=descriptors[i]
        for j in range(i, num_molecules):
            vj=descriptors[j]
            manhattan_distance=sum([np.absolute(a-b) for a,b in zip(vi,vj)])
            similarity=1.0/(1.0+manhattan_distance/float(n_features))
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity
    similar_elements_indices=find_similar_elements(similarity_matrix, threshold)
    similar_elements_indices.sort()
    #print(similar_elements_indices)
    disimilars_atoms=[atoms[i] for i in range(num_molecules) if i not in similar_elements_indices]
    return disimilars_atoms
#------------------------------------------------------------------------------------------
def comparator_mbtr_conv(atoms0, threshold, nproc):
    start = time.time()
    ni=len(atoms0)
    atoms1=disc_MBTR(atoms0, threshold, nproc)
    nf=len(atoms1)
    end = time.time()
    print('Comparator MBTR conv at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return atoms1
#------------------------------------------------------------------------------------------
def make_comparator_mbtr(ifolder, threshold):
    atoms0=readposcars(ifolder+'/'+ifolder+'.vasp')
    atoms1=disc_MBTR(atoms0, threshold, 1)
    writeposcars(atoms1,ifolder+'/'+ifolder+'_disc.vasp', 'D', 1)
#------------------------------------------------------------------------------------------
def comparator_mbtr_parallel(poscarlist, threshold, nproc, base_name):
    start = time.time()
    ni=len(poscarlist)
    folderlist=prepare_folders(poscarlist, nproc, base_name)
    poscar_split_list=split_poscarlist(poscarlist, nproc)
    procs = []
    #dicc_term = {iposcar.info['i']: iposcar.info['c'] for iposcar in poscarlist}
    for ifolder, iposcars in zip(folderlist, poscar_split_list):
        writeposcars(iposcars, ifolder+'/'+ifolder+'.vasp', 'D', 1)
        proc = Process(target=make_comparator_mbtr, args=(ifolder,threshold,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    moleculeout=[]
    for ifolder in folderlist:
        molx=readposcars(ifolder+'/'+ifolder+'_disc.vasp')
        #for imol in molx: imol.info['c']=dicc_term[imol.info['i']]
        moleculeout=moleculeout+molx
    #os.system('rm -rf %sproc[0-9][0-9]' %(base_name))
    nf=len(moleculeout)
    end = time.time()
    print('MBTR comparison (parallel) at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return moleculeout
#------------------------------------------------------------------------------------------
