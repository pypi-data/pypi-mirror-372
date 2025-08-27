.. index::
   single: Function reference; Calculators

ASE calculators
===============

:program:`calorine` provides two ASE calculators for NEP calculations, one that uses the GPU implementation and one that uses the CPU implementation of NEP.
For smaller calculations the CPU calculators is usually more performant.
For very large simulations and for comparison the GPU calculator can be useful as well.
The GPU calculator can also be used to set up molecular dynamics simulations with GPUMD using the :meth:`run_custom_md <calorine.calculators.GPUNEP.run_custom_md>` method.
         
.. currentmodule:: calorine.calculators

CPU calculator
--------------

.. autoclass:: CPUNEP
   :members: set_atoms, get_descriptors, get_dipole_gradient, get_polarizability, get_polarizability_gradient


GPU calculator
--------------

.. autoclass:: GPUNEP
   :members: run_custom_md, set_atoms, set_directory, single_point_parameters, command
