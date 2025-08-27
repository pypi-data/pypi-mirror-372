.. index::
   single: Function reference; NEP interface

NEP interface
=============

Training IO
-----------
:program:`calorine` provides a number of functions for preparing input files for training NEP models, including in particular the :func:`setup_training <calorine.nep.setup_training>` function.
There are also several functions for analyzing the training process, including, e.g., the :func:`read_loss <calorine.nep.read_loss>`, :func:`read_structures <calorine.nep.read_structures>`, and :func:`get_parity_data <calorine.nep.get_parity_data>` functions.

.. autofunction:: calorine.nep.get_parity_data
.. autofunction:: calorine.nep.read_loss
.. autofunction:: calorine.nep.read_nepfile
.. autofunction:: calorine.nep.read_structures
.. autofunction:: calorine.nep.setup_training
.. autofunction:: calorine.nep.write_nepfile
.. autofunction:: calorine.nep.write_structures

Evaluating models
-----------------
TNEP models allow one to represent tensorial properties such as dipole moment, susceptibility, or polarizability.
To test and analyze these models :program:`calorine` provides several specialized functions, which can also be used to implement extended Hamiltonians.

.. autofunction:: calorine.nep.get_dipole
.. autofunction:: calorine.nep.get_dipole_gradient
.. autofunction:: calorine.nep.get_polarizability
.. autofunction:: calorine.nep.get_polarizability_gradient
.. autofunction:: calorine.nep.get_potential_forces_and_virials

Inspecting NEP models
---------------------
Once a model has been trained it can be analyzed in more detail.
To this end, there are functions for accessing the descriptors, the latent space, or to load the entire model.
The latter function (:func:`read_model <calorine.nep.read_model>`) returns a :class:`Model <calorine.nep.model.Model>` object, which contains the entire information about this model.
It is thereby possible not only to query but to manipulate the model and write the result back to disk.

.. autofunction:: calorine.nep.get_descriptors
.. autofunction:: calorine.nep.get_latent_space
.. autofunction:: calorine.nep.read_model

NEP model class
---------------
.. autoclass:: calorine.nep.model.Model
   :members:
