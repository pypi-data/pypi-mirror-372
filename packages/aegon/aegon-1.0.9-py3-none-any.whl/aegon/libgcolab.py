import py3Dmol
import numpy as np
from ase.data import covalent_radii, atomic_numbers
from ase.data.colors import cpk_colors as ase_cpk_colors
#-------------------------------------------------------------------------------
def viewmol_RDKit(atoms, width=300, height=300):
    view = py3Dmol.view(width=width, height=height)
    xyz_str=atoms2xyz_str(atoms)
    view.addModel(xyz_str, 'xyz')
    view.setStyle({'sphere': {'scale': 0.3}, 'stick': {'radius': 0.2}})
    view.setBackgroundColor("white")
    view.zoomTo()
    view.show()
#-------------------------------------------------------------------------------
MetalicElements = {
    'Li', 'Na', 'K', 'Rb', 'Cs', 'Fr', 'Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra',
    'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Y', 'Zr',
    'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'Hf', 'Ta', 'W', 'Re',
    'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
    'Rg', 'Cn', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',
    'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am',
    'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Al', 'Ga', 'In', 'Sn',
    'Tl', 'Pb', 'Bi', 'Po'
}
#-------------------------------------------------------------------------------
def rgb_to_hex(rgb):
    r, g, b = (int(255 * x) for x in rgb)
    return f'#{r:02X}{g:02X}{b:02X}'
#-------------------------------------------------------------------------------
def celda(a1, a2, a3, view):
    vertices = [np.array([0, 0, 0]), a1, a2, a3, a1 + a2, a1 + a3, a2 + a3, a1 + a2 + a3]
    vertices_dict = [{'x': float(v[0]), 'y': float(v[1]), 'z': float(v[2])} for v in vertices]
    aristas = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5),
               (3, 6), (4, 7), (5, 7), (6, 7)]
    for arista in aristas:
        view.addCylinder({'start': vertices_dict[arista[0]],'end': vertices_dict[arista[1]],'radius': 0.05, 'color': 'black'})
#-------------------------------------------------------------------------------
def origen(a1, a2, a3, view):
    longitud, radio_cilindro  = 2.5, 0.07
    origen = -0.75 * a1 + 0.5 * a3
    ejes = {'X': (np.array([.5, 0, 0]), 'red'),'Y': (np.array([0, .5, 0]), 'green'),'Z': (np.array([0, 0, .5]), 'blue')}
    num_segmentos, longitud_cono, radio_base_cono = 15, 0.3, 0.12
    for _, (vector, color) in ejes.items():
        start = origen
        end = origen + vector * longitud
        view.addCylinder({'start': {'x': float(start[0]), 'y': float(start[1]), 'z': float(start[2])},'end': {'x': float(end[0]), 'y': float(end[1]), 'z': float(end[2])},'radius': radio_cilindro,'color': color,'fromCap': True,'toCap': True})
        direction = end - start
        norm = np.linalg.norm(direction)
        if norm == 0:
            continue
        unit_dir = direction / norm
        base = end
        for i in range(num_segmentos):
            frac_start = longitud_cono * i / num_segmentos
            frac_end = longitud_cono * (i + 1) / num_segmentos
            cyl_start = base + unit_dir * frac_start
            cyl_end = base + unit_dir * frac_end
            radius = radio_base_cono * (1 - (i + 1) / num_segmentos)
            if radius <= 0:
                radius = 0.001
            view.addCylinder({'start': {'x': float(cyl_start[0]), 'y': float(cyl_start[1]), 'z': float(cyl_start[2])},'end': {'x': float(cyl_end[0]), 'y': float(cyl_end[1]), 'z': float(cyl_end[2])},'radius': radius,'color': color,'fromCap': True,'toCap': True})
#-------------------------------------------------------------------------------
def ValidBonds(atoms):
    num_atoms = len(atoms)
    bonds = []
    for i in range(num_atoms):
        for j in range(i + 1, num_atoms):
            a1, a2 = atoms[i], atoms[j]
            if a1.symbol in MetalicElements and a2.symbol in MetalicElements:
                continue
            try:
                r1 = covalent_radii[atomic_numbers[a1.symbol]]
                r2 = covalent_radii[atomic_numbers[a2.symbol]]
            except KeyError:
                r1 = r2 = 0.5
            dist = np.linalg.norm(a1.position - a2.position)
            if dist <= 1.2 * (r1 + r2):
                bonds.append((i, j))
    return bonds
#-------------------------------------------------------------------------------
def draw_bonds(atoms, bonds, view):
    for i, j in bonds:
        pos1, pos2 = atoms[i].position, atoms[j].position
        sym1, sym2 = atoms[i].symbol, atoms[j].symbol
        try:
            r1 = covalent_radii[atomic_numbers[sym1]]
        except (KeyError, IndexError):
            r1 = 0.15
        try:
            r2 = covalent_radii[atomic_numbers[sym2]]
        except (KeyError, IndexError):
            r2 = 0.15
        t = (r1 ** 0.15) / ((r1 ** 0.15) + (r2 ** 0.15))
        cut = pos1 + t * (pos2 - pos1)
        color1 = rgb_to_hex(ase_cpk_colors[atomic_numbers[sym1]])
        color2 = rgb_to_hex(ase_cpk_colors[atomic_numbers[sym2]])
        view.addCylinder({'start': dict(zip("xyz", pos1)),'end': dict(zip("xyz", cut)),'radius': 0.1,'color': color1})
        view.addCylinder({'start': dict(zip("xyz", cut)),'end': dict(zip("xyz", pos2)),'radius': 0.1, 'color': color2})
#-------------------------------------------------------------------------------
def viewmol_ASE(atoms, width=500, height=500):
    if isinstance(atoms, list): atoms=atoms[0] 
    view = py3Dmol.view(width=width, height=height)
    xyz_str = f"{len(atoms)}\n\n"
    for atom in atoms:
        x, y, z = atom.position
        xyz_str += f"{atom.symbol:2s} {x:14.9f} {y:16.9f} {z:16.9f}\n"
    view.addModel(xyz_str, 'xyz')
    for atom in atoms:
        symbol = atom.symbol
        try:
            atomic_num = atomic_numbers[symbol]
            r = covalent_radii[atomic_num]
        except (KeyError, IndexError):
            r = 0.5
        color = rgb_to_hex(ase_cpk_colors[atomic_numbers[symbol]])
        view.setStyle({"elem": symbol}, {"sphere": {"scale": r * 0.35, "color": color}})
    bonds = ValidBonds(atoms)
    draw_bonds(atoms, bonds, view)
    view.setBackgroundColor("white")
    if any(atoms.pbc):
        celda(atoms.cell[0], atoms.cell[1], atoms.cell[2], view)
        origen(atoms.cell[0], atoms.cell[1], atoms.cell[2], view)
    #view.zoomTo()
    view.show()
#-------------------------------------------------------------------------------
