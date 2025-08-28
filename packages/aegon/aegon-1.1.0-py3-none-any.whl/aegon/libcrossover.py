import random
import numpy as np
from ase import Atom, Atoms
from aegon.libutils import rand_unit_vector, rotate_random, distance_atoms2atoms, rotate_vector_angle_deg
#------------------------------------------------------------------------------------------
""" CUT IN THE Z AXIS """
def get_gen(atoms):
    ene=float(0.0)
    list_up, list_dn = [], []
    children_up=Atoms()
    children_dn=Atoms()
    for ii, iatom in enumerate(atoms):
        if iatom.position[2] >= 0.0:
            children_up.append(iatom)
            list_up.append(ii)
        else:
            children_dn.append(iatom)
            list_dn.append(ii)
    children_up.info['c']=list_up
    children_dn.info['c']=list_dn
    return children_up, children_dn
#------------------------------------------------------------------------------------------
def randvector(r):
    ru=float(random.uniform(0.0, r))
    vector = ru*rand_unit_vector()
    return vector
#------------------------------------------------------------------------------------------
def molecule_from_list(moleculein, n):
    if not isinstance(n, list): n = [n]
    moleculeout = Atoms()
    for i in n: moleculeout.append(moleculein[i])
    return moleculeout
#------------------------------------------------------------------------------------------
def up_part_from_n(father1, nff, deltadisp):
    fall=True
    contador=0
    while fall:
        father2=father1.copy()
        rv=randvector(deltadisp)
        father2.translate(-rv)
        rotate_random(father2)
        fup, fdn=get_gen(father2)
        fup_cs=fup.get_chemical_symbols()
        fdn_cs=fdn.get_chemical_symbols()
        if len(fup_cs)==nff:
            fall=False
            return fup, fdn
        elif len(fdn_cs)==nff:
            fall=False
            positions = fup.get_positions()
            positions[:, 2] *= -1
            fup.set_positions(positions)
            positions = fdn.get_positions()
            positions[:, 2] *= -1
            fdn.set_positions(positions)
            return fdn, fup
        else:
            contador=contador+1
            if contador==5000:
                return False
#------------------------------------------------------------------------------------------
def dn_part_from_zlist(mother1, list_chemical_symbols, deltadisp):
    fall=True
    contador=0
    while fall:
        mother2=mother1.copy()
        rv=randvector(deltadisp)
        mother2.translate(-rv)
        rotate_random(mother2)
        mup, mdn=get_gen(mother2)
        mdn_cs=mdn.get_chemical_symbols()
        mup_cs=mup.get_chemical_symbols()
        if (mdn_cs==list_chemical_symbols):
            fall=False
            return mup, mdn
        elif (mup_cs==list_chemical_symbols):
            fall=False
            positions = mup.get_positions()
            positions[:, 2] *= -1
            mup.set_positions(positions)
            positions = mdn.get_positions()
            positions[:, 2] *= -1
            mdn.set_positions(positions)
            return mdn, mup
        else:
            contador=contador+1
            if contador==5000:
                return False
#------------------------------------------------------------------------------------------
def mol_min_radius(atoms):
    moleculeout=atoms.copy()
    moleculeout.translate(-moleculeout.get_center_of_mass())
    positions = atoms.get_positions()
    distances = np.linalg.norm(positions, axis=1)
    distances.sort()
    rmin=distances[0]*float(0.6)
    return rmin
#------------------------------------------------------------------------------------------
def complement(tot, part):
    ans=tot.copy()
    for elemi in part:
      if elemi in ans: ans.remove(elemi)
    return(ans)
#------------------------------------------------------------------------------------------
def cut_deavenho(singlefather, singlemother, atomlist):
    father1=singlefather.copy()
    mother1=singlemother.copy()
    father1.translate(-father1.get_center_of_mass())
    mother1.translate(-mother1.get_center_of_mass())
    rminf=mol_min_radius(father1)
    rminm=mol_min_radius(mother1)
    n0=len(atomlist)//2
    for ii, nff in enumerate([n0, n0-1, n0+1]):
        ans1=up_part_from_n(father1, nff, rminf)
        if (ans1 is False):
            return False
        fup, fdn  = ans1
        acfzlist=fup.get_chemical_symbols()
        rsdzlist=complement(atomlist, acfzlist)
        ans2=dn_part_from_zlist(mother1, rsdzlist, rminm)
        if (ans2 is False):
            if (ii == 2):
                return False
            else:
                continue
        else:
            mup, mdn = ans2
            break
    moleculeout=[fup, mdn]
    return moleculeout
#------------------------------------------------------------------------------------------
def crossover_deavenho(singlefather, singlemother, atomlist):
    moleculelist=Atoms()
    father=singlefather.copy()
    mother=singlemother.copy()
    result=cut_deavenho(singlefather, singlemother, atomlist)
    if not result:
        result=cut_deavenho(singlemother, singlefather, atomlist)
    if not result:
        return False
    else:
        gena,genb=result
        ratio_radii_crit=0.90
        var=gena.copy()
        moleculelist=[var+genb]
        dmin=distance_atoms2atoms(var, genb)
        test = False if (dmin < ratio_radii_crit) else True
        angle=0
        zeta=[0.0,0.0,1.0]
        vz=np.array([float(0.0), float(0.0), float(0.05)])
        while test == False:
            angle=angle+10
            var=rotate_vector_angle_deg(gena, zeta, angle)
            moleculelist.append(var+genb)
            dmin=distance_atoms2atoms(var, genb)
            if (dmin >= ratio_radii_crit):
                #writexyzs(moleculelist,'fenomeno.xyz')
                test=True
            if (angle >=360):
                angle=0
                gena.translate(-vz)
        moleculeout=moleculelist[-1]
        return moleculeout
#------------------------------------------------------------------------------------------

