from joblib import Parallel, delayed
import numpy as np
from dscribe.descriptors import CoulombMatrix,  ACSF, SOAP, MBTR, LMBTR
from libdiscusr import USRMonoatom#, USRMultiatom
#------------------------------------------------------------------------------
def descriptors_MBTR_dis(lista):
    des_list = []
    for imol in lista:
        atoms = imol.get_chemical_symbols()
        especies = set(atoms)
        mbtr = MBTR(
            species=especies,
            geometry={"function": "distance"},
            grid={"min": 0, "max": 15, "sigma": 0.075, "n": 500},
            weighting={"function": "exp", "r_cut": 10, "threshold": 1e-3},
            periodic=False, sparse=False, normalization="l2"
        )
        des = mbtr.create(imol)
        des_list.append(des)
    return des_list

def descriptors_MBTR_angle(lista):
    des_list = []
    for imol in lista:
        atoms = imol.get_chemical_symbols()
        especies = set(atoms)
        mbtr = MBTR(
            species=especies,
            geometry={"function": "angle"},
            grid={"min": 0, "max": 180, "sigma": 1, "n": 360},
            weighting={"function": "exp", "r_cut": 10, "threshold": 1e-3},
            periodic=False, sparse=False, normalization="l2"
        )
        des = mbtr.create(imol)
        des_list.append(des)
    return des_list

def descriptors_MBTR_inv_dis (lista):
    des_list = []
    for  imol in lista:
        atoms = imol.get_chemical_symbols()
        especies = set(atoms)
        mbtr = MBTR(species = especies, geometry={"function": "inverse_distance"},
                    grid = {"min": 0, "max": 1, "sigma": 0.005, "n": 500}, 
                    weighting={"function": "exp", "r_cut": 10, "threshold": 1e-3}, #weighting={"function": "inverse_square", "r_cut": 10},
                    periodic=False, sparse=False, normalization="l2")
        des = mbtr.create(imol)
        des_list.append(des)
    return des_list

def descriptors_MBTR_cos (lista):
    des_list = []
    for  imol in lista:
        atoms = imol.get_chemical_symbols()
        especies = set(atoms)
        mbtr = MBTR(species = especies, geometry={"function": "cosine"},
                    grid = {"min": -1.0, "max": 1.0, "sigma": 0.01, "n": 300}, 
                    weighting={"function": "exp", "r_cut": 10, "threshold": 1e-3}, #weighting={"function": "inverse_square", "r_cut": 10},
                    periodic=False, sparse=False, normalization="l2")
        des = mbtr.create(imol)
        des_list.append(des)
    return des_list

def descriptors_LMBTR (lista):
    des_list = []
    for imol in lista:
         geometria={"function": "distance"}
         grid={"min": 0, "max": 5, "n": 100, "sigma": 0.1}
         pesaje={"function": "exp", "scale": 0.5, "threshold": 1e-3}
         atoms = imol.get_chemical_symbols()
         especies = set(atoms)
         lmbtr = LMBTR(species = especies, geometry=geometria, grid=grid, weighting=pesaje, periodic=False, normalization="l2")
         lmbtr_des = lmbtr.create(imol)
         des = lmbtr_des.flatten()
         des_list.append(des)
    return des_list

def descriptors_SOAP (lista):
    des_list = []
    for imol in lista:
        atoms = imol.get_chemical_symbols()
        especies = set(atoms)
        r_cut = 6.0
        n_max = 8
        l_max = 6
        soap = SOAP(species = especies, periodic=False, r_cut = r_cut, n_max=n_max, l_max=l_max)
        soap_des = soap.create(imol)
        des = soap_des.flatten()
        des_list.append(des)
    return des_list

def descriptors_CoulombMatrix (lista):
    des_list = []
    for imol in lista:
        filas = len(imol)
        cm = CoulombMatrix(n_atoms_max = filas)
        des = cm.create(imol)
        des_list.append(des)
    return des_list

def descriptors_ACSF (lista):
    des_list = []
    for imol in lista:
         g2params=[[1, 1], [1, 2], [1, 3]]
         g4params=[[1, 1, 1], [1, 2, 1], [1, 1, -1], [1, 2, -1]]
         atoms = imol.get_chemical_symbols()
         especies = set(atoms)
         r_cut = 3.5
         acsf = ACSF(species = especies, r_cut = r_cut, g2_params=g2params, g4_params=g4params)
         acsf_des = acsf.create(imol)
         des = acsf_des.flatten()
         des_list.append(des)
    return des_list

def descriptors_USR_mono (lista):
    des_list = []
    for imol in lista:
        des = USRMonoatom(imol)
        des_list.append(des)
    return des_list

#def descriptors_USR_multi(lista):
#    des_list = []
#    for imol in lista:
#        des = USRMultiatom(imol)
#        des_list.append(des)
#    return des_list
#-------------------------------------------------------------------------------

def split_list(lista, chunk_size):
    return [lista[i:i + chunk_size] for i in range(0, len(lista), chunk_size)]

def descriptors_sel(lista, des, chunk_size=500, n_jobs=-1):
    descriptor_functions = { "MBTR_dis": descriptors_MBTR_dis, "MBTR_ang": descriptors_MBTR_angle,
                             "MBTR_inv_dis": descriptors_MBTR_inv_dis, "MBTR_cos": descriptors_MBTR_cos,
                             "USR_mono": descriptors_USR_mono, #"USR_multi": descriptors_USR_multi,
                             "LMBTR": descriptors_LMBTR, "SOAP": descriptors_SOAP,
                             "CoulombMatrix": descriptors_CoulombMatrix, "ACSF": descriptors_ACSF}
    
    des_fun = descriptor_functions[des]
    sublistas = split_list(lista, chunk_size)
    resultados = Parallel(n_jobs=n_jobs)(delayed(des_fun)(sublista) for sublista in sublistas)
    descriptores = [descriptor for sublista in resultados for descriptor in sublista]
    return descriptores

def descriptors_comb(lista, des_1, des_2, chunk_size=500, n_jobs=-1): 
    des_list1 = descriptors_sel(lista, des_1, chunk_size, n_jobs)
    des_list2 = descriptors_sel(lista, des_2, chunk_size, n_jobs)
    combined = [np.concatenate((d1, d2)) for d1, d2 in zip(des_list1, des_list2)]
    return combined
