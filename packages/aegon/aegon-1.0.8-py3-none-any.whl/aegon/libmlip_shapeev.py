import os
from aegon.libposcar import molecule2poscar
from aegon.libcfg import readcfgs, writecfgs
# -------------------------------------------------------------------
def make_mlp_relax_files(fileout, mlp_bin, mtp_pot):
    fh=open(fileout,'w')
    print("#!/bin/bash", file=fh)
    print("export OMP_NUM_THREADS=32", file=fh)
    print("MLP=%s" %(mlp_bin), file=fh)
    print("$MLP relax relax.ini --cfg-filename=initial.cfg --save-relaxed=relaxed.cfg --force-tolerance=1e-6 --stress-tolerance=1e-6", file=fh)
    print("if [ -f \"relaxed.cfg_0\" ]; then mv \"relaxed.cfg_0\" \"relaxed.cfg\"; fi", file=fh)
    fh.close()
    fg=open('relax.ini','w')
    print("mtp-filename           %s" %(mtp_pot), file=fg)
    fg.close()
# -------------------------------------------------------------------
def opt_mlip(molecules, mlp_bin, mtp_pot):
    poscars = molecule2poscar(molecules, 15.0)
    writecfgs(poscars,'initial.cfg', force=False)
    make_mlp_relax_files('relax.sh', mlp_bin, mtp_pot)    
    os.system('sh relax.sh')
    asemols=readcfgs('relaxed.cfg')
    os.system('rm -f initial.cfg relax.ini relax.sh')
    return asemols
# -------------------------------------------------------------------
