"""various viewer functions for ASE"""
from fractions import Fraction
import numpy
import pandas
import pint
import matplotlib
from matplotlib import pyplot
from ase import io, visualize
from ase.eos import EquationOfState
from ase.spectrum.band_structure import BandStructure
from ase.dft.kpoints import BandPath
from ase.mep.neb import NEBTools
from ase.vibrations import VibrationsData
from ase.calculators.singlepoint import SinglePointCalculator
from virtmat.language.utilities.errors import RuntimeValueError, RuntimeTypeError
from virtmat.language.utilities.amml import AMMLStructure, Constraint


def show_atoms(atoms, show=True):
    """show atoms object(s)"""
    if show:
        visualize.view(atoms)


def display_amml_structure(obj, show=True):
    """display an atomic structure using ASE"""
    atoms_lst = obj.params[0].value.to_ase()
    if len(obj.params) == 2:
        constraints = [c for cs in obj.params[1].value for c in cs.to_ase()]
        for atoms_obj in atoms_lst:
            atoms_obj.constraints = constraints
    show_atoms(atoms_lst, show=show)


def display_amml_trajectory(obj, show=True):
    """display an AMML trajectory using ASE"""
    traj = obj.params[0].value
    if traj.filename:
        images = io.read(traj.filename, index=':')
        show_atoms(images, show=show)


def display_vibration(obj, show=True):
    """display a vibrational normal mode"""
    try:
        assert isinstance(obj.params[0].value, AMMLStructure)
        assert isinstance(obj.params[1].value, pandas.Series)
        assert isinstance(obj.params[1].value[0], pint.Quantity)
        assert isinstance(obj.params[1].value[0].magnitude, numpy.ndarray)
    except AssertionError as err:
        raise RuntimeTypeError(str(err)) from err
    atoms = obj.params[0].value.to_ase()[0]
    hessian = obj.params[1].value[0].to('eV / angstrom**2').magnitude
    mode = -1
    if len(obj.params) > 2:
        tab = obj.params[2].value
        if 'constraints' in tab.columns:
            if not all(isinstance(c, Constraint) for c in tab['constraints'][0]):
                raise RuntimeTypeError('constraints have incorrect type')
            atoms.set_constraint([c.to_ase()[0] for c in tab['constraints'][0]])
        if 'mode' in tab.columns:
            mode = tab['mode'][0].magnitude
    try:
        vib_data = VibrationsData(atoms, hessian)
    except ValueError as err:
        raise RuntimeValueError(str(err)) from err
    n_modes = len(vib_data.get_modes(all_atoms=True))
    mode %= n_modes
    images = []
    for image in vib_data.iter_animated_mode(mode):
        displ = vib_data.get_modes(all_atoms=True)[mode]
        image.calc = SinglePointCalculator(image, forces=displ)
        images.append(image)
    show_atoms(images, show=show)


def display_neb(obj, show=True):
    """display an NEB simulation from provided trajectory"""
    traj = obj.params[0].value
    if traj.filename:
        images = io.read(traj.filename, index=':')
        nebt = NEBTools(images)
        nebt.plot_bands()
        if show:
            pyplot.show()


def display_bs(obj, show=True):
    """display a band structure using ASE"""
    assert obj.params[0].type_ and issubclass(obj.params[0].type_, pandas.DataFrame)
    assert isinstance(obj.params[0].value, pandas.DataFrame)
    bs_dct = dict(next(obj.params[0].value.iterrows())[1])
    bs_dct['energies'] = bs_dct['energies'].to('eV').magnitude
    bs_dct['reference'] = bs_dct['reference'].to('eV').magnitude
    bp_dct = bs_dct['band_path']
    bp_dct = dict(next(bp_dct.iterrows())[1])
    sp_dct = bp_dct['special_points']
    sp_dct = dict(next(sp_dct.iterrows())[1])
    sp_dct = {k: v.to('angstrom**-1').magnitude for k, v in sp_dct.items()}
    bp_dct['special_points'] = sp_dct
    bp_dct['cell'] = bp_dct['cell'].to('angstrom').magnitude
    bp_dct['kpts'] = bp_dct['kpts'].to('angstrom**-1').magnitude
    band_path = BandPath(**bp_dct)
    bs = BandStructure(band_path, bs_dct['energies'], bs_dct['reference'])
    plt_kwargs = {}
    if len(obj.params) > 1:
        assert obj.params[1].type_ and issubclass(obj.params[1].type_, pandas.DataFrame)
        assert isinstance(obj.params[1].value, pandas.DataFrame)
        plt_dct = dict(next(obj.params[1].value.iterrows())[1])
        if 'emin' in plt_dct:
            plt_kwargs['emin'] = plt_dct['emin'].to('eV').magnitude
        if 'emax' in plt_dct:
            plt_kwargs['emax'] = plt_dct['emax'].to('eV').magnitude
    bs.plot(show=show, **plt_kwargs)


def display_eos(obj, show=True):
    """display fit to equation of state"""
    volumes = obj.params[0].value
    energies = obj.params[1].value
    eos_kwargs = {}
    if len(obj.params) == 3:
        eos_kwargs['eos'] = obj.params[2].value
    eos_obj = EquationOfState(volumes, energies, **eos_kwargs)
    eos_obj.plot(show=show)


def display_waterfall(obj, show=True):
    """display a reaction profile diagram of type waterfall"""
    fontsize = 14
    uprec = 2  # display precision of potentials and free energies
    barwidth = 0.25
    font = {'family': 'sans-serif', 'weight': 'normal', 'size': fontsize+2}
    matplotlib.rc('font', **font)
    matplotlib.rc('axes', linewidth=1.5)

    def autolabel(rects, ax, position='above'):
        """Attach a text label above each bar in *rects*, displaying its height."""
        offset = {'above': 3, 'below': -3}   # 3 points vertical offset
        valign = {'above': 'bottom', 'below': 'top'}
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{round(height, uprec)}',
                        xy=(rect.get_x()+rect.get_width()/2, height),
                        xytext=(0, offset[position]),
                        textcoords='offset points',
                        ha='center', va=valign[position])

    def get_ueffumax(reactions):
        """ calculate effective and critical potentials """
        fref = sum(r['free energy'] for r in reactions if r['electrons'] == 0)
        frst = sum(r['free energy'] for r in reactions)
        elec = sum(r['electrons'] for r in reactions)
        u0 = frst/elec
        ueff = u0 - fref/elec
        sign = -numpy.sign(elec)  # sign is positive for cathode reactions
        utol = 0.001  # stopping criterion in case of convergence
        ulim = 10.  # stopping criterion if umax is in invalid range
        umax = ueff
        delta = ueff / 2.0
        while abs(delta) > utol:
            free_umax = [r['free energy']-r['electrons']*umax for r in reactions]
            if all(feu <= 0 for feu in free_umax):
                if sign*delta < 0:
                    delta = -delta / 2.0
            else:
                if sign*delta > 0:
                    delta = -delta / 2.0
            umax += delta
            assert abs(umax) <= ulim
            # if abs(umax) > ulim:
            #     umax = -sign*numpy.infty
            #     break
        assert sign*ueff > sign*umax
        return ueff, umax

    def reverse_reactions(reactions):
        """return the reverse reactions and their properties"""
        result = []
        for r in reversed(reactions):
            react = {}
            for key in r:
                if key == 'equation':
                    react['equation'] = []
                    for t in reversed(r['equation']):
                        term = {}
                        term['coefficient'] = -t['coefficient']
                        term['species'] = t['species']
                        react['equation'].append(term)
                else:
                    react[key] = -r[key]
            result.append(react)
        return result

    def plot_diagram(reactions, metadata, rtype='orr'):
        """plot the waterfall diagram for oxygen reduction/evolution reaction"""

        if rtype == 'oer':
            _, ucrit = get_ueffumax(reverse_reactions(reactions))
        else:
            _, ucrit = get_ueffumax(reactions)

        orr_freeh = sum(r['free energy'] for r in reactions)
        orr_nelec = sum(r['electrons'] for r in reactions)

        freeh_opt = []
        for ri, reaction in enumerate(reactions):
            en = -orr_freeh*sum(r['electrons'] for r in reactions[ri:])/orr_nelec
            freeh_opt.append(en)
        freeh_opt.append(0.0)

        freeh = []
        for ri, reaction in enumerate(reactions):
            freeh.append(-sum(r['free energy'] for r in reactions[ri:]))
        freeh.append(0.0)

        free_crit = []
        for ri, reaction in enumerate(reactions):
            en = -sum(r['free energy']-ucrit*r['electrons'] for r in reactions[ri:])
            free_crit.append(en)
        free_crit.append(0.0)

        energ = []
        for ri, reaction in enumerate(reactions):
            energ.append(-sum(r['energy'] for r in reactions[ri:]))
        energ.append(0.0)

        def labfunc(spec, coeff):
            if abs(coeff) == 1.:
                return spec
            return ' '.join((str(Fraction(abs(coeff))), spec))

        labels = []
        for index, _ in enumerate(reactions):
            species = {}
            for reaction in reactions[index:]:
                for term in reaction['equation']:
                    if term['coefficient'] < 0:
                        if species.get(term['species']):
                            species[term['species']] += term['coefficient']
                        else:
                            species[term['species']] = term['coefficient']
            for reaction in reactions[index:-1]:
                for term in reaction['equation']:
                    if term['coefficient'] > 0:
                        if species.get(term['species']):
                            species[term['species']] += term['coefficient']
                        else:
                            species[term['species']] = term['coefficient']
            terms = [labfunc(k, v) for k, v in species.items() if v < 0]
            labels.append(' + '.join(terms))

        species = {}
        for reaction in reactions[1:]:
            for term in reaction['equation']:
                if term['coefficient'] < 0:
                    if species.get(term['species']):
                        species[term['species']] += term['coefficient']
                    else:
                        species[term['species']] = term['coefficient']
        for reaction in reactions:
            for term in reaction['equation']:
                if term['coefficient'] > 0:
                    if species.get(term['species']):
                        species[term['species']] += term['coefficient']
                    else:
                        species[term['species']] = term['coefficient']
        terms = [labfunc(k, v) for k, v in species.items() if v > 0]
        labels.append(' + '.join(terms))
        index = numpy.arange(len(labels))

        if rtype == 'oer':
            labels = list(reversed(labels))
            energ = list(reversed(energ))
            freeh = list(reversed(freeh))
            free_crit = list(reversed(free_crit))
            freeh_opt = list(reversed(freeh_opt))
            ucrit_label = r'\mathrm{min}'
            textx = 0
            texty = 5
            annotation_position = 'below'
        else:
            ucrit_label = r'\mathrm{max}'
            textx = 2.8
            texty = 5
            annotation_position = 'above'

        # plotting the figure
        labels = [
          r'${\ast} {+} \mathrm{O}_2 {+} 2 \mathrm{H}_2$',
          r'${\ast}{\mathrm{OOH}} {+} 3/2 \mathrm{H}_2$',
          r'${\ast}{\mathrm{O}} {+} \mathrm{H}_2 {+} \mathrm{H}_2\mathrm{O}$',
          r'${\ast}{\mathrm{OH}} {+} 1/2 \mathrm{H}_2 {+} \mathrm{H}_2\mathrm{O}$',
          r'${\ast} {+} 2 \mathrm{H}_2\mathrm{O}$']

        if rtype == 'oer':
            labels = list(reversed(labels))

        fig = pyplot.figure(figsize=(16, 9))
        plot = fig.add_subplot(111)
        plot.tick_params(direction='in', length=10, width=2, pad=10)
        ideal = plot.bar(index, freeh_opt, barwidth, edgecolor='k', color='w',
                         label=r'$\Delta G_{0, \mathrm{ideal}}$')
        free0 = plot.bar(index+1*barwidth, freeh, barwidth, color='b',
                         label=r'$\Delta G_0$')
        freeu = plot.bar(index+2*barwidth, free_crit, barwidth, color='r',
                         label=r'$\Delta G(U_{'+ucrit_label+r'})$')
        plot.set_xlabel('Reaction path')
        plot.set_ylabel('Free energy, eV')
        plot.set_xticks(index+barwidth)
        plot.set_xticklabels(labels)
        plot.tick_params(axis='x', length=0)
        autolabel(ideal, plot)
        autolabel(free0, plot)
        autolabel(freeu, plot, position=annotation_position)
        plot.legend(loc='lower left')
        text = r'$U_{'+ucrit_label+r'} =' + str(round(ucrit, uprec)) + r'$ V (vs. RHE)'
        plot.text(textx, texty, text, fontsize=fontsize+2, va='top', wrap=True)
        plot.set_title(repr(metadata), fontsize=fontsize-2, wrap=True)

    reactions_obj = obj.params[0].value
    reactions = []
    for r_obj in reactions_obj:
        eqn = []
        for term in r_obj.terms:
            eqn.append({'species': term['species'].name, 'coefficient': term['coefficient']})
        freeh = r_obj['free_energy'][0].to('eV').magnitude
        energy = r_obj['energy'][0].to('eV').magnitude
        r_dct = {'equation': eqn, 'electrons': -1, 'free energy': freeh, 'energy': energy}
        reactions.append(r_dct)
    metadata = {}
    kwargs = {'rtype': obj.params[1].value} if len(obj.params) == 2 else {}
    plot_diagram(reactions, metadata, **kwargs)
    if show:
        pyplot.show()
