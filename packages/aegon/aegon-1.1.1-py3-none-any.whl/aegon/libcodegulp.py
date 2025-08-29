import os
import time
import numpy as np
from ase import Atoms
from multiprocessing import Process
from aegon.libutils import sort_by_energy, prepare_folders, split_poscarlist
#------------------------------------------------------------------------------------------
def make_ainput_gulp(headgulp, singleposcar, folder):
    iposname=singleposcar.info['i']
    nameinp=iposname+'.gin'
    nameout=iposname+'.got'
    if os.path.isfile(folder+nameout):
        print ("%s ... was not built because %s exists" %(folder+nameinp, folder+nameout))
    elif os.path.isfile(folder+nameinp):
        print ("%s .... was not built because it exists." %(nameinp))
    else:
        #print("Making input file = %s" %(folder+nameinp))
        fh=open(folder+nameinp,"w")
        for iline in headgulp:
            if iline=='LATTICEVECTORS':
                matrix=singleposcar.cell
                print("%12.9f %16.9f %16.9f" %(matrix[0,0],matrix[0,1],matrix[0,2]), file=fh)
                print("%12.9f %16.9f %16.9f" %(matrix[1,0],matrix[1,1],matrix[1,2]), file=fh)
                print("%12.9f %16.9f %16.9f" %(matrix[2,0],matrix[2,1],matrix[2,2]), file=fh)
            elif iline=='COORDINATES':
                symbols = singleposcar.get_chemical_symbols()
                direct_coordinates = singleposcar.get_scaled_positions()
                for symbol, coord in zip(symbols, direct_coordinates):
                    print("%-2s %16.9f %16.9f %16.9f" %(symbol,coord[0], coord[1], coord[2]), file=fh)
            else:
                print(iline, file=fh)
        fh.close()
#------------------------------------------------------------------------------------------
def make_the_sh_gulp(basename, poscarlist, gulp_path):
    filesh=basename+'.sh'
    if os.path.isfile(filesh):
        os.system("rm -f -v "+filesh)
    else:
    #if not os.path.isdir(basename):
        fh=open(filesh,'w')
        print("#!/bin/bash", file=fh)
        print("exe_gulp=%s" %(gulp_path), file=fh)
        print("cd %s" %(basename), file=fh)
        for iposcar in poscarlist:
            print("wait $PID ; $exe_gulp < %s.gin > %s.got" %(iposcar.info['i'],iposcar.info['i']), file=fh)
        print("cd ..", file=fh)
        print("exit 0", file=fh)
        fh.close()
#------------------------------------------------------------------------------------------
def get_termination_gulp(pathfilename):
    if os.path.isfile(pathfilename):
        file=open(pathfilename,'r')
        for line in file:
            if '**** Optimisation achieved ****' in line:
                normal = 1
                break
            else:
                normal = 0
        file.close()
        return normal
    else:
        return False
#------------------------------------------------------------------------------------------
def get_energy_gulp(pathfilename):
    file = open(pathfilename,'r')
    for line in file:
        if 'Final energy =' in line:
            ls = line.split()
            eneineV = float(ls[3])
        if 'Final enthalpy =' in line:
            ls = line.split()
            eneineV = float(ls[3])
    file.close()
    #eneinkcalpermol=eneineV*eVtokcalpermol
    #return eneinkcalpermol
    return eneineV
#------------------------------------------------------------------------------------------
def get_geometry_gulp(pathfilename):
    nt=get_termination_gulp(pathfilename)
    if nt==False: return False
    filename = os.path.basename(pathfilename)
    namein=filename.split('.')[0]
    matrix=np.array([])
    file = open(pathfilename,'r')
    ans=False
    ans1 = 'Final Cartesian lattice vectors (Angstroms) :'
    ans2 = 'Cartesian lattice vectors (Angstroms) :'
    for line in file:
        if (ans1 in line) or (ans2 in line):
            ans=True
            line=file.readline()
            line=file.readline()
            ls = line.split()
            a1x, a1y, a1z=float(ls[0]), float(ls[1]), float(ls[2])
            line=file.readline()
            ls = line.split()
            a2x, a2y, a2z=float(ls[0]), float(ls[1]), float(ls[2])
            line=file.readline()
            ls = line.split()
            a3x, a3y, a3z=float(ls[0]), float(ls[1]), float(ls[2])
            matrix=np.array([[a1x, a1y, a1z],[a2x, a2y, a2z],[a3x, a3y, a3z]])
    file.close()
    file=open(pathfilename,'r')
    direct_coordinates,symbols=[],[]
    for line in file:
        if 'Final fractional coordinates of atoms :' in line:
            for ii in range(5): line=file.readline()
            line=file.readline()
            ls = line.split()
            lenls=len(ls)
            while ( lenls == 7 ):
                si=str(ls[1])
                symbols.append(si)
                xd,yd,zd=float(ls[3]),float(ls[4]),float(ls[5])
                direct_coordinates.append([xd,yd,zd])
                line=file.readline()
                ls = line.split()
                lenls=len(ls)
    file.close()
    poscarx = Atoms(symbols=symbols, scaled_positions=direct_coordinates, cell=matrix, pbc=ans)
    energy=get_energy_gulp(pathfilename)
    poscarx.info['c'] = nt
    poscarx.info['i'] = namein
    poscarx.info['e'] = energy
    return poscarx
#------------------------------------------------------------------------------------------
def get_all_xt_geometry_gulp(poscarlist, path):
    poscarout,count=[],0
    for ipos in poscarlist:
        iposname=ipos.info['i']
        filename = iposname + '.got'
        pos01 = get_geometry_gulp(path+filename)
        if pos01:
            poscarout.extend([pos01])
            count = count + 1
    if count==0: return False
    else: return poscarout
#------------------------------------------------------------------------------------------
def structure_recolector(folders, poscars_split):
    list_ne, list_at, list_nt, listall=[],[],[],[]
    ntot=0
    moleculeout=[]
    for ifolder, iposcars in zip(folders,poscars_split):
        ntot=ntot+len(iposcars)
        molx=get_all_xt_geometry_gulp(iposcars, ifolder+'/')
        if molx is not False:
            moleculeout=moleculeout+molx
        for iposcar in iposcars:
            id = get_termination_gulp(ifolder+'/'+iposcar.info['i']+'.got')
            if (id is False): list_ne.append(iposcar.info['i'])
            elif (id == 0):   list_at.append(iposcar.info['i'])
            elif (id == 1):   list_nt.append(iposcar.info['i'])
    nnt, nat, nne = len(list_nt), len(list_at), len(list_ne)
    pnt=int(float(nnt)*100.0/float(ntot))
    pat=int(float(nat)*100.0/float(ntot))
    print("Calculations with N.T. = %d (%d percent)" %(nnt,pnt))
    print("Calculations with A.T. = %d (%d percent)" %(nat,pat))
    if len(moleculeout)==0:
        print("ZERO calculation finished satisfactorily")
        exit()
    return moleculeout
#------------------------------------------------------------------------------------------
def send_sh_file(sh_file):
    os.system("bash %s" %(sh_file))
    os.system("rm -f %s" %(sh_file))
    return 0
#------------------------------------------------------------------------------------------
def calculator_all_gulp(poscar_list_in, block_gulp, gulp_path, nproc, base_name):
    start = time.time()
    folder_names=prepare_folders(poscar_list_in, nproc, base_name)
    split_poscars= split_poscarlist(poscar_list_in, nproc)
    for poscars, ifolder in zip(split_poscars, folder_names):
        for iposcar in poscars:
            make_ainput_gulp(block_gulp, iposcar, ifolder+'/')
        make_the_sh_gulp(ifolder, poscars, gulp_path)
    procs = []
    print("Local submit: %sproc01.sh to %sproc%s.sh" %(base_name, base_name, str(nproc).zfill(2)), end=" ")
    for ifolder in folder_names:
        if os.path.isfile(ifolder+'.sh'):
            proc = Process(target=send_sh_file, args=(ifolder+'.sh',))
            procs.append(proc)
            proc.start()
    for proc in procs:
        proc.join()
    end = time.time()
    print('TOTAL TIME: %5.2f s' %(end - start))
    poscar_list_out=structure_recolector(folder_names, split_poscars)
    return poscar_list_out
#------------------------------------------------------------------------------------------
def display_info(moleculein, stage_string, dicc_term):
    print("-------------------------------------------------------------------")
    print("------------------------- SUMMARY %s -------------------------" %(stage_string))
    print("Number File--------Name   Energy (ev)   Delta----E T")
    molzz = sort_by_energy(moleculein, 1)
    emin = molzz[0].info['e']
    for ii, imol in enumerate(molzz):
        ei = imol.info['e']
        id = imol.info['i']
        #nt = imol.info['c']
        nt = dicc_term[id]
        deltae  =  ei - emin
        kk=str(ii+1).zfill(6)
        print("%s %s %13.8f %12.8f %d" %(kk, id, ei, deltae, nt))
#------------------------------------------------------------------------------------------------
