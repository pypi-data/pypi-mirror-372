.. raw:: html

  <p>
  <a href="https://badge.fury.io/py/calorine"><img src="https://badge.fury.io/py/calorine.svg" alt="PyPI version" height="18"></a>
  <a href="https://doi.org/10.5281/zenodo.7919206"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.7919206.svg" alt="zenodo" height="18"></a>
  </p>

calorine
********

:program:`calorine` is a Python library for constructing and sampling neuroevolution potential (NEP) models via the `GPUMD <https://gpumd.org/>`_ package.
It provides ASE calculators, IO functions for reading and writing :program:`GPUMD` input and output files, as well as a Python interface that allows inspection of NEP models.

.. grid:: 4
   :gutter: 2

   .. grid-item-card:: Training analysis
      :link: model_training_tutorial
      :link-type: ref

      .. image:: _static/parity-plot.png
         :width: 100%

   .. grid-item-card:: Model manipulation
      :link: nep_analysis_tutorial
      :link-type: ref

      .. image:: _static/model-analysis.png
         :width: 100%

   .. grid-item-card:: Phonon dispersions
      :link: phonons_tutorial
      :link-type: ref

      .. image:: _static/phonon-dispersion.png
         :width: 100%

   .. grid-item-card:: Free energy analysis
      :link: free_energy_tutorial
      :link-type: ref

      .. image:: _static/phase-diagram.png
         :width: 100%

The following snippet illustrates how a :doc:`CPUNEP calculator <reference/calculators>` instance can be created given a NEP potential file, and how it can be used to predict the potential energy, forces, and stress for a structure. ::

    from ase.io import read
    from ase.build import bulk
    from calorine.calculators import CPUNEP
    
    structure = bulk('PbTe', crystalstructure='rocksalt', a=6.7)
    calc = CPUNEP('nep-PbTe.txt')
    structure.calc = calc

    print('Energy (eV):', structure.get_potential_energy())
    print('Forces (eV/Å):\n', structure.get_forces())
    print('Stress (eV/Å^3):\n', structure.get_stress())

Information on how to install :program:`calorine` as well as a large number of tutorials can be found in the :ref:`get started section <get_started>`.
A detailed function reference is provided in the :ref:`reference section <reference>`.

.. note::
   
   Please consult the credits page for information on how to cite :program:`calorine` if you use it in your publications or derived packages.
   :program:`calorine` and its development are hosted on `gitlab <https://gitlab.com/materials-modeling/calorine>`_.

.. toctree::
   :hidden:

   get_started/index
   reference/index
   credits
   genindex
