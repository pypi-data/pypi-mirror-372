import time
import numpy as np
from aegon.libdescriptors import descriptors_sel, descriptors_comb
from aegon.libclustering import clustering_agg, clustering_hdbscan, clustering_kmeans
from aegon.libutils import sort_by_energy
#----------------Energias promedio---------------------------------------------
def selectbyclustering_uni_prom(mol_in, selection_count = [10, 8, 6, 4, 2], descriptor_type="MBTR_dis_2"):
    start = time.time()
    nn=len (mol_in)
    ni=sum(selection_count)
    if nn <= ni:
        return mol_in
    n_count= len (selection_count)
    des = descriptors_sel(mol_in, descriptor_type)    
    clus = clustering_agg(mol_in, des, n_count)    
    ord_clus = ordenar_diccionario_por_energia_promedio(clus)
    lista_est = min_de_cada_clus_con_select_count(ord_clus, selection_count)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out

def selectbyclustering_des_comb_prom(mol_in, selection_count = [10, 8, 6, 4, 2], descriptor_type_1 = "MBTR_dis_2", descriptor_type_2 = "MBTR_arg_2"):
    start = time.time()
    nn=len (mol_in)
    ni=sum(selection_count)
    if nn <= ni:
        return mol_in
    n_count= len (selection_count)
    des = descriptors_comb(mol_in, descriptor_type_1, descriptor_type_2)
    clus = clustering_agg(mol_in, des, n_count)
    ord_clus = ordenar_diccionario_por_energia_promedio(clus)
    lista_est = min_de_cada_clus_con_select_count(ord_clus, selection_count)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out
#---------------------------------por enegia del individuo de menor enegia--------------
def selectbyclustering_uni(mol_in, selection_count = [10, 8, 6, 4, 2], descriptor_type="MBTR_dis_2"):
    start = time.time()
    nn=len (mol_in)
    ni=sum(selection_count)
    if nn <= ni:
        return mol_in
    n_count= len (selection_count)
    des = descriptors_sel(mol_in, descriptor_type)    
    clus = clustering_agg(mol_in, des, n_count)    
    ord_clus = ordenar_diccionario_por_minima_energia(clus)
    lista_est = min_de_cada_clus_con_select_count(ord_clus, selection_count)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out

def selectbyclustering_des_comb(mol_in, selection_count = [10, 8, 6, 4, 2], descriptor_type_1 = "MBTR_dis", descriptor_type_2 = "MBTR_ang"):
    start = time.time()
    nn=len (mol_in)
    ni=sum(selection_count)
    if nn <= ni:
        return mol_in
    n_count= len (selection_count)
    des = descriptors_comb(mol_in, descriptor_type_1, descriptor_type_2)
    clus = clustering_agg(mol_in, des, n_count)
    ord_clus = ordenar_diccionario_por_minima_energia(clus)
    lista_est = min_de_cada_clus_con_select_count(ord_clus, selection_count)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out
#-------------------------HDBSCAN-------------------------------------------------------
def selectbyclustering_uni_hdbscan(mol_in, n_seed = 45, descriptor_type = "MBTR_dis_2"):
    start = time.time()
    nn=len (mol_in)
    if nn <= 100:
        return mol_in
    des = descriptors_sel(mol_in, descriptor_type)
    clus, n_clus =  clustering_hdbscan(mol_in, des)
    lista_est, g_fit, selection_counts = select_individuals(clus, n_seed)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out

def selectbyclustering_comb_hdbscan(mol_in, n_seed  = 45,  descriptor_type_1 = "MBTR_dis_2", descriptor_type_2 = "MBTR_arg_2"):
    start = time.time()
    nn=len (mol_in)
    if nn <= 100:
        return mol_in
    des = descriptors_comb(mol_in, descriptor_type_1, descriptor_type_2)
    clus, n_clus =  clustering_hdbscan(mol_in, des)
    lista_est, g_fit, selection_counts = select_individuals(clus, n_seed)
    mol_out = sort_by_energy(lista_est, 1)
    nf=len(mol_out)
    end = time.time()
    print('Clustering selection (serial) at %5.2f s [%d -> %d]' %(end - start, nn, nf))
    return mol_out
#------------------------Manejo de diccionarios--------------------------------
def ordenar_diccionario_por_energia_promedio(diccionario):
    lista_claves_energias = []
    for clave, ilistmol in diccionario.items():
        if isinstance(ilistmol, list):
            energia_total = sum(mol.info['e'] for mol in ilistmol)
            energia_media = energia_total / len(ilistmol) if ilistmol else float('inf')
            lista_claves_energias.append((clave, energia_media))
        else:
            print(f"Advertencia: {clave} no es una lista.")
    lista_claves_energias.sort(key=lambda x: x[1])
    diccionario_ordenado = {clave: diccionario[clave] for clave, _ in lista_claves_energias}
    return diccionario_ordenado

def ordenar_diccionario_por_minima_energia(diccionario):
    lista_claves_energias = []
    for clave, ilistmol in diccionario.items():
        if isinstance(ilistmol, list):
            energias = [mol.info['e'] for mol in ilistmol if 'e' in mol.info]
            energia_minima = min(energias) if energias else float('inf')
            lista_claves_energias.append((clave, energia_minima))
        else:
            print(f"Advertencia: {clave} no es una lista y será ignorado.")

    lista_claves_energias.sort(key=lambda x: x[1])
    diccionario_ordenado = {clave: diccionario[clave] for clave, _ in lista_claves_energias}
    return diccionario_ordenado
#------------------------ selection counts-------------------------------------
def min_de_cada_clus (diccionario):
    nueva_lista= []
    recorrer_dic_and_take_min(diccionario, nueva_lista)
    return nueva_lista

def min_de_cada_clus_con_select_count(diccionario,selection_count):
    nueva_lista= []
    recorrer_dic_and_take_min_con_select_count(diccionario, nueva_lista, selection_count)
    return nueva_lista

def recorrer_dic_and_take_min (diccionario, nueva_lista):
    for clave,valor in diccionario.items():
        if isinstance(valor, dict):
            recorrer_dic_and_take_min(valor, nueva_lista)
        elif isinstance( valor, list):
            list_ord = sort_by_energy(valor,1)
            nueva_lista.append(list_ord[0])

def recorrer_dic_and_take_min_con_select_count(diccionario, nueva_lista, selection_count):
    indice = 0  # Empezamos con el primer valor de la lista de cantidades
    for clave, valor in diccionario.items():
        if isinstance(valor, dict):
            recorrer_dic_and_take_min(valor, nueva_lista, selection_count)
        elif isinstance(valor, list):
            list_ord = sort_by_energy(valor, 1)
            count = selection_count[indice] if indice < len(selection_count) else 1
            nueva_lista.extend(list_ord[:count])
            indice += 1

def clust_ite(diccionario, descriptor_func, selection_count):
    nue_dic = {}
    listas = list(diccionario.values())
    for idx, (lista, n_clusters) in enumerate(zip(listas, selection_count)):
        #print(f"Procesando lista {idx + 1} con n_clusters={n_clusters}...")
        if len(lista) > 1 and len(lista) >= n_clusters:
           des = descriptor_func(lista)
           clus = clustering_agg(lista, des, n_clusters)
           nue_dic[idx] = clus
        else:
            nue_dic[idx] = {0: lista}
    return nue_dic
#----------------------------selection HDBSCAN---------------------------------
def compute_group_fitness(diccionario):
    group_avg_energies = {}
    for key, molecules in diccionario.items():
        if molecules:
            energies = [mol.info['e'] for mol in molecules]
            group_avg_energies[key] = sum(energies) / len(energies)
        else:
            group_avg_energies[key] = float('inf')

    E_min = min(group_avg_energies.values())
    E_max = max(group_avg_energies.values())

    group_fitness = {}
    for key, avgE in group_avg_energies.items():
        if E_max == E_min:
            fitness = 1.0
        else:
            normalized = (avgE - E_min) / (E_max - E_min)
            fitness = 0.5 * (1.0 - np.tanh((2.0 * normalized) - 1.0))
        group_fitness[key] = fitness
    return group_fitness

def selection_counts_from_fitness(group_fitness, total_individuals):
    total_fitness = sum(group_fitness.values())
    raw_counts = {key: (total_individuals * (fit / total_fitness)) if total_fitness != 0 else 0
                  for key, fit in group_fitness.items()}
    
    selection_counts = {key: int(np.floor(count)) for key, count in raw_counts.items()}
    allocated = sum(selection_counts.values())
    remainder = total_individuals - allocated

    sorted_keys = sorted(raw_counts, key=lambda k: raw_counts[k] - selection_counts[k], reverse=True)
    for key in sorted_keys:
        if remainder <= 0:
            break
        selection_counts[key] += 1
        remainder -= 1

    return selection_counts

def select_individuals(diccionario, total_individuals):
    group_fitness = compute_group_fitness(diccionario)
    selection_counts = selection_counts_from_fitness(group_fitness, total_individuals)

    nueva_lista = []
    for key, molecules in diccionario.items():
        sorted_molecules = sort_by_energy(molecules, 1)
        count = selection_counts.get(key, 1)
        nueva_lista.extend(sorted_molecules[:count])

    return nueva_lista, group_fitness, selection_counts



    
