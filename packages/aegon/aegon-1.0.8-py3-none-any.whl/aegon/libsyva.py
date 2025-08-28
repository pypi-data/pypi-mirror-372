import os
from ase import Atom, Atoms
from ase.data import chemical_symbols
#------------------------------------------------------------------------------------------
def syva(moleculeglomos):
    natoms=len(moleculeglomos)
    namein=moleculeglomos.info['i']
    energy=moleculeglomos.info['e']
    fh=open('syvamolinput',"w")
    print(namein, file=fh)
    print(natoms, file=fh)
    for iatom in moleculeglomos:
        ani = iatom.number
        xc, yc, zc = iatom.position
        print("%-2d %16.9f %16.9f %16.9f" %(ani, xc, yc, zc), file=fh)
    fh.close()
    os.system("syva all syvamolinput > syvamolout")
    syvafile=open('syvamolout','r')
    moleculeout=[]
    for line in syvafile:
        if "ERROR" in line:
            moltmp=moleculeglomos.copy()
            moltmp.info['c'] = 'X'
            return moltmp
        if "Optimized" in line:
            hls=line.split()
            pg=str(hls[1])
            moltmp = Atoms()
            moltmp.info['e'] = energy
            moltmp.info['i'] = namein
            moltmp.info['c'] = pg
            line=syvafile.readline()
            for ii in range(natoms):
                line=syvafile.readline()
                ls=line.split()
                ss=chemical_symbols[int(ls[0])]
                xc,yc,zc = float(ls[1]), float(ls[2]), float(ls[3])
                ai=Atom(symbol=ss, position=(xc, yc, zc))
                moltmp.append(ai)
            moleculeout.extend([moltmp])
    syvafile.close()
    os.system("rm -f syvamolinput syvamolout")
    return moleculeout[-1]
#------------------------------------------------------------------------------------------
def sym_syva(moleculelist):
    moleculeout=[]
    for imol in moleculelist:
        mol1=syva(imol)
        pg=mol1.info['c']
        print('%-11s run syva:%-3s' %(mol1.info['i'], pg))
        moleculeout.extend([mol1])
    return moleculeout
#------------------------------------------------------------------------------------------