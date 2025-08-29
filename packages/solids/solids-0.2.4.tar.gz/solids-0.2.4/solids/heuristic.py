import os
from aegon.libutils import sort_by_energy, cutter_energy, rename
from aegon.libposcar import writeposcars
from aegon.libstdio import read_main_input
from aegon.libroulette import get_roulette_wheel_selection
from solids.libdiscmbtrcrystals import comparator_mbtr_conv, descriptor_comparison_calculated, descriptor_comparison_calculated_vs_pool
from solids.libtools import display_mol_info
from solids.libmakextal import random_crystal_generator
from solids.libcrossover import crossover
from solids.libmutants import make_mutants
from solids.calc import code
import random
ndigit1=3
ndigit2=4
pformat='C'
#-------------------------------------------------------------------------------
def genetic_algorithm(inputfile='INPUT.txt'):
    #Reading variables
    df = read_main_input(inputfile)
    composition = df.get_comp(key='COMPOSITION')
    atomlist=composition.atoms
    nameid=composition.name
    nformulaunits=df.get_int(key='formula_units', default=1)
    nof_initpop=df.get_int(key='nof_initpop', default=10)
    nof_matings=df.get_int(key='nof_matings', default=5)
    nof_strains=df.get_int(key='nof_strains', default=5)
    nof_xchange=df.get_int(key='nof_xchange', default=5)
    tol_similarity=df.get_float(key='tol_similarity', default=0.95)
    cutoff_energy=df.get_float(key='cutoff_energy', default=5.0)
    cutoff_population=df.get_int(key='cutoff_population', default=8)
    nof_generations=df.get_int(key='nof_generations', default=3)
    nof_repeats=df.get_int(key='nof_repeats', default=2)
    nof_stagnant=df.get_int(key='nof_stagnant', default=3)
    calculator=df.get_str(key='calculator', default='ANI1ccx')
    nof_processes=df.get_int(key='nof_processes', default=1)
    #Welcome
    print('------- Genetic Algorithm for Crystal Structure Prediction -------')
    print('Chemical Formula        = %s'    %(nameid))
    print('Number of Formula units = %s'    %(nformulaunits))
    print('\nEVOLUTIVE PARAMETERS:')
    print('Initial Population      = %d'    %(nof_initpop))
    print('Number of matings       = %d'    %(nof_matings))
    print('Number of strains       = %d'    %(nof_strains))
    print('Number of xchange       = %d'    %(nof_xchange))
    print('\nDISCRIMINATION PARAMETERS:')
    print('Tol for similarity      = %4.2f' %(tol_similarity))
    print('Energy Cut-off          = %.2f'  %(cutoff_energy))
    print('Max population size     = %d'    %(cutoff_population))
    print('\nSTOP CRITERION:')
    print('Max generations         = %d'    %(nof_generations))
    print('Max repeated isomers    = %d'    %(nof_repeats))
    print('Max stagnant cycles     = %d'    %(nof_stagnant))
    print()
    print('Theory Level            = %s'    %(calculator))
    #Main Algorithm
    print('---------------------------GENERATION 0---------------------------')
    print('Construction of the guest population (nof_initpop=%d)\n' %(nof_initpop))
    xrand = random_crystal_generator(inputfile)
    # write('random_crystal1.vasp', xrand[0], format='vasp')
    print('written random_crystal1.vasp\n')
    rename(xrand, 'random_'+str(0).zfill(ndigit1), ndigit2)
    print('Optimization at %s:' %(calculator))

    if calculator=='EMT':
        cd=code(xrand)
        xopt=cd.set_EMT()
    elif calculator=='GULP':
        cd=code(xrand)
        block_gulp=df.get_block(key='GULP')
        path_exe=df.get_str(key='path_exe', default=None)
        xopt=cd.set_GULP(block_gulp=block_gulp, gulp_path=path_exe, nproc=nof_processes, base_name='stage')
        os.system('rm -rf stageproc*')

    print()
    print('--------------- Duplicates Removal in Generation ------------------')
    print('Max population size=%d; Energy Cut-off=%.2f; Tolerance for similarity=%4.2f' %(cutoff_population,cutoff_energy,tol_similarity))
    xopt=cutter_energy(xopt, cutoff_energy)
    xopt_sort=sort_by_energy(xopt, 1)
    xopt_sort = descriptor_comparison_calculated(xopt_sort, tol_similarity)
    # write('gen0_disc.vasp', xopt_sort[0], format='vasp')
    xopt_sort = xopt_sort[:cutoff_population]
    # write('gen0_optimized.vasp', xopt_sort[0], format='vasp')
    print('\n---------------------------GLOBAL SUMMARY---------------------------')
    display_mol_info(xopt_sort)
    namesi=[imol.info['i'] for imol in xopt_sort][:nof_repeats]
    count=0
    for igen in range(nof_generations):
        print("\n---------------------------GENERATION %d---------------------------" %(igen+1))
        print('Construction of crossovers ...\n')
        list_p=get_roulette_wheel_selection(xopt_sort, nof_matings)
        list_m=get_roulette_wheel_selection(xopt_sort, nof_matings)
        atoms_list_out=[]
        for i in range(nof_matings):
            atomsA, atomsB = random.choice(list_p), random.choice(list_m)
            if atomsA.info['i'] == atomsB.info['i']:
                atomsB = random.choice(list_m)
            cross = crossover(atomsA, atomsB)
            if cross:
                print('mating_'+str(igen+1).zfill(4)+'_'+str(i+1).zfill(4)+' ---> '+list_p[i].info['i']+'_x_'+list_m[i].info['i'])
                atoms_list_out.extend([cross])
        rename(atoms_list_out, 'mating_'+str(igen+1).zfill(ndigit1), ndigit2)
        # write('mating_'+str(igen+1).zfill(ndigit1)+'.vasp', atoms_list_out[0], format='vasp')
        print('\nConstruction of mutants ...\n')
        list_x=get_roulette_wheel_selection(xopt_sort, nof_strains+nof_xchange)
        strain_atoms, exchange_atoms = make_mutants(list_x, nof_strains, nof_xchange,igen=igen)
        rename(strain_atoms, 'mutant_'+str(igen+1).zfill(ndigit1), ndigit2)
        rename(exchange_atoms, 'mutant_'+str(igen+1).zfill(ndigit1), ndigit2)
        # write('strained_'+str(igen+1).zfill(ndigit1)+'.vasp', strain_atoms[0], format='vasp')
        # write('exchanged_'+str(igen+1).zfill(ndigit1)+'.vasp', exchange_atoms[0], format='vasp')
        atoms_list_mut = strain_atoms + exchange_atoms
        print('\nOptimization at %s:' %(calculator))

        if calculator=='EMT':
            cd=code(atoms_list_out+atoms_list_mut)
            generation_opt=cd.set_EMT()
        elif calculator=='GULP':
            cd=code(xrand)
            block_gulp=df.get_block(key='GULP')
            path_exe=df.get_str(key='path_exe', default=None)
            generation_opt=cd.set_GULP(block_gulp=block_gulp, gulp_path=path_exe, nproc=nof_processes, base_name='stage')
            os.system('rm -rf stageproc*')

        print('\nDiscrimination. Max population size=%d; Energy Cut-off=%.2f; Tol for similarity=%4.2f\n' %(cutoff_population,cutoff_energy,tol_similarity))
        generation_opt=cutter_energy(generation_opt, cutoff_energy)
        generation_opt=sort_by_energy(generation_opt,1)
        generation_opt = descriptor_comparison_calculated_vs_pool(generation_opt, xopt_sort, tol_similarity)
        xopt_sort=sort_by_energy(xopt_sort+generation_opt, 1)
        xopt_sort=xopt_sort[:cutoff_population]
        writeposcars(xopt_sort, 'summary.vasp', pformat)
        print('\n---------------------------GLOBAL SUMMARY---------------------------')
        display_mol_info(xopt_sort)
        namesj=[imol.info['i'] for imol in xopt_sort][:nof_repeats]
        numij=[1 for i, j in zip(namesi,namesj) if i == j]
        count=count+1 if sum(numij) == nof_repeats else 1
        if count == nof_stagnant:
            print("\nEarly termination. Max repeated isomers (%d) reached at the Max stagnant cycles (%d)." %(nof_repeats, nof_stagnant))
            break
        namesi=namesj
    print("\nGlobal optimization complete.")
    return xopt_sort
#-------------------------------------------------------------------------------
