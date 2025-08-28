from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Molecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
#------------------------------------------------------------------------------------------
def molase2pymatgen(moleculease):
    if any(moleculease.pbc):
        structurepymatgen = AseAtomsAdaptor.get_structure(moleculease)
        return structurepymatgen
    else:
        symbols = moleculease.get_chemical_symbols()
        positions = moleculease.get_positions()
        moleculepymatgen=Molecule(symbols, positions)
        return moleculepymatgen
#------------------------------------------------------------------------------------------
def point_group(moleculease, tolerance=0.25, eigen_tolerance=1E-3, matrix_tolerance=0.1):
    molpmg=molase2pymatgen(moleculease)
    molx=PointGroupAnalyzer(molpmg, tolerance, eigen_tolerance, matrix_tolerance)
    pointgroup=molx.get_pointgroup()
    return pointgroup
#------------------------------------------------------------------------------------------
def symmetry_number(moleculease, tolerance=0.25, eigen_tolerance=1E-3, matrix_tolerance=0.1):
    molpmg=molase2pymatgen(moleculease)
    molx=PointGroupAnalyzer(molpmg, tolerance, eigen_tolerance, matrix_tolerance)
    symmetry_number=len(molx.get_symmetry_operations())
    return symmetry_number
#------------------------------------------------------------------------------------------
def inequivalent_finder(moleculease, tolerance=0.3, eigen_tolerance=0.008, matrix_tolerance=0.1):
    molpmg=molase2pymatgen(moleculease)
    #molpmg=AseAtomsAdaptor.get_structure(moleculease)
    molx=PointGroupAnalyzer(molpmg, tolerance, eigen_tolerance, matrix_tolerance)
    dictionary=molx.get_equivalent_atoms()
    dict=dictionary['eq_sets']
    inequiv=[ix for ix in dict.keys()]
    #for ix in dict.keys(): print(list(dict[ix]))
    #print('')
    inequiv.sort()
    return inequiv
#------------------------------------------------------------------------------------------
