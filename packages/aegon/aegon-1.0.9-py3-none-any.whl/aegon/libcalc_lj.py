import numpy as np
from scipy.optimize import minimize
from joblib import Parallel, delayed
#-------------------------------------------------------------------------------
def lj_energy_forces(positions, epsilon, sigma, rc):
    N = len(positions)
    energy = 0.0
    forces = np.zeros_like(positions)
    rc2 = rc * rc  # para evitar sqrt innecesario
    for i in range(N):
        for j in range(i + 1, N):
            rij = positions[i] - positions[j]
            r2 = np.dot(rij, rij)
            if r2 > rc2:
                continue  # ignorar interacciones más allá del corte
            r = np.sqrt(r2)
            inv_r = 1.0 / r
            sr = sigma * inv_r
            sr2 = sr * sr
            sr6 = sr2 ** 3
            sr12 = sr6 ** 2
            energy += 4 * epsilon * (sr12 - sr6)
            f_scalar = 24 * epsilon * inv_r * (2 * sr12 - sr6)
            fij = f_scalar * (rij * inv_r)
            forces[i] += fij
            forces[j] -= fij
    return energy, forces
#-------------------------------------------------------------------------------
def lj_energy_forces_wrapper(x, epsilon, sigma, rc):
    positions = x.reshape(-1, 3)
    energy, forces = lj_energy_forces(positions, epsilon, sigma, rc)
    grad = -forces.reshape(-1)  # SciPy espera el negativo
    return energy, grad
#-------------------------------------------------------------------------------
def LennardJones(atoms):
    epsilon=1.0
    sigma=3.0/np.power(2, 1/6)
    rc=15.0
    gtol=1e-5
    x0 = atoms.positions
    result = minimize(
        fun=lambda x: lj_energy_forces_wrapper(x, epsilon, sigma, rc),
        x0=x0.reshape(-1),
        jac=True,  # indica que devolvemos gradiente junto con energía
        method='BFGS',
        options={'disp': False, 'gtol': gtol}
    )
    opt_positions = result.x.reshape(-1, 3)
    energy_final, forces_final = lj_energy_forces(opt_positions, epsilon, sigma, rc)
    atoms_opt = atoms.copy()
    atoms_opt.set_positions(opt_positions)
    atoms_opt.info['e']=energy_final
    return atoms_opt
#-------------------------------------------------------------------------------
def LennardJones_parallel(mol_list, n_jobs = 1):
    results = Parallel(n_jobs = n_jobs)(delayed(LennardJones)(mol) for mol in mol_list)
    return results
#-------------------------------------------------------------------------------
input_text = """6
-12.71206225     LJ006_00001_0002
Mo     11.772807036     12.159993396     10.178396957
Mo     11.277566246      9.443618118      9.040008025
Mo      9.535242754     11.756345682     12.114918975
Mo     11.760631543      9.769843487     11.969161528
Mo      9.052177457     11.430141513      9.185786627
Mo      9.040001964      9.040012804     10.976530043
6
-12.30292751     LJ006_00001_0001
Mo     10.011216235      9.039992171     10.552090687
Mo      9.040007179     11.877082056     10.552175104
Mo     13.003807795      9.040013548     10.552154000
Mo     13.974970821     11.877103433     10.552132896
Mo     11.507465985     11.147379143     12.064298773
Mo     11.507489000     11.147464649      9.040051436
6
 -9.35827433     LJ006_00002_0002
Mo     14.199278579      9.535364580      9.040000000
Mo      9.039997122     12.535775942      9.040000000
Mo     14.225265878     12.535822091      9.040000000
Mo      9.066007686      9.535364580      9.040000000
Mo     11.632608235     14.034585611      9.040000000
Mo     11.632631500     11.046865270      9.040000000
6
 -9.28925182     LJ006_00002_0001
Mo     14.905910371      9.040000651      9.040000000
Mo      9.039996962     10.173306028      9.040000000
Mo     16.861137137     11.307126933      9.040000000
Mo     11.975271820      9.604655663      9.040000000
Mo     10.995275530     12.440389349      9.040000000
Mo     13.925862279     11.875691376      9.040000000
"""
def example():
    from aegon.libutils import readxyzs
    file = 'LJ006.xyz'
    with open(file, "w") as f: f.write(input_text)
    print('SERIAL')
    for imol in readxyzs(file):
        mol=LennardJones(imol)
        print("%s: %.15f" %(mol.info['i'], mol.info['e']))
    print('PARALLEL')
    listmol=readxyzs(file)
    result=LennardJones_parallel(listmol, n_jobs = 4)
    for imol in result:
        print("%s: %.15f" %(imol.info['i'], imol.info['e']))
#example()
