"""
This module includes physical constants defined with pint. The list is a copy
from https://github.com/hgrecco/pint/blob/master/pint/constants_en.txt. Only the
ASCII compatible names are included here but no other names and no definitions.
As soon as there is python interface to access the list in pint this module will
become more automated. See issue https://github.com/hgrecco/pint/issues/1078.
"""
from virtmat.language.utilities.units import ureg

# MATHEMATICAL CONSTANTS
pi = ureg.Quantity(1., 'pi')
tansec = ureg.Quantity(1., 'tansec')
ln10 = ureg.Quantity(1., 'ln10')
wien_x = ureg.Quantity(1., 'wien_x')
wien_u = ureg.Quantity(1., 'wien_u')
eulers_number = ureg.Quantity(1., 'eulers_number')

# DEFINED EXACT CONSTANTS
speed_of_light = c = c_0 = ureg.Quantity(1., 'speed_of_light')
planck_constant = ureg.Quantity(1., 'planck_constant')
elementary_charge = e = ureg.Quantity(1., 'elementary_charge')
avogadro_number = ureg.Quantity(1., 'avogadro_number')
boltzmann_constant = k = k_B = ureg.Quantity(1., 'boltzmann_constant')
standard_gravity = g_0 = g0 = g_n = gravity = ureg.Quantity(1., 'standard_gravity')
standard_atmosphere = atm = atmosphere = ureg.Quantity(1., 'standard_atmosphere')
conventional_josephson_constant = K_J90 = ureg.Quantity(1., 'conventional_josephson_constant')
conventional_von_klitzing_constant = R_K90 = ureg.Quantity(1., 'conventional_von_klitzing_constant')

# DERIVED EXACT CONSTANTS
zeta = ureg.Quantity(1., 'zeta')
dirac_constant = hbar = atomic_unit_of_action = a_u_action = ureg.Quantity(1., 'dirac_constant')
avogadro_constant = N_A = ureg.Quantity(1., 'avogadro_constant')
molar_gas_constant = R = ureg.Quantity(1., 'molar_gas_constant')
faraday_constant = ureg.Quantity(1., 'faraday_constant')
conductance_quantum = G_0 = ureg.Quantity(1., 'conductance_quantum')
magnetic_flux_quantum = Phi_0 = ureg.Quantity(1., 'magnetic_flux_quantum')
josephson_constant = K_J = ureg.Quantity(1., 'josephson_constant')
von_klitzing_constant = R_K = ureg.Quantity(1., 'von_klitzing_constant')
stefan_boltzmann_constant = sigma = ureg.Quantity(1., 'stefan_boltzmann_constant')
first_radiation_constant = c_1 = ureg.Quantity(1., 'first_radiation_constant')
second_radiation_constant = c_2 = ureg.Quantity(1., 'second_radiation_constant')
wien_wavelength_displacement_law_constant = (
    ureg.Quantity(1., 'wien_wavelength_displacement_law_constant'))
wien_frequency_displacement_law_constant = (
    ureg.Quantity(1., 'wien_frequency_displacement_law_constant'))

# MEASURED CONSTANTS
newtonian_constant_of_gravitation = gravitational_constant = (
    ureg.Quantity(1., 'newtonian_constant_of_gravitation'))
rydberg_constant = R_inf = ureg.Quantity(1., 'rydberg_constant')
electron_g_factor = g_e = ureg.Quantity(1., 'electron_g_factor')
atomic_mass_constant = m_u = ureg.Quantity(1., 'atomic_mass_constant')
electron_mass = m_e = atomic_unit_of_mass = a_u_mass = ureg.Quantity(1., 'electron_mass')
proton_mass = m_p = ureg.Quantity(1., 'proton_mass')
neutron_mass = m_n = ureg.Quantity(1., 'neutron_mass')
x_unit_Cu = Xu_Cu = ureg.Quantity(1., 'x_unit_Cu')
x_unit_Mo = Xu_Mo = ureg.Quantity(1., 'x_unit_Mo')
angstrom_star = ureg.Quantity(1., 'angstrom_star')

# DERIVED CONSTANTS
fine_structure_constant = alpha = ureg.Quantity(1., 'fine_structure_constant')
vacuum_permeability = mu_0 = mu0 = magnetic_constant = ureg.Quantity(1., 'vacuum_permeability')
vacuum_permittivity = epsilon_0 = eps_0 = eps0 = electric_constant = (
    ureg.Quantity(1., 'vacuum_permittivity'))
impedance_of_free_space = Z_0 = characteristic_impedance_of_vacuum = (
    ureg.Quantity(1., 'impedance_of_free_space'))
coulomb_constant = k_C = ureg.Quantity(1., 'coulomb_constant')
classical_electron_radius = r_e = ureg.Quantity(1., 'classical_electron_radius')
thomson_cross_section = sigma_e = ureg.Quantity(1., 'thomson_cross_section')
