from ase.calculators.emt import EMT
from ase.optimize import BFGS
#------------------------------------------------------------------------------------------
def ene_EMT(moleculein):
    moleculein.calc = EMT()
    energy = moleculein.get_potential_energy()
    return energy
#------------------------------------------------------------------------------------------
def opt_EMT(moleculein):
    moleculein.calc = EMT()
    optimizer = BFGS(moleculein, logfile=None)
    optimizer.run(fmax=0.001)
    moleculein.info['e']=moleculein.get_potential_energy()
    return moleculein
#------------------------------------------------------------------------------------------
