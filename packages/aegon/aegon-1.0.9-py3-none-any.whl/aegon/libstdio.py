import os.path
from ase.data import atomic_masses, atomic_numbers
#------------------------------------------------------------------------------------------
def sort_composition(composition):
    s=[[x[0],x[1], atomic_masses[atomic_numbers[x[0]]]] for x in composition]
    t = sorted(s, key=lambda x: float(x[2]), reverse=True)
    newcomposition=([[x[0],x[1]] for x in t])
    return newcomposition
#------------------------------------------------------------------------------------------
def clustername(composition):
    newcomposition=sort_composition(composition)
    chainname=' '.join([item[0]+str(item[1]) for item in newcomposition])
    return chainname
#------------------------------------------------------------------------------------------
def get_inatoms(composition):
    inatoms=[]
    newcomposition=sort_composition(composition)                                
    for xxx in newcomposition:
        for jj in range(xxx[1]):
            inatoms.append(xxx[0])
    return inatoms
#------------------------------------------------------------------------------------------
def get_elements(composition):
    newcomposition=sort_composition(composition)
    atoms=([x[0] for x in newcomposition])
    return atoms
#------------------------------------------------------------------------------------------
def read_var_composition(bilatu_file, id, index):
    bilfile=open(bilatu_file,"r")
    chainchar='---'+id.upper()+'---'
    printer=0
    data_block=[]
    for line in bilfile:
         lin = line.lstrip()
         if lin.startswith(chainchar): printer=1+printer
         if printer == 1 and not lin.startswith(chainchar):
             data_block.append(line.split())
    bilfile.close()
    nat, nvc, varcomp=len(data_block), len(data_block[0]), []
    for jj  in range(1,nvc):
        icomp=[]
        for ii in range(nat):
            atom=data_block[ii][0]
            nats=int(data_block[ii][jj])
            icomp.append([atom,nats])
        varcomp.append(icomp)
    class Composition:
        def __init__(self, xcomposition):
            self.comp    = sort_composition(xcomposition)
            self.atoms   = get_inatoms(self.comp)
            self.name    = clustername(self.comp)
            self.elements= get_elements(self.comp)
    classcomp=Composition(varcomp[index])
    return classcomp
#------------------------------------------------------------------------------------------
def read_block_of_bil(bilatu_file, id):
    bilfile=open(bilatu_file,"r")
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
def get_a_float(bilatu_file, strchain, defaultvalue):
    finalvalue=float(defaultvalue)
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    if len(readline) == 2:
                        data0=readline[0].strip('\t\n\r') 
                        data1=readline[1].strip('\t\n\r')
                        if data0.lower() == str(strchain): finalvalue=float(data1)
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
def get_a_int(bilatu_file, strchain, defaultvalue):
    finalvalue=int(defaultvalue)
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    if len(readline) == 2:
                        data0=readline[0].strip('\t\n\r') 
                        data1=readline[1].strip('\t\n\r')
                        if data0.lower() == str(strchain): finalvalue=int(data1)
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
def get_a_str(bilatu_file, strchain, defaultvalue):
    finalvalue=str(defaultvalue)
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    if len(readline) == 2:
                        data0=readline[0].strip('\t\n\r') 
                        data1=readline[1].strip('\t\n\r')
                        if data0.lower() == str(strchain): finalvalue=str(data1)
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
def get_float_list(bilatu_file, strchain, defaultvalue):
    finalvalue=[float(item) for item in defaultvalue]
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    data0=readline[0].strip('\t\n\r') 
                    if data0.lower() == str(strchain):
                        del readline[0]
                        data1=[float(item) for item in readline]
                        finalvalue=data1
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
def get_int_list(bilatu_file, strchain, defaultvalue):
    finalvalue=[int(item) for item in defaultvalue]
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    data0=readline[0].strip('\t\n\r') 
                    if data0.lower() == str(strchain):
                        del readline[0]
                        data1=[int(item) for item in readline]
                        finalvalue=data1
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
def get_str_list(bilatu_file, strchain, defaultvalue):
    finalvalue=[str(item) for item in defaultvalue]
    if os.path.isfile(bilatu_file):
        bilfile=open(bilatu_file,"r")
        for line in bilfile:
            line=line.strip(' \t\n\r')
            if len(line.strip()) != 0 :
                li = line.lstrip()
                if not li.startswith("#"):
                    readline=line.split()
                    data0=readline[0].strip('\t\n\r') 
                    if data0.lower() == str(strchain):
                        del readline[0]
                        data1=[str(item) for item in readline]
                        finalvalue=data1
        bilfile.close()
    return finalvalue
#------------------------------------------------------------------------------------------
class read_main_input:
    def __init__(self, filename):
        self.filename = filename

    def get_int(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        #return get_a_int(self.filename, key, default)
        return get_value_from_file(self.filename, key, int, default)

    def get_float(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return get_a_float(self.filename, key, default)

    def get_str(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return get_a_str(self.filename, key, default)

    def get_int_list(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return get_int_list(self.filename, key, default)

    def get_float_list(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return get_float_list(self.filename, key, default)

    def get_str_list(self, key, default):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return get_str_list(self.filename, key, default)

    def get_block(self, key):
        if not isinstance(key, str):
            raise TypeError("The first argument must be a (str).")
        return read_block_of_bil(self.filename, key)

    def get_comp(self, key, index=0):
        if not isinstance(key, str):
            raise TypeError("The key argument must be a (str).")
        if not isinstance(index, int):
            raise TypeError("The index argument must be a (int).")
        return read_var_composition(self.filename, key, index)      
#------------------------------------------------------------------------------------------
