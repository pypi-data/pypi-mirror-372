import random
import numpy as np
from ase import Atoms
#--------------------------------------------------------------------------------------------
def atom_exchange(atoms_in, rounds=1):
    """Randomly swaps the positions of atoms of different species in an ASE Atoms object.
    in:
        atoms_in (Atoms): The ASE Atoms object
        rounds (int): number of swaps to perform
    out:
        atoms_out: The new ASE Atoms object with exchanged atoms."""
    atoms_out = atoms_in.copy()
    n = len(atoms_out)
    species = set(atom.symbol for atom in atoms_out)
    if len(species) < 2:
        # Only one species, nothing to swap
        return atoms_out
    c = 0
    while c < rounds:
        i1, i2 = random.sample(range(n), 2)
        s1 = atoms_out[i1].symbol
        s2 = atoms_out[i2].symbol
        if s1 != s2:
            pos1 = atoms_out[i1].position.copy()
            pos2 = atoms_out[i2].position.copy()
            atoms_out[i1].position = pos2
            atoms_out[i2].position = pos1
            c = c + 1
    return atoms_out
#--------------------------------------------------------------------------------------------
def correct_cell_vectors(cell):
    '''Reduces the cell vectors of a crystal lattice by removing redundant vectors.
    in:
        cell (np.ndarray): 3x3 array representing the cell vectors
    out:
        new_cell (np.ndarray): 3x3 array with reduced cell vectors'''
    new_cell = cell.copy()
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            vi = new_cell[i]
            vj = new_cell[j]
            norm_vi = np.linalg.norm(vi)
            norm_vj = np.linalg.norm(vj)
            dot = np.dot(vi, vj)
            # Angle condition
            angle = np.arccos(dot / (norm_vi * norm_vj))
            if abs(angle - np.pi) > (np.pi / 3) and norm_vi >= norm_vj:
                # Reduction step
                factor = np.ceil(dot / (norm_vj ** 2)) * np.sign(dot)
                vi_new = vi - factor * vj
                new_cell[i] = vi_new
    return new_cell

#--------------------------------------------------------------------------------------------
def lattice_correction(atoms_in):
    """Applies the correction described above to the cell of an ASE Atoms object.
    Returns a new ASE Atoms object with the corrected lattice.
    """
    atoms_out = atoms_in.copy()
    cell = atoms_out.get_cell()
    corrected_cell = correct_cell_vectors(cell)
    # Rescale to preserve original volume
    orig_vol = np.linalg.det(cell)
    new_vol = np.linalg.det(corrected_cell)
    scale = (orig_vol / new_vol) ** (1/3)
    corrected_cell = corrected_cell * scale
    atoms_out.set_cell(corrected_cell, scale_atoms=True)
    return atoms_out
#--------------------------------------------------------------------------------------------
def lattice_mutation(atoms_in, strain_std):
    """Applies a random strain to the lattice of an ASE Atoms object and rescales to preserve volume.
    in:
        atoms_in (Atoms): ASE Atoms object
        strain_std (Float): Standard deviation for the Gaussian strain (default 0.05)
    out:
        atoms_out (Atoms): The new ASE Atoms object with the mutated lattice."""
    atoms_out = atoms_in.copy()
    cell = atoms_out.get_cell()
    orig_vol = atoms_out.get_volume()
    strain = np.zeros((3, 3))
    new_vol = 0
    while new_vol == 0:
        for i in range(3):
            for j in range(i, 3):
                if i == j:
                    strain[i, j] = np.clip(np.random.normal(loc=0.0, scale=strain_std), -0.5, 0.5) 
                else:
                    value = np.clip(np.random.normal(loc=0.0, scale=strain_std), -0.5, 0.5)
                    strain[i, j] = value / 2
                    strain[j, i] = value / 2
        strain_matrix = np.eye(3) + strain
        new_cell = np.dot(strain_matrix, cell)
        new_vol = np.linalg.det(new_cell)
    scale = (orig_vol / abs(new_vol)) ** (1/3)
    new_cell *= scale
    atoms_out.set_cell(new_cell, scale_atoms=True)
    atoms_out = lattice_correction(atoms_out)
    return atoms_out

#--------------------------------------------------------------------------------------------
def make_mutants(atoms_list_in, number_of_lattstr=1, number_of_atmxchange=1, strain_std=0.5, igen=0):
    """Generates mutants by applying lattice strain and atom exchange to a list of ASE Atoms objects.
    in:
        atoms_list_in (list): List of ASE Atoms objects to mutate
        number_of_lattstr (int): Number of lattice strain mutations to apply
        number_of_atmxchange (int): Number of atom exchange mutations to apply
    out:
        atoms_out (list): List of mutated ASE Atoms objects."""
    strain_atoms_out = []
    exchange_atoms_out = []
    # Lattice mutations
    # print('-------------------------------------------------------------------')
    # print('-----------------------GENERATOR OF MUTANTS------------------------')
    elegibleMutants = atoms_list_in.copy()
    random.shuffle(elegibleMutants)
    composition = elegibleMutants[0].get_chemical_symbols()
    unique_species = set(composition)
    strCount = 0
    xchCount = 0
    for i,atm in enumerate(elegibleMutants):
        strainMut = lattice_mutation(atm, strain_std)
        strainMut.set_pbc(True)
        strain_atoms_out.append(strainMut)
        print('mutant_'+str(igen+1).zfill(4)+'_'+str(i+1).zfill(4)+' ---> '+atm.info['i']+'_lattice_strain')
        strCount += 1
        if strCount >= number_of_lattstr:
            break
    # Atom exchange mutations only if more than one species
    random.shuffle(elegibleMutants)
    if len(unique_species) > 1:
        for atm in elegibleMutants:
            r = random.randint(1, 4)
            exchangeMut = atom_exchange(atm, r)
            exchangeMut.set_pbc(True)
            exchange_atoms_out.append(exchangeMut)
            print('mutant_'+str(igen+1).zfill(4)+'_'+str(strCount+1).zfill(4)+' ---> '+atm.info['i']+'_atom_exchange')
            strCount += 1
            xchCount += 1
            if xchCount >= number_of_atmxchange:
                break
    return strain_atoms_out, exchange_atoms_out



# from ase.io import write, read
# from libmakecrystals import random_crystal_generator
# x = random_crystal_generator('INPUT.txt')
# number_of_lattstr = 10
# number_of_atmxchange = 10
# mutants = make_mutants(x, number_of_lattstr, number_of_atmxchange)
# x = mutants[0]
# y = mutants[10]
# write('exchanged.vasp', x, format='vasp')
# write('latticestrained.vasp', y, format='vasp')



