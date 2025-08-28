import random
import os.path
from pyxtal import pyxtal
from pyxtal.symmetry import Group
from pyxtal.tolerance import Tol_matrix
from pyxtal.lattice import Lattice
from ase.data import covalent_radii, atomic_numbers
from aegon.libstdio import read_main_input, read_block_from_file
#------------------------------------------------------------------------------------------------
def uc_restriction_pyxtal(file):
    '''Obtains the UC restrictions imposed by the user. Format a b c alpha beta gamma.
    in: 
        file (str): path to the file containing the restrictions
    out: 
        restr_uc (Lattice or None): Pyxtal object for the lattice or None if not found'''
    restr_uc = None
    if os.path.isfile(file):
        with open(file, "r") as f:
            for line in f:
                if not line.startswith('#') and 'fixed_lattice' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        a, b, c = float(parts[1]), float(parts[2]), float(parts[3])
                        alpha, beta, gamma = float(parts[4]), float(parts[5]), float(parts[6])
                        restr_uc = Lattice.from_para(a, b, c, alpha, beta, gamma)
                    break
    return restr_uc

#------------------------------------------------------------------------------------------------
def get_percent_tolerances_pyxtal(species, tolerance_percent):
    '''Gets the default tolerances for each pair of atoms in the structure.
    in:
        species (list): list of chemical symbols of the species in the structure
        tolerance_percent (float): percentage of the covalent radius to be used as tolerance
    out:
        pyxtal_tolerances (Tol_matrix): Pyxtal tolerance matrix with the specified tolerances'''
    pyxtal_tolerances = Tol_matrix()
    try:
        species_number = [atomic_numbers[s] for s in species]
    except KeyError as e:
        raise ValueError(f"Invalid species symbol: {e}")

    if len(species) == 1:
        s = species[0]
        n = species_number[0]
        r = covalent_radii[n]
        tv = round(r * tolerance_percent * 2, 2)
        pyxtal_tolerances.set_tol(s, s, tv)
    else:
        for i in range(len(species)):
            s1 = species[i]
            r1 = covalent_radii[species_number[i]]
            tv = round(r1 * tolerance_percent, 2)
            pyxtal_tolerances.set_tol(s1, s1, tv)
            for j in range(i + 1, len(species)):
                s2 = species[j]
                r2 = covalent_radii[species_number[j]]
                tv_mix = round((r1 + r2) * tolerance_percent, 2)
                pyxtal_tolerances.set_tol(s1, s2, tv_mix)
                #pyxtal_tolerances.set_tol(s2, s1, tv_mix)  # Ensure symmetry if needed
    return pyxtal_tolerances

#------------------------------------------------------------------------------------------------
def interatom_restriction_pyxtal(file):
    '''Reads interatomic tolerance restrictions from file. As a default, it uses the covalent radii of the species
    and the tolerance percentage specified in the file. If the file contains a TOLERANCES block, it reads the custom tolerances.
    in:
        file (str): path to the file containing the tolerances
    out:
        pyxtal_tolerances (Tol_matrix or None): Pyxtal tolerance matrix with the specified tolerances or None if not found.'''
    pyxtal_tolerances = None
    if os.path.isfile(file):
        try:
            x = read_block_from_file(file, 'TOLERANCES')
            if not x:
                df = read_main_input(file)
                df_comp = df.get_comp(key='COMPOSITION')
                atms_specie = [k[0] for k in df_comp.comp]
                tolerance_percent = df.get_float(key='tol_atomic_overlap', default=0.95)
                pyxtal_tolerances = get_percent_tolerances_pyxtal(atms_specie, tolerance_percent)
            else:
                pyxtal_tolerances = Tol_matrix()
                for i in x:
                    part = i.strip().split()
                    if len(part) >= 3:
                        s1, s2, dist = part[0], part[1], float(part[2])
                        pyxtal_tolerances.set_tol(s1, s2, dist)
                        #pyxtal_tolerances.set_tol(s2, s1, dist)  # Ensure symmetry
        except Exception as e:
            print(f"Error reading tolerances: {e}")
            return None
    return pyxtal_tolerances

#------------------------------------------------------------------------------------------------
def get_symmetry_constrains(file, str_range, dimension=3):
    '''Extracts a desired range of integers to be used as SGs in the construction of structures.
    in:
        file (str): path to the file containing the symmetry constraints
        str_range (str): string to identify the range in the file (e.g., 'symmetries')
        dimension (int): dimension of the crystal structure (2 or 3)
    out:
        range_list (list): list of integers representing the range of symmetries'''
    range_list = []
    if os.path.isfile(file):
        with open(file, 'r') as f:
            for line in f:
                if not line.startswith('#') and str_range in line:
                    parts = line.strip().split()
                    if len(parts) > 1 and '-' in parts[1]:
                        try:
                            start, end = map(int, parts[1].split('-'))
                            range_list = list(range(start, end + 1))
                        except Exception:
                            pass
                    break
    if not range_list:
        if dimension == 2:
            range_list = list(range(2, 81))
        elif dimension == 3:
            range_list = list(range(2, 231))
    return range_list

#------------------------------------------------------------------------------------------------
def random_crystal_generator(file):
    df = read_main_input(file)
    composition = df.get_comp(key='COMPOSITION')
    species = [k[0] for k in composition.comp]
    formula_units = df.get_int('formula_units',2)
    atms_per_specie = [k[1]*formula_units for k in composition.comp]
    dimension = df.get_int('dimension',3)
    vol_factor = df.get_float('volume_factor',1.0)
    revisit_syms = df.get_int('revisit_syms',1)
    tol_atomic_overlap = df.get_float('tol_atomic_overlap',0.97)
    number_of_xtals = df.get_int('number_of_xtals',False)
    sym_list = get_symmetry_constrains(file,'symmetries', dimension)
    uc_rest = uc_restriction_pyxtal(file)
    pyxtal_mtx_tolerance = interatom_restriction_pyxtal(file)
    xtalist_out = []
    xc = 1
    for i in range(revisit_syms):
        if number_of_xtals:
            random.shuffle(sym_list)
        for sym in sym_list:
            xtal = pyxtal()
            if dimension == 2:
                try:
                    xtal.from_random(dimension,sym,species,atms_per_specie,thickness=0.0)
                except:
                    continue
                else:
                    sg = Group (sym)
                    sg_symbol = str(sg.symbol)
                    ase_xtal = xtal.to_ase()
                    print('random_000_'+str(xc).zfill(3)+' ---> SG_'+str(sg_symbol)+"_("+str(sym)+")")
                    xtalist_out.append(ase_xtal)
                    xc = xc + 1
            elif dimension == 3:
                try:
                    if uc_rest:
                        xtal.from_random(dimension,sym,species,atms_per_specie,vol_factor,uc_rest,pyxtal_mtx_tolerance)
                    else:
                        xtal.from_random(dimension,sym,species,atms_per_specie,vol_factor,tm=pyxtal_mtx_tolerance)
                except:
                    continue
                else:
                    sg = Group (sym)
                    sg_symbol = str(sg.symbol)
                    ase_xtal = xtal.to_ase()
                    print('random_000_'+str(xc).zfill(3)+' ---> SG_'+str(sg_symbol)+"_("+str(sym)+")")
                    xtalist_out.append(ase_xtal)
                    xc = xc + 1
            if number_of_xtals!= False and xc == number_of_xtals+1:
                break
    return xtalist_out
#------------------------------------------------------------------------------------------------
input_text = """
---COMPOSITION---
Au 2
Ag 3
---COMPOSITION---
formula_units       2
dimension           3
number_of_xtals     5
symmetries          16-74
fixed_lattice       2.474 8.121 6.138 90.0 90.0 90.0
#custom_tolerances   Ti,Ti,1.2 Ti,O,1.3 O,O,1.2
tol_atomic_overlap  0.90
"""
def test():
    file = 'INPUT.txt'
    with open(file, "w") as f: f.write(input_text)
    x = random_crystal_generator(file)
#------------------------------------------------------------------------------------------------
