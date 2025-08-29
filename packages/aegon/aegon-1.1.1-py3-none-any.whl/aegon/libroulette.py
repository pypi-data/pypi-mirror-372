import random
import numpy as np
from aegon.libutils import sort_by_energy
#-------------------------------------------------------------------------------
def get_fitness(moleculelist):
    if len(moleculelist)==1:
       fitness=[float(1.0)]
    else:
       fitness=[]
       listmolecule=sort_by_energy(moleculelist,1)
       Emin=listmolecule[0].info['e']
       Emax=listmolecule[-1].info['e']
       for imol in listmolecule:
           Ei=imol.info['e']
           EFEi=(Ei-Emin)/(Emax-Emin)
           fi=0.5*(1.0-np.tanh(((2.0*EFEi)-1.0)))
           fitness.append(float(fi))
    return fitness
#-------------------------------------------------------------------------------
def get_roulette_wheel_selection(moleculelist, nmating):
    listmolecule=sort_by_energy(moleculelist,1)
    fitness=get_fitness(listmolecule)
    sum_of_fitness=sum(fitness)
    previous_probability=0.0
    n=len(listmolecule)
    pp=[]
    for ix in range(n):
        previous_probability= previous_probability+ (fitness[ix]/sum_of_fitness)
        if ix==n-1: pp.append(1.0)
        else: pp.append(previous_probability)
    roulette = []
    for i in range(nmating):
        random_number = random.random()
        for ii, p in enumerate(pp):
            if random_number <= p:
                roulette.append(listmolecule[ii])
                break
    return roulette
#-------------------------------------------------------------------------------
