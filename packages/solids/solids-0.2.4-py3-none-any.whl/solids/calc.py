block_gulp="""opti conj conp
switch_minimiser bfgs gnorm 0.01
vectors
LATTICEVECTORS
frac
COORDINATES
species
Ti  2.196
O  -1.098
buck
Ti Ti 31120.1 0.1540 5.25  15
O  O  11782.7 0.2340 30.22 15
Ti O  16957.5 0.1940 12.59 15
lennard 12 6
Ti Ti   1   0 15
O  O    1   0 15
Ti O    1   0 15
maxcyc 1500
"""
block_gulp = block_gulp.splitlines()
gulp_path='/Users/fortiz/installdir/bin/gulp'
nproc = 10
base_name='stage'
#------------------------------------------------------------------------------------------
class code:
    def __init__(self, list_of_atoms):
        self.list_of_atoms = list_of_atoms
    def set_EMT(self):
        from aegon.libcalc_emt import opt_EMT
        xopt=[opt_EMT(ix) for ix in self.list_of_atoms]
        return xopt
    def set_GULP(self, block_gulp=block_gulp, gulp_path=gulp_path, nproc=nproc, base_name=base_name):
        if gulp_path is None:
            print('Error in the path_exe for GULP')
        from aegon.libcodegulp import calculator_all_gulp
        xopt=calculator_all_gulp(self.list_of_atoms, block_gulp, gulp_path, nproc, base_name)
        return xopt
#------------------------------------------------------------------------------------------
