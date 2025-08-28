import os
import time
import numpy as np
from multiprocessing import Process
from dscribe.descriptors import MBTR, ValleOganov
from aegon.libposcar import readposcars, writeposcars
from aegon.libutils import prepare_folders, split_poscarlist
#------------------------------------------------------------------------------------------
def find_similar_elements(similarity_matrix, threshold):
    similar_elements_indices = []
    num_elements = similarity_matrix.shape[0]
    for i in range(num_elements):
        for j in range(i+1,num_elements):
            if similarity_matrix[i, j] >= threshold:
                similar_elements_indices.append(j)
    return similar_elements_indices
#------------------------------------------------------------------------------------------
def disc_MBTR(atoms, threshold, nproc=1):
    num_molecules = len(atoms)
    num_atomsxmol = len(atoms[0])
    r_cut=10
    species = set(atoms[0].get_chemical_symbols())
    geometry={"function": "distance"}
    weighting = {"function": "inverse_square", "r_cut": r_cut,  "threshold": 1E-3}
    grid={"min": 0, "max": r_cut, "sigma": 1E-5, "n" : 100}
    opt="none"
    # mbtr=MBTR(species=species, geometry=geometry, weighting=weighting,  grid=grid, periodic=True, normalization=opt, normalize_gaussians=True, sparse=False, dtype="float64")
    mbtr=ValleOganov(species=species,function='distance',n=100,sigma=1E-5,r_cut=r_cut)
    n_features=mbtr.get_number_of_features()
    if nproc ==1:
        descriptors=[mbtr.create(imol) for imol in atoms]
    elif nproc > 1:
        descriptors=mbtr.create(atoms, n_jobs=nproc)
    similar_elements_indices = []
    similarity_matrix = np.zeros((num_molecules, num_molecules))
    for i in range(num_molecules):
        vi=descriptors[i]
        for j in range(i, num_molecules):
            vj=descriptors[j]
            manhattan_distance=sum([np.absolute(a-b) for a,b in zip(vi,vj)])
            similarity=1.0/(1.0+manhattan_distance/float(n_features))
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity
    similar_elements_indices=find_similar_elements(similarity_matrix, threshold)
    similar_elements_indices.sort()
    #print(similar_elements_indices)
    disimilars_atoms=[atoms[i] for i in range(num_molecules) if i not in similar_elements_indices]
    return disimilars_atoms

#------------------------------------------------------------------------------------------
def descriptor_comparison_calculated(atoms_list_in, tolerance):
    '''This function compares the descriptors of structures in atoms_list_in and removes 
    those that are too similar to each other based on the given tolerance.
    in:
        atoms_list_in (list): list of Atoms objects
        tolerance (float): similarity threshold for removing duplicates
    out:
        atoms_list_out (list): list of Atoms objects that are not too similar to each other.'''
    atoms_list_out = []
    species = set(list(atoms_list_in[0].get_chemical_symbols()))
    vo = ValleOganov(species=species, function='distance', n=100, sigma=1E-5, r_cut=10)
    # vo = ValleOganov(species=species, k2 = {"sigma": 1E-5, "n":100, "r_cut":10})
    descriptors = [vo.create(structure) for structure in atoms_list_in]
    disc_count = 0
    for i in range(len(descriptors)):
        stop_flag = False
        for j in range(i+1, len(descriptors)):
            norm_i = np.linalg.norm(descriptors[i])
            norm_j = np.linalg.norm(descriptors[j])
            dot_product = np.dot(descriptors[i], descriptors[j])
            similarity = dot_product / (norm_i * norm_j)
            if similarity >= tolerance:
                print('%s removed, too similar to %s, similarity = %.5f' %(atoms_list_in[j].info['i'],atoms_list_in[i].info['i'],similarity))
                disc_count = disc_count + 1 
                stop_flag = True
                break
        if not stop_flag:
            atoms_list_out.append(atoms_list_in[i])
    print('\n'+str(disc_count)+' structures removed by similarity in generation comparison \n')
    return atoms_list_out

#------------------------------------------------------------------------------------------
def descriptor_comparison_calculated_vs_pool(atoms_calculated, atoms_pool, tolerance):
    '''This function compares the descriptors of structures in atoms_calculated with those in
    atoms_pool and removes those that are too similar based on the given tolerance.
    in:
        atoms_calculated (list): list of Atoms objects from the current generation
        atoms_pool (list): list of Atoms objects from the pool
        tolerance (float): similarity threshold for removing duplicates
    out:
        atoms_list_out (list): list of Atoms objects that are not too similar to each other.'''
    print('---------------- Duplicates Removal Gen vs Pool -------------------\n')
    different_calc = []
    atoms_list_out = []
    species = set(list(atoms_calculated[0].get_chemical_symbols()))
    vo = ValleOganov(species=species, function='distance', n=100, sigma=1E-5, r_cut=10)
    # vo = ValleOganov(species=species, k2 = {"sigma": 1E-5, "n":100, "r_cut":10})
    descr_calc = [vo.create(structure) for structure in atoms_calculated]
    descr_pool = [vo.create(structure) for structure in atoms_pool]
    disc_count = 0
    for i in range(len(descr_calc)):
        stop_flag = False
        for j in range(len(descr_pool)):
            norm_i = np.linalg.norm(descr_calc[i])
            norm_j = np.linalg.norm(descr_pool[j])
            dot_product = np.dot(descr_calc[i], descr_pool[j])
            similarity = dot_product / (norm_i * norm_j)
            if similarity >= tolerance:
                print('%s removed, too similar to %s, similarity = %.5f' %(atoms_calculated[i].info['i'],atoms_pool[j].info['i'],similarity)) 
                stop_flag = True
                disc_count = disc_count + 1
                break
        if not stop_flag:
            different_calc.append(atoms_calculated[i])
    if different_calc:
        print('\n'+str(disc_count)+' structures removed by similarity in Gen vs Pool comparison'+'\n')
        atoms_list_out.extend(different_calc)
    else:
        print('\nZero structures removed by similarity in Gen vs Pool comparison'+'\n')
    return atoms_list_out

#------------------------------------------------------------------------------------------
def comparator_mbtr_conv(atoms0, threshold, nproc):
    start = time.time()
    ni=len(atoms0)
    atoms1=disc_MBTR(atoms0, threshold, nproc)
    nf=len(atoms1)
    end = time.time()
    print('Comparator MBTR conv at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return atoms1
#------------------------------------------------------------------------------------------
def make_comparator_mbtr(ifolder, threshold):
    atoms0=readposcars(ifolder+'/'+ifolder+'.vasp')
    atoms1=disc_MBTR(atoms0, threshold, 1)
    writeposcars(atoms1,ifolder+'/'+ifolder+'_disc.vasp', 'D', 1)
#------------------------------------------------------------------------------------------
def comparator_mbtr_parallel(poscarlist, threshold, nproc, base_name):
    start = time.time()
    ni=len(poscarlist)
    folderlist=prepare_folders(poscarlist, nproc, base_name)
    poscar_split_list=split_poscarlist(poscarlist, nproc)
    procs = []
    #dicc_term = {iposcar.info['i']: iposcar.info['c'] for iposcar in poscarlist}
    for ifolder, iposcars in zip(folderlist, poscar_split_list):
        writeposcars(iposcars, ifolder+'/'+ifolder+'.vasp', 'D', 1)
        proc = Process(target=make_comparator_mbtr, args=(ifolder,threshold,))
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    moleculeout=[]
    for ifolder in folderlist:
        molx=readposcars(ifolder+'/'+ifolder+'_disc.vasp')
        #for imol in molx: imol.info['c']=dicc_term[imol.info['i']]
        moleculeout=moleculeout+molx
    #os.system('rm -rf %sproc[0-9][0-9]' %(base_name))
    nf=len(moleculeout)
    end = time.time()
    print('MBTR comparison (parallel) at %5.2f s [%d -> %d]' %(end - start, ni, nf))
    return moleculeout
#------------------------------------------------------------------------------------------
