"""wrapper classes for ASE calculators and algorithms"""
import importlib
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import numpy
from scipy import sparse
from matplotlib import pyplot
from ase import Atoms
from ase.utils import IOContext
from ase.io import read
from ase.build import minimize_rotation_and_translation
from ase.geometry.analysis import Analysis
from ase.eos import EquationOfState
from ase.dft.dos import DOS
from ase.mep import NEBTools, DimerControl, MinModeAtoms, MinModeTranslate
from ase.vibrations import Vibrations
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.vasp import Vasp
from ase.md import velocitydistribution
from ase.neighborlist import NeighborList, natural_cutoffs
from ase.neighborlist import PrimitiveNeighborList, NewPrimitiveNeighborList
from virtmat.language.utilities.errors import RuntimeValueError
from virtmat.language.utilities.ase_params import spec
from virtmat.language.utilities.warnings import warnings, TextSUserWarning


@contextmanager
def plot_backend(backend):
    """a context manager for switching to a non-interactive backend and back"""
    assert backend in pyplot.rcsetup.all_backends
    current_backend = pyplot.get_backend()
    try:
        pyplot.switch_backend(backend)
        yield pyplot
    finally:
        pyplot.close()
        pyplot.switch_backend(current_backend)


class RMSD(IOContext):  # not covered
    """A wrapper algorithm to calculate root mean square deviation"""
    results = None

    def __init__(self, atoms):
        self.atoms_list = [atoms] if isinstance(atoms, Atoms) else atoms

    def run(self, reference, adjust=True):
        """Calculate the root mean square deviation (RMSD) between a structure
           and a reference"""
        assert len(reference) == 1
        rmsd = []
        for atoms in self.atoms_list:
            ref_atoms = reference.to_ase()[0]
            if adjust:
                minimize_rotation_and_translation(ref_atoms, atoms)
            rmsd.append(numpy.sqrt(numpy.mean((numpy.linalg.norm(atoms.get_positions()
                                   - ref_atoms.get_positions(), axis=1))**2, axis=0)))
        self.results = {'rmsd': numpy.mean(rmsd), 'output_structure': self.atoms_list}
        return True


class RDF(IOContext):
    """A wrapper algorithm to calculate radial distribution function"""
    results = None

    def __init__(self, atoms):
        self.atoms_list = [atoms] if isinstance(atoms, Atoms) else atoms
        if any(sum(sum(a.cell)) == 0 for a in self.atoms_list):  # not covered
            msg = 'the structure cell must have at least one non-zero vector'
            raise RuntimeValueError(msg)

    def run(self, rmax=None, nbins=40, neighborlist=None, elements=None):
        """Calculate the radial distribution function for a structure"""
        neighborlist_pars = neighborlist and neighborlist['parameters'] or {}
        analysis = Analysis(self.atoms_list, **neighborlist_pars)
        rmax = rmax or 0.49*max(max(a.cell.lengths()) for a in self.atoms_list)
        ret = analysis.get_rdf(rmax, nbins, elements=elements, return_dists=True)
        self.results = {'rdf': numpy.mean([a for a, b in ret], axis=0),
                        'rdf_distance': numpy.mean([b for a, b in ret], axis=0)}
        return True


class VelocityDistribution(IOContext):
    """A wrapper algorithm for velocity distributions"""
    results = None

    def __init__(self, atoms, distribution='maxwell-boltzmann', **kwargs):
        self.atoms = atoms
        assert isinstance(self.atoms, Atoms)
        assert distribution == 'maxwell-boltzmann'
        velocitydistribution.MaxwellBoltzmannDistribution(self.atoms, **kwargs)

    def run(self, stationary, zero_rotation, preserve_temperature=True, nbins=40):
        """optionally correct for translations/rotations and construct a histogram"""
        if stationary:
            velocitydistribution.Stationary(self.atoms,
                                            preserve_temperature=preserve_temperature)
        if zero_rotation:
            velocitydistribution.ZeroRotation(self.atoms,
                                              preserve_temperature=preserve_temperature)
        tpl = numpy.histogram(self.atoms.get_velocities().flatten(), bins=nbins)
        self.results = {'vdf': tpl[0], 'velocity': tpl[1]}
        return True


class EOS(IOContext):
    """A wrapper algorithm to fit the equation of state"""
    results = None

    def __init__(self, configs):
        assert isinstance(configs, list)
        self.volumes = [a.get_volume() for a in configs]

    def run(self, energies, eos='sjeos', filename=None):
        """v0: optimal volume, e0: minimum energy, B: bulk modulus"""
        obj = EquationOfState(self.volumes, energies, eos=eos)
        keys = ('minimum_energy', 'optimal_volume', 'bulk_modulus', 'eos_volume',
                'eos_energy')
        self.results = dict(zip(keys, obj.getplotdata()[1:7]))
        with plot_backend('agg'):
            obj.plot(filename)
        return True


class DensityOfStates(IOContext):  # not covered
    """A wrapper algorithm to calculate the density of states"""
    results = None

    def __init__(self, atoms):
        atoms.get_potential_energy()
        self.calc = atoms.calc

    def run(self, width=0.1, window=None, npts=401, spin=None):
        """add density of states and sampling energy points to results"""
        window = window if window is None else tuple(window.tolist())
        obj = DOS(self.calc, width=width, window=window, npts=npts)
        self.results = {'dos_energy': obj.get_energies(), 'dos': obj.get_dos(spin=spin)}
        return True


class BandStructure(IOContext):
    """A wrapper algorithm to calculate the band structure"""
    results = None

    def __init__(self, atoms):
        atoms.get_potential_energy()
        self.calc = atoms.calc

    def run(self, **kwargs):
        """add band structure path, energies, reference to results"""
        obj = self.calc.band_structure()
        keys = ('path', 'energies', 'reference')
        self.results = {'band_structure': {k: getattr(obj, k) for k in keys}}
        if kwargs.get('filename'):
            with plot_backend('agg'):
                obj.plot(**kwargs)
        return True


class NudgedElasticBand(IOContext):
    """a wrapper class for the NEB algorithm from ASE, no parallel NEB yet"""
    results = None
    trajectory = None

    def __init__(self, if_inp, **kwargs):
        assert isinstance(if_inp, list) and len(if_inp) == 2
        assert all(isinstance(a, Atoms) for a in if_inp)

        self.n_images = kwargs.pop('number_of_images')
        images = [if_inp[0]]
        for _ in range(self.n_images-2):
            image = if_inp[0].copy()
            image.calc = if_inp[0].calc  # should be copied for parallel
            image.set_constraint(if_inp[0].constraints)
            images.append(image)
        images.append(if_inp[1])

        if_inp[0].calc = SinglePointCalculator(if_inp[0],
                                               energy=if_inp[0].get_potential_energy(),
                                               forces=if_inp[0].get_forces())
        if_inp[1].calc = SinglePointCalculator(if_inp[1],
                                               energy=if_inp[1].get_potential_energy(),
                                               forces=if_inp[1].get_forces())
        interpolate_method = kwargs.pop('interpolate_method')
        interpolate_mic = kwargs.pop('interpolate_mic')
        self.dynamic_relaxation = kwargs.pop('dynamic_relaxation')
        if self.dynamic_relaxation:
            self.fmax = kwargs['fmax']
            class_name = 'DyNEB'
        else:
            del kwargs['fmax']
            del kwargs['scale_fmax']
            class_name = 'NEB'
        neb_class = getattr(importlib.import_module('ase.mep'), class_name)
        self.neb = neb_class(images, allow_shared_calculator=True, **kwargs)
        self.neb.interpolate(method=interpolate_method, mic=interpolate_mic,
                             apply_constraint=False)

    def run(self, optimizer, fit=False, filename=None, **kwargs):
        """run an NEB simulation"""
        module = importlib.import_module(spec[optimizer['name']]['module'])
        opt_class = getattr(module, spec[optimizer['name']]['class'])
        fmax = optimizer['parameters'].pop('fmax', 0.05)
        if self.dynamic_relaxation:
            fmax = self.fmax
        with opt_class(self.neb, **optimizer['parameters'], **kwargs) as obj:
            converged = obj.run(fmax=fmax)
            self.trajectory = obj.trajectory
        images = read(f'{self.trajectory.filename}@-{self.n_images}:')
        self.results = {}
        self.results['final_images'] = images
        nebt = NEBTools(images)
        energies = nebt.get_barrier(fit=fit)
        self.results['activation_energy'] = energies[0]
        self.results['reaction_energy'] = energies[1]
        self.results['maximum_force'] = numpy.sqrt((self.neb.get_forces() ** 2).sum(axis=1).max())
        self.results['forces'] = [i.get_forces() for i in images]
        self.results['energy'] = [i.get_potential_energy() for i in images]
        if filename:
            with plot_backend('agg'):
                nebt.plot_band().savefig(filename)
        return converged


class Dimer(MinModeTranslate):  # pylint: disable=W0223
    """a wrapper class for the Dimer algorithm from ASE"""

    def __init__(self, initial, mask=None, target=None, logfile=None, trajectory=None,
                 **kwargs):
        assert isinstance(initial, Atoms)
        mask = mask and mask.tolist()
        d_atoms = MinModeAtoms(initial, DimerControl(mask=mask, **kwargs))
        displ_kwargs = {'mic': any(initial.pbc), 'log': logfile}
        if kwargs.get('displacement_method') == 'vector':
            if target is None:
                msg = 'target structure needed to calculate displacement vector'
                raise RuntimeValueError(msg)
            displ = target.to_ase()[0].positions - initial.positions
            displ_kwargs['displacement_vector'] = 0.1*displ
        d_atoms.displace(**displ_kwargs)
        super().__init__(d_atoms, logfile=logfile, trajectory=trajectory)


class VibrationsWrapper(IOContext):
    """a wrapper class for the Vibrations algorithm from ASE"""
    results = None

    def __init__(self, atoms, **kwargs):
        assert isinstance(atoms, Atoms)
        self.atoms = atoms
        self.class_kwargs = kwargs

    def run(self, method='standard', direction='central', all_atoms=False, imag_tol=1e-5):
        """run vibrational analysis"""
        with TemporaryDirectory() as vib_cache:
            vib = Vibrations(self.atoms, name=vib_cache, **self.class_kwargs)
            vib.run()
            vib_data = vib.get_vibrations(method=method, direction=direction)
        enes, modes = vib_data.get_energies_and_modes(all_atoms=all_atoms)
        hessian = vib_data.get_hessian()
        imag = sum(enes.imag > imag_tol)
        self.results = {'hessian': hessian, 'eigen_real': enes.real,
                        'eigen_imag': enes.imag, 'eigen_modes': modes,
                        'transition_state': imag == 1, 'energy_minimum': imag == 0}
        return True


class NeighborListWrapper(IOContext):
    """a wrapper class for the NeighborList algorithms in ASE"""
    results = None

    def __init__(self, atoms, cutoffs=None, method='quadratic', **kwargs):
        assert isinstance(atoms, Atoms)
        self.atoms = atoms
        if cutoffs is None:
            cutoffs = natural_cutoffs(atoms)
        assert method in ('quadratic', 'linear')
        pclass = PrimitiveNeighborList if method == 'quadratic' else NewPrimitiveNeighborList
        self.nl = NeighborList(cutoffs, primitive=pclass, **kwargs)

    def run(self):
        """update neghbor list and get the properties"""
        self.nl.update(self.atoms)
        neighbors = []
        neighbor_offsets = []
        for atom in self.atoms:
            neighbors_ = self.nl.get_neighbors(atom.index)
            neighbors.append(neighbors_[0])
            neighbor_offsets.append(neighbors_[1])
        matrix = self.nl.get_connectivity_matrix(sparse=False)
        _, components = sparse.csgraph.connected_components(matrix)
        self.results = {'neighbors': neighbors, 'neighbor_offsets': neighbor_offsets,
                        'connectivity_matrix': matrix, 'connected_components': components}
        return True


def vasp_calculate_decorator(func):
    """perform modifications of Vasp.calculate's arguments"""
    def calculate_wrapper(self, atoms, *args, **kwargs):
        if not all(p for p in atoms.pbc):
            warnings.warn('setting PBC for structure in Vasp', TextSUserWarning)
            atoms.pbc = True
        return func(self, atoms, *args, **kwargs)
    return calculate_wrapper


Vasp.calculate = vasp_calculate_decorator(vars(Vasp)['calculate'])
