import random
import numpy as np
from ase import Atom, Atoms
from ase.data import atomic_numbers, covalent_radii
from aegon.libutils import distance_atom2atoms, distance_interatom, connected_graph, scale_coords, distance_atoms2atoms, merge_atoms, rand_unit_vector
#------------------------------------------------------------------------------------------
ratio_radii_min =0.95
ratio_radii_max =1.15
pvalue=float(ratio_radii_min+ratio_radii_max)/2.0
cte=(4.0*np.pi*np.sqrt(2.0))
reactivelist=['H', 'Li']
#------------------------------------------------------------------------------------------
def min_step(inatoms):
    min_covalent_radii=min([covalent_radii[atomic_numbers[si]] for si in inatoms])
    return min_covalent_radii
#------------------------------------------------------------------------------------------
def make_molecule_3Da(inatoms):
    atom_step=min_step(inatoms)
    onion_radii_factor=float(0.5)
    radius_of_container=float(0.5+(((len(inatoms)*3)/cte)**(1.0/3.0)))
    radius_of_container=onion_radii_factor*radius_of_container*float(1.1)
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    xi, yi, zi=random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)
    mm3da=Atoms(symbols=[si], positions=[(xi, yi, zi)])
    while atoms:
        random.shuffle(atoms)
        si=atoms.pop()
        inside, test=100, 0
        while inside > 0:
            RR=100.0
            while RR > radius_of_container: 
                xx=random.uniform(-radius_of_container, radius_of_container)
                yy=random.uniform(-radius_of_container, radius_of_container)
                zz=random.uniform(-radius_of_container, radius_of_container)
                RR=np.sqrt((xx*xx)+(yy*yy)+(zz*zz))
            tryatom=Atom(symbol=si, position=(xx, yy, zz))
            dmin=distance_atom2atoms(tryatom,mm3da)
            if (dmin >= ratio_radii_min) and (dmin <= ratio_radii_max):
                inside=0
                mm3da.append(tryatom)
            if test > 5000:
                radius_of_container=radius_of_container + atom_step
                test=0
            test+=1
    mm3da.info['e'] = 0.0
    mm3da.info['i'] = 'make_molecule_3Da'
    return mm3da
#------------------------------------------------------------------------------------------
def make_molecule_3Db(inatoms):
    atom_step=min_step(inatoms)
    onion_radii_factor=float(1.5)
    radius_of_container=float(0.5+(((len(inatoms)*3)/cte)**(1.0/3.0)))
    radius_of_container=onion_radii_factor*radius_of_container*float(1.1)
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    xi, yi, zi=random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)
    mm3db=Atoms(symbols=[si], positions=[(xi, yi, zi)])
    while atoms:
        random.shuffle(atoms)
        si=atoms.pop() 
        inside, test=100, 0
        while inside > 0:
            RR=100.0
            while RR > radius_of_container: 
                xx=random.uniform(-radius_of_container, radius_of_container)
                yy=random.uniform(-radius_of_container, radius_of_container)
                zz=random.uniform(-radius_of_container, radius_of_container)
                RR=np.sqrt((xx*xx)+(yy*yy)+(zz*zz))
            tryatom=Atom(symbol=si, position=(xx, yy, zz))
            dmin=distance_atom2atoms(tryatom, mm3db)
            if (dmin >= ratio_radii_min) and (dmin <= ratio_radii_max):
                inside=0
                mm3db.append(tryatom)
            if test > 8000:
                radius_of_container=radius_of_container + atom_step
                test=0
            test+=1
    mm3db.info['e'] = 0.0
    mm3db.info['i'] = 'make_molecule_3Db'
    return mm3db
#------------------------------------------------------------------------------------------
def make_molecule_2Da(inatoms):
    atom_step=min_step(inatoms)
    onion_radii_factor=float(1.25)
    radius_of_container=float(0.5+(((len(inatoms)*3)/cte)**(1.0/3.0)))
    radius_of_container= onion_radii_factor*radius_of_container*float(1.2)
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    xi, yi, zi=random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25), 0.0
    mm2da=Atoms(symbols=[si], positions=[(xi, yi, zi)])
    while atoms:
        random.shuffle(atoms)
        si=atoms.pop() 
        inside, test=100, 0
        while inside > 0:
            RR=100.0
            while RR > radius_of_container: 
                xx=random.uniform(-radius_of_container, radius_of_container)
                yy=random.uniform(-radius_of_container, radius_of_container)
                RR=np.sqrt((xx*xx)+(yy*yy))
            tryatom=Atom(symbol=si, position=(xx, yy, 0.0))
            dmin=distance_atom2atoms(tryatom, mm2da)
            if (dmin >= ratio_radii_min) and (dmin <= ratio_radii_max):
                inside=0
                mm2da.append(tryatom)
            if test > 7000:
                radius_of_container=radius_of_container + atom_step
                test=0
            test+=1
    mm2da.info['e'] = 0.0
    mm2da.info['i'] = 'make_molecule_2Da'
    return mm2da
#------------------------------------------------------------------------------------------
def make_molecule_sphere(inatoms):
    atom_step=min_step(inatoms)
    onion_radii_factor=float(0.70)
    radius_of_container=float(0.5+(((len(inatoms)*3)/cte)**(1.0/3.0)))
    radius_of_container=onion_radii_factor*radius_of_container*float(1.2)
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    phi=float(random.uniform(0.0, 2*np.pi))
    costheta=float(random.uniform(-1.0, 1.0))
    theta = np.arccos(costheta)
    x = radius_of_container * np.sin(theta) * np.cos(phi)
    y = radius_of_container * np.sin(theta) * np.sin(phi)
    z = radius_of_container * np.cos(theta)
    mmsp=Atoms(symbols=[si], positions=[(float(x), float(y), float(z))])    
    while atoms:
        random.shuffle(atoms)
        si=atoms.pop() 
        inside, test=100, 0
        while inside > 0:
            phi=float(random.uniform(0.0, 2*np.pi))
            costheta=float(random.uniform(-1.0, 1.0))
            theta = np.arccos(costheta)
            xx = radius_of_container * np.sin(theta) * np.cos(phi)
            yy = radius_of_container * np.sin(theta) * np.sin(phi)
            zz = radius_of_container * np.cos(theta)
            tryatom=Atom(symbol=si, position=(float(xx), float(yy), float(zz)))
            dmin=distance_atom2atoms(tryatom, mmsp)
            if (dmin >= ratio_radii_min) and (dmin <= ratio_radii_max):
                inside=0
                mmsp.append(tryatom)
            if test > 5000:
                test=0
                radius_of_container=radius_of_container + atom_step
            test+=1
    mmsp.info['e'] = 0.0
    mmsp.info['i'] = 'make_molecule_sphere'
    return mmsp
#------------------------------------------------------------------------------------------
def make_molecule_wire(inatoms):
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    xxx=float(0.0)
    mm2da=Atoms(symbols=[si], positions=[(float(0.0), float(0.0), float(0.0))])
    last=[si]
    while atoms:
        random.shuffle(atoms)
        si=atoms.pop()
        a1=covalent_radii[atomic_numbers[last[-1]]]
        a2=covalent_radii[atomic_numbers[si]]
        xxx=float(a1+a2)*pvalue + xxx
        tryatom=Atom(symbol=si, position=(xxx, float(0.0), float(0.0)))
        mm2da.append(tryatom)
        last.append(si)
    mm2da.info['e'] = 0.0
    mm2da.info['i'] = 'make_molecule_wire'
    return mm2da
#------------------------------------------------------------------------------------------
def make_molecule_circle(inatoms):
    atoms=list(inatoms)
    random.shuffle(atoms)
    radiomax=sum([covalent_radii[atomic_numbers[ii]] for ii in atoms])/(np.pi)
    si=atoms.pop()
    mcircle=Atoms(symbols=[si], positions=[(radiomax, 0.0, 0.0)])
    last=[si]
    angle=0.0
    while atoms:
        si=atoms.pop()
        a1=covalent_radii[atomic_numbers[last[-1]]]        
        a2=covalent_radii[atomic_numbers[si]]
        S=a1+a2
        last.append(si)
        theta=S/radiomax
        angle=angle+theta
        xx=radiomax*np.cos(angle)
        yy=radiomax*np.sin(angle)
        ai=Atom(symbol=si, position=(float(xx), float(yy), 0.0))
        mcircle.append(ai)
    rmin=distance_interatom(mcircle)
    factor=(ratio_radii_min+ratio_radii_max)/(2.0*rmin)
    mcircle=scale_coords(mcircle, factor)
    mcircle.info['e'] = 0.0
    mcircle.info['i'] = 'make_molecule_circle'
    return mcircle
#------------------------------------------------------------------------------------------
def make_molecule_two_rings(inatoms):
    listsh=list(inatoms)
    random.shuffle(listsh)
    circ1=int(np.ceil(len(listsh)/2.0))
    atoms1=list(listsh[0:circ1])
    atoms2=list(listsh[(circ1):])
    circulo1=make_molecule_circle(atoms1)
    circulo2=make_molecule_circle(atoms2)
    zzz, inside=0.05, 100
    while inside > 50:
        tmp=circulo2.copy()
        vz=np.array([0.0, 0.0, zzz])
        tmp.translate(-vz)
        dmin=distance_atoms2atoms(tmp, circulo1)
        if (dmin > ratio_radii_min):
            inside=0
            two_rings=merge_atoms([circulo1,tmp])            
        else: zzz = zzz + 0.01
    two_rings.info['e'] = 0.0
    two_rings.info['i'] = 'make_molecule_two_rings'
    return two_rings
#------------------------------------------------------------------------------------------
def make_molecule_helix(inatoms):
    atoms0=list(inatoms)
    len0=len(atoms0)
    random.shuffle(atoms0)
    #----------------------------------
    circ1=random.randint(2, 6) if len0 > 6 else random.randint(1, len0)
    atoms1=list(atoms0[0:circ1])
    radiomax=sum([covalent_radii[atomic_numbers[ii]] for ii in atoms1])*pvalue/(np.pi)
    #----------------------------------
    ref0=covalent_radii[atomic_numbers[atoms0[0]]]
    refn=covalent_radii[atomic_numbers[atoms0[-1]]]
    avg=(ref0+refn)*pvalue/float(circ1)
    #----------------------------------
    t, angle=float(0.0), 0.0
    si=atoms0.pop()
    helix=Atoms(symbols=[si], positions=[(float(radiomax), 0.0, 0.0)])
    last=[si]
    while atoms0:
        si=atoms0.pop()
        a1=covalent_radii[atomic_numbers[last[-1]]]
        a2=covalent_radii[atomic_numbers[si]]    
        S=(a1+a2)*pvalue
        theta=S/radiomax
        angle=angle+theta
        xx=radiomax*np.cos(angle)
        yy=radiomax*np.sin(angle)
        t=t+float(avg)
        inside=100
        while inside > 50:
            ai=Atom(symbol=si, position=(float(xx), float(yy), t))
            dmin=distance_atom2atoms(ai, helix)
            if (dmin >= ratio_radii_min) or (dmin >= ratio_radii_max): inside=0
            else: t = t - float(0.01)
        helix.append(ai)
        last.append(si)
    helix.info['e'] = 0.0
    helix.info['i'] = 'make_molecule_helix'
    return helix
#------------------------------------------------------------------------------------------
def make_molecule_eye(inatoms):
    atom_step=min_step(inatoms)
    atoms=list(inatoms)
    random.shuffle(atoms)
    si=atoms.pop()
    meyes=make_molecule_circle(atoms)
    zzz, inside=float(0.0), 100
    while inside > 50:
        tryatom=Atom(symbol=si, position=(float(0.0), float(0.0), zzz))        
        dmin=distance_atom2atoms(tryatom, meyes)
        if (dmin >= ratio_radii_min):
            meyes.append(tryatom)
            inside=0
        else: zzz = zzz + atom_step
    meyes.info['e'] = 0.0
    meyes.info['i'] = 'make_molecule_eye'
    return meyes
#------------------------------------------------------------------------------------------
def single_random_molecule_without_h(inatoms):
    if len(inatoms)==1:
        atoms=list(inatoms)
        m1=Atoms(symbols=[atoms[0]], positions=[(float(0.0), float(0.0), float(0.0))])
    else:
        which=random.randrange(0, 18)
        if which in [0, 1, 2]:    m1=make_molecule_3Da(inatoms)
        if which in [3, 4, 5]:    m1=make_molecule_3Db(inatoms)
        if which in [6, 7, 8, 9]: m1=make_molecule_2Da(inatoms)
        if which in [10, 11, 12]: m1=make_molecule_sphere(inatoms)
        if which in [13, 14]:     m1=make_molecule_helix(inatoms)
        if which == 15:           m1=make_molecule_wire(inatoms)
        if which == 16:           m1=make_molecule_circle(inatoms)
        if which == 17:           m1=make_molecule_two_rings(inatoms)
        if which == 18:           m1=make_molecule_eye(inatoms)
    return m1
#------------------------------------------------------------------------------------------
def add_atomrand(atomsin, newatomlist, randomatomplacement = 0, rec=0):            
    numlockedatoms, count, index = 0, 0, 0
    vecr=rand_unit_vector()
    last_success, mismatch = 0, 0
    start = random.randrange(0, len(atomsin))
    while(numlockedatoms < len(newatomlist) and count< 100*len(newatomlist)):        
        count+=1
        if(randomatomplacement == 1):
            index = random.randrange(0, len(atomsin))
        else:
            index = (numlockedatoms+start+int((count-last_success)/10)+mismatch)%len(atomsin)
        mainvector=atomsin[index].position
        vec=rand_unit_vector()
        norma=(covalent_radii[atomsin[index].number]+covalent_radii[atomic_numbers[newatomlist[numlockedatoms]]])*pvalue
        vecr = mainvector + norma*vec
        tryatom = Atom(symbol=newatomlist[numlockedatoms], position=vecr)        
        dmin=distance_atom2atoms(tryatom, atomsin)
        if (dmin >= ratio_radii_min):            
            if(numlockedatoms == 0):
                newatoms=Atoms(symbols=[tryatom.symbol], positions=[tryatom.position])
                numlockedatoms+=1    
            else:
                dmin=distance_atom2atoms(tryatom, newatoms)
                if (dmin > ratio_radii_max):                
                    newatoms.append(tryatom)                    
                    mismatch+=int((count-last_success)/10)
                    last_success=count    
                    numlockedatoms+=1        
    if(numlockedatoms>0):
        atomsout = merge_atoms([atomsin, newatoms])
    else:
        atomsout = atomsin.copy()

    ### If the process is not completed after 100 * (number of atoms to add) attempts,
    #   the function "add_atomrand" is called recursively 10 times using the final Atoms object.
    #   If the process still fails, an intentional failure is triggered,
    #   and the process is terminated.

    if(numlockedatoms<len(newatomlist)):
        print("FALL ... tries: %s" %(count))
        if(rec<10):
            senderlist=[]
            for ii in range(numlockedatoms, len(newatomlist)):
                senderlist.append(newatomlist[ii])
            atomsout = add_atomrand(atomsout, senderlist, randomatomplacement, rec+1)
        else:
            mainvector=atomsin[0].position
            vec=rand_unit_vector()        
            norma=(covalent_radii[atomsin[index].number]+covalent_radii[atomic_numbers[newatomlist[numlockedatoms]]])*(ratio_radii_min-0.1)
            vecr = mainvector + norma*vec            
            tryatom = Atom(symbol=newatomlist[numlockedatoms], position=vecr)        
            newatoms.append(tryatom)        
            print("QUIT add_atomrand()")    
    return atomsout
#------------------------------------------------------------------------------------------
def single_random_molecule(inatoms):
    ticklish, skeleton =[], []
    for iatom in inatoms:
        if iatom in reactivelist: ticklish.append(iatom)
        else:                     skeleton.append(iatom)
    moleculeout=single_random_molecule_without_h(skeleton)
    if ticklish != []: moleculeout=add_atomrand(moleculeout, ticklish)
    return moleculeout
#------------------------------------------------------------------------------------------
def make_molecules_random(inatoms, cuantas, index=0):    
    m0, count=[], 0
    for ii in range(cuantas):
        m1=single_random_molecule(inatoms)
        rmin=distance_interatom(m1)
        if rmin >= ratio_radii_min:
            ans=connected_graph(m1, ratio_radii_max)
            if ans:
                count=count+1
                m0.extend([m1])
                if(len(m0) == cuantas): break             
    #print("Generando aleatoriamente %s de %s mol (proc: %s)" %(count, cuantas, index))   
    return m0
#------------------------------------------------------------------------------------------
