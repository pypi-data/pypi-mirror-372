============
Installation
============

We recommend the conda_ package manager and the Anaconda_ or Miniconda_
distributions for easy cross platform installation.

.. _conda: http://conda.pydata.org/
.. _Anaconda: http://docs.continuum.io/anaconda/
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html

Once Anaconda (or Miniconda) is installed type::

   $ conda install -c conda-forge pydy

Also, a simple way to install all of the optional dependencies is to install
the ``pydy-optional`` metapackage using conda::

   $ conda install -c conda-forge pydy-optional

Note that ``pydy-optional`` currently enforces the use of Jupyter 4.0, so you
may not want to install into your root environment. Create a new environment
for working with PyDy examples that use the embedded Jupyter visualizations::

   $ conda create -n pydy -c conda-forge pydy-optional
   $ conda activate pydy
   (pydy)$ python -c "import pydy; print(pydy.__version__)"

Other installation options
--------------------------

If you have the pip package manager installed you can type::

   $ pip install pydy

Installing from source is also supported. The latest stable version of the
package can be downloaded from PyPi\ [#]_::

   $ wget https://pypi.python.org/packages/source/p/pydy/pydy-X.X.X.tar.gz

.. [#] Change ``X.X.X`` to the latest version number.

and extracted and installed\ [#]_::

   $ tar -zxvf pydy-X.X.X.tar.gz
   $ cd pydy-X.X.X
   $ python setup.py install

.. [#] For system wide installs you may need root permissions (perhaps prepend
   commands with ``sudo``).

Dependencies
------------

PyDy has hard dependencies on the following software\ [#]_:

.. [#] We only test PyDy with these minimum dependencies; these module versions
       are provided in the Ubuntu 20.04 packages. Previous versions may work.

- Python >= 3.9
- setuptools >= 44.1.1
- NumPy_ >= 1.21.5
- SciPy_ >= 1.8.0
- SymPy_ >= 1.9
- PyWin32 >= 303 (Windows Only)

PyDy has optional dependencies for extended code generation on:

- Cython_ >= 0.29.28
- Theano_ >= 1.0.5

and animated visualizations with ``Scene.display_jupyter()`` on:

- `Jupyter Notebook`_ >= 6.0.0 or `Jupyter Lab` >= 1.0.0
- ipywidgets_ >= 6.0.0
- pythreejs_ >= 2.1.1

or interactive animated visualizations with ``Scene.display_ipython()`` on:

- 4.0.0 <= `Jupyter Notebook`_ < 5.0.0
- 4.0.0 <= ipywidgets_ < 5.0.0

.. _Cython: http://cython.org/
.. _Theano: http://deeplearning.net/software/theano/
.. _Jupyter Notebook: https://jupyter-notebook.readthedocs.io
.. _Jupyter Lab: https://jupyterlab.readthedocs.io

The examples may require these dependencies:

- matplotlib_ >= 3.5.1
- version_information_

.. _version_information: https://pypi.python.org/pypi/version_information

