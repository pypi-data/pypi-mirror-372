from ase     import Atoms
from ase.io  import write as ase_write
from ase.calculators.singlepoint import SinglePointCalculator
from aegon.libcodegaussian import get_geometry_gaussian, get_traj_gaussian
from aegon.libcodeorca     import get_geometry_orca,     get_traj_orca
from aegon.libcodevasp     import get_geometry_vasp,     get_traj_vasp 
from aegon.libcodegulp     import get_geometry_gulp
from aegon.libcfg          import writecfgs
from aegon.libutils        import writexyzs
from aegon.libposcar       import writeposcars
#------------------------------------------------------------------------------------------
# CREATION OF CLASSES
class read_out:
    
    def __init__(self):
       self.fileout_traj = {
           "gaussian": get_traj_gaussian,
           "orca":     get_traj_orca,
           "vasp":     get_traj_vasp
       } 
       self.fileout_geometry = {
           "gaussian": get_geometry_gaussian,
           "orca":     get_geometry_orca,
           "vasp":     get_geometry_vasp,
           "gulp":     get_geometry_gulp
       } 
    def traj(self, document, file_name, force=False):
        if document not in self.fileout_traj:
            raise ValueError(f"This '{document}' do not exist.")
        if not isinstance(file_name, str):
            raise TypeError("The second argument must be a (str).")
        if not isinstance(force, bool):
            raise TypeError("The third argument must be a boolean (True/False).")
        return self.fileout_traj[document](file_name, force)
    
    def geo(self,document,name):
        if document not in self.fileout_geometry:
            raise ValueError(f"This '{document}' do not exist.")
        if not isinstance(name, str):
            raise TypeError("The second argument must be a (str).")   
        return self.fileout_geometry[document](name)
#------------------------------------------------------------------------------------------
class write:
    @classmethod
    def cfg(cls, data, output_file, force=False):
        try:
            if isinstance(data, bool) and not data:
                raise ValueError("Data is False. Cannot execute cfg.")
            else:
               if not isinstance(data, list):
                   data = [data]
            if not isinstance(output_file, str):
                raise ValueError("The first argument must be a (str).")
            if not isinstance(force, bool):
                raise ValueError("The second argument must be a boolean (True/False).")
            writecfgs(data, output_file, force)  
            print("Writing %s" %(output_file))
        except Exception as e:
            print(f"Error in cfg: {e}")
    @classmethod
    def xyz(cls, data, output_file):
        try:
            if isinstance(data, bool) and not data:
                raise ValueError("Data is False. Cannot execute cfg.")
            else:
                if not isinstance(data, list):
                    data = [data]
            if not isinstance(output_file, str):
                raise ValueError("The first argument must be a (str).")
            writexyzs(data, output_file)  
            print("Writing %s" %(output_file))
        except Exception as e:
            print(f"Error in xyz: {e}")
    @classmethod       
    def poscar(cls,data, output_file, opt='D'):
        try:
            if isinstance(data, bool) and not data:
                raise ValueError("Data is False. Cannot execute cfg.")
            else:
                if not isinstance(data, list):
                    data = [data]
            if not isinstance(output_file, str):
                raise ValueError("The first argument must be a (str).")
            if not isinstance(opt, str):
                raise ValueError("The second argument must be a (str). \tOptions:D,C or other.")
            writeposcars(data, output_file, opt)
            print("Writing %s" %(output_file))
        except Exception as e:
            print(f"Error in vasp: {e}")
    @classmethod
    def extxyz(cls, data, output_file, force=False):
        try:
            if isinstance(data, bool) and not data:
                raise ValueError("Data is False. Cannot execute cfg.")
            else:
                if not isinstance(data, list):
                    data = [data]
            if not isinstance(output_file, str):
                raise ValueError("The first argument must be a (str).")

            poscarout=[]
            for ipos in data:
                if any(ipos.pbc):
                    atoms = Atoms(ipos.symbols, positions=ipos.positions, cell=ipos.cell, pbc=True)
                else:
                    atoms = Atoms(ipos.symbols, positions=ipos.positions, cell=[0, 0, 0], pbc=False)
                atoms.calc = SinglePointCalculator(atoms, energy=ipos.info['e'])
                if force: atoms.arrays['forces']=ipos.arrays['forces']
                poscarout.extend([atoms])
            ase_write(output_file, poscarout, format="extxyz")
            print("Writing %s" %(output_file))
        except Exception as e:
            print(f"Error in extxyz: {e}")
#------------------------------------------------------------------------------------------
