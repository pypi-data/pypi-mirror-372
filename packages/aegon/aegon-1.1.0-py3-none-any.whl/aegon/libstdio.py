import os.path
from ase.data import atomic_masses, atomic_numbers
#------------------------------------------------------------------------------------------
def sort_composition(composition):
    s=[[x[0],x[1], atomic_masses[atomic_numbers[x[0]]]] for x in composition]
    t = sorted(s, key=lambda x: float(x[2]), reverse=True)
    newcomposition=([[x[0],x[1]] for x in t])
    return newcomposition
#------------------------------------------------------------------------------------------
def get_inatoms(composition):
    newcomposition=sort_composition(composition)                                
    inatoms=[]
    for xxx in newcomposition:
        for jj in range(xxx[1]):
            inatoms.append(xxx[0])
    return inatoms
#------------------------------------------------------------------------------------------
def clustername(composition):
    newcomposition=sort_composition(composition)
    chainname=' '.join([item[0]+str(item[1]) for item in newcomposition])
    return chainname
#------------------------------------------------------------------------------------------
def get_elements(composition):
    newcomposition=sort_composition(composition)
    atoms=([x[0] for x in newcomposition])
    return atoms
#------------------------------------------------------------------------------------------
#df = read_main_input(inputfile)
#cf=df.get_comp('composition').comp
def read_composition(filename, key):
    start_marker = f"---{key.upper()}---"
    end_marker = start_marker
    composition = []
    recording = False
    with open(filename, 'r') as file:
        for line in file:
            stripped = line.strip()
            if stripped == start_marker:
                recording = not recording
                continue
            if recording and stripped:
                parts = stripped.split()
                if len(parts) == 2:
                    element, count = parts[0], int(parts[1])
                    composition.append([element, count])
                else:
                    raise ValueError(f"Invalid line format in block '{key}': '{line.strip()}'")
    class Konpozition:
        def __init__(self, xcomposition):
            self.comp    = sort_composition(xcomposition)
            self.atoms   = get_inatoms(self.comp)
            self.name    = clustername(self.comp)
            self.elements= get_elements(self.comp)
    classcomp=Konpozition(composition)
    return classcomp
#------------------------------------------------------------------------------------------
def read_block_from_file(filepath, id):
    bilfile=open(filepath,"r")
    chainchar='---'+id.upper()+'---'
    printer=0
    data_block=[]
    for line in bilfile:
         lin = line.lstrip()
         if lin.startswith(chainchar): printer=1+printer
         if printer == 1 and not lin.startswith(chainchar): data_block.append(line)
    bilfile.close()
    return data_block 
#------------------------------------------------------------------------------------------
def get_value_from_file(filepath, key, dtype=str, default=None):
    """
    Reads the value associated with 'key' from a parameter file, ignoring comments.
    
    Parameters:
        filepath (str): Path to the input file.
        key (str): Name of the parameter to search for.
        dtype (type): Type of the value to return (int, float, str).
        default: Default value if key is not found.
    
    Returns:
        The parsed value of the specified type, or the default if not found.
    """
    if not os.path.isfile(filepath):
        return default
    with open(filepath, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].lower() == key.lower():
                value_str = parts[1]
                try:
                    return dtype(value_str)
                except ValueError:
                    print(f"Warning: Could not convert '{value_str}' to {dtype.__name__}. Returning default.")
                    return default
    return default
#------------------------------------------------------------------------------------------
def get_list_from_file(filepath, key, datatype, default=None):
    """
    Reads a list of values (int, float, or str) from a given key in an input file.
    Parameters:
        filepath (str): Path to the input file.
        key (str): Name of the variable to extract.
        datatype (type): Type to which each item should be cast (int, float, str).
        default (list): Default list to return if the key is not found.
    Returns:
        list: List of values of specified type.
    """
    if default is None:
        default = []
    if not os.path.isfile(filepath):
        return default
    with open(filepath, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue
            parts = line.split()
            if parts and parts[0].lower() == key.lower():
                try:
                    return [datatype(x) for x in parts[1:]]
                except ValueError:
                    print(f"Warning: Could not convert values in key '{key}' to {datatype.__name__}.")
                    return default
    return default
#------------------------------------------------------------------------------------------
class read_main_input:
    def __init__(self, filename):
        self.filename = filename
    def get_int(self, key, default):
        return get_value_from_file(self.filename, key, int, default)
    def get_float(self, key, default):
        return get_value_from_file(self.filename, key, float, default)
    def get_str(self, key, default):
        return get_value_from_file(self.filename, key, str, default)
    def get_int_list(self, key, default):
        return get_list_from_file(self.filename, key, int, default)
    def get_float_list(self, key, default):
        return get_list_from_file(self.filename, key, float, default)
    def get_str_list(self, key, default):
        return get_list_from_file(self.filename, key, str, default)
    def get_block(self, key):
        return read_block_from_file(self.filename, key)
    def get_comp(self, key, index=0):
        return read_composition(self.filename, key)
#------------------------------------------------------------------------------------------
