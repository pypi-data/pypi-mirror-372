import os
import time
import numpy as np
from multiprocessing import Process
from ase.data import atomic_masses
from aegon.libutils import readxyzs, writexyzs, centroid, sort_by_energy, prepare_folders, split_poscarlist
tolsij=0.95
tolene=0.10
#------------------------------------------------------------------------------------------
#Ultrafast Shape Recognition (USR) Algorithm
#------------------------------------------------------------------------------------------
def lastwo_central_moment(listxxx):
    xavg=np.mean(listxxx)
    res = listxxx - xavg
    ssq2 = np.mean(res**2) 
    ssq3 = np.mean(res**3) 
    return [ssq2,ssq3]
#------------------------------------------------------------------------------------------
def four_points(atoms):
    ####ctd: the molecular centroid
    ####cst: The closest atom to the molecular centroid (ctd)
    ####fct: The farthest atom from the molecular centroid (ctd)
    ####ftf: The farthest atom from the fct
    vecpos=[np.array(position) for position in atoms.get_positions()]
    ctd=centroid(atoms)
    r=[[np.linalg.norm(xyz - ctd), xyz] for xyz in vecpos]
    r.sort(key=lambda x: x[0])
    cst=r[0][1]
    fct=r[-1][1]
    s=[[np.linalg.norm(xyz - fct), xyz] for xyz in vecpos]
    s.sort(key=lambda x: x[0])
    ftf=s[-1][1]
    return ctd, cst, fct, ftf
#------------------------------------------------------------------------------------------
def USRMonoatom(moleculein):
    ctd,   cst,  fct,  ftf=four_points(moleculein)
    lctd, lcst, lfct, lftf= [], [], [], []
    for iatom in moleculein:
        xyz=np.array(iatom.position)
        ictd1=np.linalg.norm(xyz-ctd)
        icst1=np.linalg.norm(xyz-cst)
        ifct1=np.linalg.norm(xyz-fct)
        iftf1=np.linalg.norm(xyz-ftf)
        lctd.append(ictd1)
        lcst.append(icst1)
        lfct.append(ifct1)
        lftf.append(iftf1)
    a1=lastwo_central_moment(lctd)
    a2=lastwo_central_moment(lcst)
    a3=lastwo_central_moment(lfct)
    a4=lastwo_central_moment(lftf)
    standard_USR=a1+a2+a3+a4
    return standard_USR
#------------------------------------------------------------------------------------------
def USRMultiatom(moleculein):
    listm=moleculein.get_masses()
    mavg = np.mean(listm)
    ctd, cst, fct, ftf=four_points(moleculein)
    lctd,  lcst,  lfct,  lftf = [], [], [], []
    lctdm, lcstm, lfctm, lftfm = [], [], [], []
    for iatom in moleculein:
        xyz=np.array(iatom.position)
        ictd1=np.linalg.norm(xyz-ctd)
        icst1=np.linalg.norm(xyz-cst)
        ifct1=np.linalg.norm(xyz-fct)
        iftf1=np.linalg.norm(xyz-ftf)
        lctd.append(ictd1)
        lcst.append(icst1)
        lfct.append(ifct1)
        lftf.append(iftf1)
        mi=atomic_masses[iatom.number]
        ictdm1=ictd1*mi/mavg
        icstm1=icst1*mi/mavg
        ifctm1=ifct1*mi/mavg
        iftfm1=iftf1*mi/mavg
        lctdm.append(ictdm1)
        lcstm.append(icstm1)
        lfctm.append(ifctm1)
        lftfm.append(iftfm1)
    a1=lastwo_central_moment(lctd)
    a2=lastwo_central_moment(lcst)
    a3=lastwo_central_moment(lfct)
    a4=lastwo_central_moment(lftf)
    b1=lastwo_central_moment(lctdm)
    b2=lastwo_central_moment(lcstm)
    b3=lastwo_central_moment(lfctm)
    b4=lastwo_central_moment(lftfm)
    standard_USR=a1+a2+a3+a4
    m_weight_USR=b1+b2+b3+b4
    extra_descriptor_USR=standard_USR+m_weight_USR
    return extra_descriptor_USR
#------------------------------------------------------------------------------------------
def similarity(imol, jmol, mono=False):
    #elementosi = set(imol.get_chemical_symbols())
    #elementosj = set(jmol.get_chemical_symbols())
    #if elementosi != elementosj: return 0
    #mono=True if len(elementosi)==1 else False
    if mono:
        n_features=8
        vi=USRMonoatom(imol)
        vj=USRMonoatom(jmol)
    else:
        n_features=16
        vi=USRMultiatom(imol)
        vj=USRMultiatom(jmol)
    manhattan_distance=sum([np.absolute(a-b) for a,b in zip(vi,vj)])
    sij=1.0/(1.0+manhattan_distance/float(n_features))
    return sij
#------------------------------------------------------------------------------------------
def find_similar_elements(listmol, similarity_matrix, tols=tolsij, tole=tolene):
    similar_elements_indices = []
    num_elements = similarity_matrix.shape[0]
    for i in range(num_elements):
        for j in range(i+1,num_elements):
            edf=np.abs(listmol[i].info['e'] - listmol[j].info['e'])
            if (similarity_matrix[i, j] >= tols) and (edf <= tole):
                similar_elements_indices.append(j)
    return similar_elements_indices
#------------------------------------------------------------------------------------------
def disc_USR(listmol, tols=tolsij, tole=tolene, mono=False):
    num_molecules = len(listmol)
    if mono:
        n_features=8
        descriptors=[USRMonoatom(imol) for imol in listmol]
    else:
        n_features=16
        descriptors=[USRMultiatom(imol) for imol in listmol]
    #similar_elements_indices = []
    similarity_matrix = np.zeros((num_molecules, num_molecules))
    for i in range(num_molecules):
        vi=descriptors[i]
        for j in range(i, num_molecules):
            vj=descriptors[j]
            manhattan_distance=sum([np.absolute(a-b) for a,b in zip(vi,vj)])
            similarity=1.0/(1.0+manhattan_distance/float(n_features))
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity
    similar_elements_indices=find_similar_elements(listmol, similarity_matrix, tols, tole)
    similar_elements_indices.sort()
    disimilars_atoms=[listmol[i] for i in range(num_molecules) if i not in similar_elements_indices]
    return disimilars_atoms
#------------------------------------------------------------------------------------------
def comparator_usr_serial(atoms0, tols=tolsij, tole=tolene, mono=False):
    start = time.time()
    ni=len(atoms0)
    atoms1=disc_USR(atoms0, tols, tole, mono)
    nf=len(atoms1)
    end = time.time()
    print('USR comparison (-serial-) at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return atoms1
#------------------------------------------------------------------------------------------
def make_comparator_usr(ifolder, tols=tolsij, tole=tolene, mono=False):
    atoms0=readxyzs(ifolder+'/'+ifolder+'.xyz')
    atoms1=disc_USR(atoms0, tols, tole, mono)
    writexyzs(atoms1,ifolder+'/'+ifolder+'_disc.xyz')
#------------------------------------------------------------------------------------------
def comparator_usr_parallel(poscarlist, nproc, base_name, tols=tolsij, tole=tolene, mono=False):
    poscarlist=sort_by_energy(poscarlist, 1)
    ni=len(poscarlist)
    if ni < 4*nproc:
        moleculeout=comparator_usr_serial(poscarlist, tols, tole, mono)
        moleculeout=sort_by_energy(moleculeout, 1)
        return moleculeout
    start = time.time()
    folderlist=prepare_folders(poscarlist, nproc, base_name)
    poscar_split_list=split_poscarlist(poscarlist, nproc)
    procs = []
    dicc_term = {iposcar.info['i']: iposcar.info['c'] for iposcar in poscarlist}
    for ifolder, iposcars in zip(folderlist, poscar_split_list):
        writexyzs(iposcars, ifolder+'/'+ifolder+'.xyz')
        proc = Process(target=make_comparator_usr, args=(ifolder, tols, tole, mono))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    center_mols, border_mols = [], []
    for ifolder in folderlist:
        molx=readxyzs(ifolder+'/'+ifolder+'_disc.xyz')
        for imol in molx: imol.info['c']=dicc_term[imol.info['i']]
        molx=sort_by_energy(molx, 1)
        emin=molx[0].info['e']
        emax=molx[-1].info['e']
        for imol in molx:
            delw=imol.info['e'] - emin
            deup=emax - imol.info['e']
            if ( delw < tole ) or ( deup < tole ):
                border_mols.extend([imol])
            else:
                center_mols.extend([imol])
    border_mols=disc_USR(border_mols, tols, tole, mono)
    moleculeout=center_mols+border_mols
    moleculeout=sort_by_energy(moleculeout, 1)
    os.system('rm -rf %sproc[0-9][0-9][0-9]' %(base_name))
    nf=len(moleculeout)
    end = time.time()
    print('USR comparison (parallel) at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return moleculeout
#------------------------------------------------------------------------------------------
def make_similarity_matrix_compare(moleculein, moleculeref, mono=False):
    if mono:
        n_features=8
        descriptors1=[USRMonoatom(imol) for imol in moleculein]
        descriptors2=[USRMonoatom(imol) for imol in moleculeref]
    else:
        n_features=16
        descriptors1=[USRMultiatom(imol) for imol in moleculein]
        descriptors2=[USRMultiatom(imol) for imol in moleculeref]
    total_molecules1=len(moleculein)
    total_molecules2=len(moleculeref)
    similarity_matrix=np.zeros(shape=(total_molecules1, total_molecules2),dtype=float)
    for i in range(total_molecules1):
        vi=descriptors1[i]
        for j in range(total_molecules2):
            vj=descriptors2[j]
            manhattan_distance=sum([np.absolute(a-b) for a,b in zip(vi,vj)])
            similarity=1.0/(1.0+manhattan_distance/float(n_features))
            similarity_matrix[i, j] = similarity
    return similarity_matrix
#------------------------------------------------------------------------------------------
def molin_sim_molref(moleculein, moleculeref, tols=tolsij, tole=tolene, mono=False):
    start = time.time()
    ni=len(moleculein)
    matrixs=make_similarity_matrix_compare(moleculein, moleculeref, mono)
    similares=[]
    for i,imol in enumerate(moleculein):
        for j, jmol in enumerate(moleculeref):
            sij=matrixs[i][j]
            edf=np.abs(imol.info['e']-jmol.info['e'])
            if (sij >= tols) and (edf <= tole):
                similares.append(i)
                break
    moleculeout=[imol for i, imol in enumerate(moleculein) if i not in similares] 
    nf=len(moleculeout)
    end = time.time()
    print('USR comparison (-serial-) at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return moleculeout
#------------------------------------------------------------------------------------------
