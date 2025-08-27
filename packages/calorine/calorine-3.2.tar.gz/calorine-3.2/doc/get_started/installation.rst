.. _installation:

Installation
============

.. note::

    Here, we only describe the installation of :program:`calorine`.
    If you want to install :program:`GPUMD`, please consult the `GPUMD documentation <https://gpumd.org/>`_


Installation from PyPI
----------------------

Stable versions of :program:`calorine` are provided via `PyPI <https://pypi.org/project/calorine/>`_.
This allows one to install :program:`calorine` using `pip` via::

    pip install calorine --user

The `PyPI` package is provided as a `source distribution <https://packaging.python.org/glossary/#term-Source-Distribution-or-sdist>`_.
As a result, the C++ code has to be compiled as part of the installation, which requires a C++11 compliant compiler to be installed on your system, e.g., `GCC 4.8.1 and above <https://gcc.gnu.org/projects/cxx-status.html#cxx11>`_ or `Clang 3.3 and above <https://clang.llvm.org/cxx_status.html>`_.


Installing the development version
----------------------------------

If installation via pip fails or if you want to use the most recent (development) version you can run::

    pip install --user git+https://gitlab.com/materials-modeling/calorine.git
