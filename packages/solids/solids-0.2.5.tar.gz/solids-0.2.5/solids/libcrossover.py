import os.path
import numpy as np
import random
from collections import Counter
from ase import Atoms
from ase.data import covalent_radii, atomic_numbers
from aegon.libstdio import read_block_from_file, read_main_input
#------------------------------------------------------------------------------------------------
def uc_restriction_solids(file):
    '''Obtains the UC restrictions imposed by the user. Format a b c alpha beta gamma.
    in: 
        file (str): path to the file containing the restrictions
    out: 
        restr_uc (list or None): List containing the parameters or None if not found'''
    restr_uc = None
    if os.path.isfile(file):
        with open(file, "r") as f:
            for line in f:
                if not line.startswith('#') and 'fixed_lattice' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        a, b, c = float(parts[1]), float(parts[2]), float(parts[3])
                        alpha, beta, gamma = float(parts[4]), float(parts[5]), float(parts[6])
                        restr_uc = [a, b, c, alpha, beta, gamma]
                    break
    return restr_uc

#------------------------------------------------------------------------------------------------
def get_percent_tolerances_solids(species, tolerance_percent):
    '''Gets the default tolerances for each pair of atoms in the structure.
    in:
        species (list): list of chemical symbols of the species in the structure
        tolerance_percent (float): percentage of the covalent radius to be used as tolerance
    out:
        solids_tolerances (list): list of tuples containing the species and their tolerance values'''
    solids_tolerances = []
    try:
        species_number = [atomic_numbers[s] for s in species]
    except KeyError as e:
        raise ValueError(f"Invalid species symbol: {e}")

    if len(species) == 1:
        s = species[0]
        n = species_number[0]
        r = covalent_radii[n]
        tv = round(r * tolerance_percent * 2, 2)
        solids_tolerances.append((s,s,tv))
    else:
        for i in range(len(species)):
            s1 = species[i]
            r1 = covalent_radii[species_number[i]]
            tv = round(r1 * tolerance_percent, 2)
            solids_tolerances.append((s1,s1,tv))
            for j in range(i + 1, len(species)):
                s2 = species[j]
                r2 = covalent_radii[species_number[j]]
                tv_mix = round((r1 + r2) * tolerance_percent, 2)
                solids_tolerances.append((s1,s2,tv_mix))
    return solids_tolerances

#------------------------------------------------------------------------------------------------
def interatom_restriction_solids(file):
    '''Reads interatomic tolerance restrictions from file. As a default, it uses the covalent radii of the species
    and the tolerance percentage specified in the file. If the file contains a TOLERANCES block, it reads the custom tolerances.
    in:
        file (str): path to the file containing the tolerances
    out:
        solids_tolerances (list of tuples), list of tuples containing the species and their tolerance values'''
    solids_tolerances = None
    if os.path.isfile(file):
        try:
            x = read_block_from_file(file, 'TOLERANCES')
            if not x:
                df = read_main_input(file)
                df_comp = df.get_comp(key='COMPOSITION')
                atms_specie = [k[0] for k in df_comp.comp]
                tolerance_percent = df.get_float(key='tol_atomic_overlap', default=0.95)
                solids_tolerances = get_percent_tolerances_solids(atms_specie, tolerance_percent)
            else:
                solids_tolerances = []
                for i in x:
                    part = i.strip().split()
                    if len(part) >= 3:
                        s1, s2, dist = part[0], part[1], float(part[2])
                        solids_tolerances.append(s1, s2, dist)
        except Exception as e:
            print(f"Error reading tolerances: {e}")
            return None
    return solids_tolerances

#--------------------------------------------------------------------------------------------
def uc_translation_3D(atoms_in):
    """Randomly translates the atomic positions of an ASE Atoms object within the unit cell.
    in:
        atoms_in (Atoms): ASE Atoms object representing the crystal structure.
    out:
        atoms_out (Atoms): A new ASE Atoms object with translated atomic positions."""
    scaled = atoms_in.get_scaled_positions()
    delta = np.random.rand(3)
    new_scaled = (scaled + delta) % 1.0
    atoms_out = atoms_in.copy()
    atoms_out.set_scaled_positions(new_scaled)
    return atoms_out

#--------------------------------------------------------------------------------------------
def translate_to_average_uc(atoms_a, atoms_b, weight_h=0.6, weight_s=0.4):
    """Computes the averaged unit cell of two Atoms and transforms their lattice vectors to match.
    The weights determine the contribution of each crystal to the new unit cell.
    in:
        atoms_a (Atoms): First precursor crystal structure.
        atoms_b (Atoms): Second precursor crystal structure.
        weight_h (float): Weight for the first crystal.
        weight_s (float): Weight for the second crystal.
    out:
        atoms_a (Atoms): Modified first crystal structure with the new unit cell.
        atoms_b (Atoms): Modified second crystal structure with the new unit cell.
        """
    cell_a = atoms_a.get_cell()
    cell_b = atoms_b.get_cell()
    new_cell = []
    for i in range(3):
        ai = cell_a[i]
        bi = cell_b[i]
        mag_ai = np.linalg.norm(ai)
        mag_bi = np.linalg.norm(bi)
        if mag_ai > mag_bi:
            ci = bi * weight_s + ai * weight_h
        elif mag_ai < mag_bi:
            ci = ai * weight_s + bi * weight_h
        else:
            ci = 0.5 * ai + 0.5 * bi
        new_cell.append(ci)
    new_cell = np.array(new_cell)
    atoms_a.set_cell(new_cell, scale_atoms=True)
    atoms_b.set_cell(new_cell, scale_atoms=True)
    return atoms_a, atoms_b

#--------------------------------------------------------------------------------------------
def parentCut(atoms_in, cellVector, randomPoint, above=True):
    """Cuts the crystal above or below a random point in the specified cell vector.
    in:
        atoms_in (Atoms): ASE Atoms object representing the crystal structure.
        cellVector (str): The cell vector to cut along ('a', 'b', or 'c').
        randomPoint (float): A random point in the range [0, 1) to determine the cut position.
        above (bool): If True, cuts above the random point; if False, cuts below.
    out:
        Atoms: A new ASE Atoms object containing the atoms that meet the cut condition."""
    originCell = atoms_in.get_cell()
    symbols = atoms_in.get_chemical_symbols()
    atomPos = atoms_in.get_scaled_positions()
    vec_idx = {'a': 0, 'b': 1, 'c': 2}[cellVector]
    if above:
        filtered = [(s, pos) for s, pos in zip(symbols, atomPos) if pos[vec_idx] < randomPoint]
    else:
        filtered = [(s, pos) for s, pos in zip(symbols, atomPos) if pos[vec_idx] > randomPoint]
    if not filtered:
        return None
    auxSymbList, auxPosList_frac = zip(*filtered)
    auxPosList_cart = np.dot(auxPosList_frac, originCell)
    return Atoms(symbols=auxSymbList, positions=auxPosList_cart, cell=originCell)

#--------------------------------------------------------------------------------------------
def check_minimum_distances(atoms_in, symbol, position, distances):
    """Checks if the distance between a new atom (symbol, position) and all atoms in atoms_in
    is above the minimum allowed for each pair in distances.
    in:
        atoms_in (Atoms): ASE Atoms object containing the existing atoms.
        symbol (str): The chemical symbol of the new atom.
        position (array-like): The position of the new atom.
        distances (list of tuples): List of tuples containing pairs of species and their minimum distances.
    
    out:
        bool: True if the new atom can be added without violating distance constraints, False otherwise."""
    for pair in distances:
        if pair[0] == symbol or pair[1] == symbol:
            other_symbol = pair[1] if pair[0] == symbol else pair[0]
            min_dist = pair[2]
            for iatom in atoms_in:
                if iatom.symbol == other_symbol:
                    distance = np.linalg.norm(iatom.position - position)
                    if distance < min_dist:
                        return False
    return True
#---------------------------------------------------------------------------------------------
def crossover(atoms_a, atoms_b):
    """Performs a crossover operation on two ASE Atoms objects.
    in:
        atoms_a (Atoms): First precursor crystal structure.
        atoms_b (Atoms): Second precursor crystal structure.
    out:
        atomsOut: A new ASE Atoms object containing the merged structure."""
    orig_comp = Counter(atoms_a.get_chemical_symbols())
    totalAtoms = len(atoms_a)
    for _ in range(30):
        cellVector = random.choice(['a', 'b', 'c'])
        randomPoint = random.uniform(0.4, 0.7)
        atoms_a_t = uc_translation_3D(atoms_a)
        atoms_b_t = uc_translation_3D(atoms_b)
        atoms_a_avg, atoms_b_avg = translate_to_average_uc(atoms_a_t, atoms_b_t)
        part1 = parentCut(atoms_a_avg, cellVector, randomPoint, above=True)
        part2 = parentCut(atoms_b_avg, cellVector, randomPoint, above=False)
        if part1 is None or part2 is None:
            continue
        x = random.choice([0,1])
        if x == 0:
            part1, part2 = part2, part1
        atomsOut = part1.copy()
        missing = orig_comp - Counter(atomsOut.get_chemical_symbols())
        to_add_symbols = []
        to_add_positions = []
        for iatom in part2:
            symbol = iatom.symbol
            position = iatom.position
            if missing[symbol] > 0:
                minimum_distances = interatom_restriction_solids('INPUT.txt')
                check = check_minimum_distances(atomsOut, symbol, position, minimum_distances)
                if not check:
                    continue
                to_add_symbols.append(symbol)
                to_add_positions.append(position)
                missing[symbol] -= 1
        atomsOut = atomsOut + Atoms(symbols=to_add_symbols, positions=to_add_positions, cell=atomsOut.get_cell())
        atomsOutsym = atomsOut.get_chemical_symbols()
        sorted_indices = sorted(range(len(atomsOutsym)), key=lambda i: atomsOutsym[i])
        atomsOut = atomsOut[sorted_indices]
        if Counter(atomsOut.get_chemical_symbols()) == orig_comp:
            atomsOut.pbc = True
            return atomsOut
    # If no valid crossover is found after 30 attempts, return None
    return None
 
#---------------------------------------------------------------------------------------------
# from ase.io import write, read
# from libmakextal import random_crystal_generator

# x = random_crystal_generator('INPUT.txt')
# write('random1.vasp', x[0], format='vasp')
# a, b = random.choice(x), random.choice(x)
# cross = crossover(x[0], x[1])
# if cross:
#     print(f"Crossover successful")
#     write('merged.vasp', cross, format='vasp')