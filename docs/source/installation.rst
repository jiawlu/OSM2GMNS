============
Installation
============

You can install the latest release of osm2gmns at `PyPI`_ via `pip`_:

.. code-block:: bash

    pip install osm2gmns

After running the command above, the osm2gmns package along with three required dependency packages
(`Shapely`_, `osmium`_, and `numpy`_) will be installed to your computer (if they have not 
been installed yet).

Potential Issues
========================

If you install osm2gmns in a conda environment, you may get an error message: "OSError: [WinError 126]
The specified module could not be found" when importing osm2gmns. To resolve this issue, you need to uninstall
the `Shapely`_ package first, and reinstall it manually using the command below.

.. code-block:: bash

    conda install shapely

Windows users may get an error message when installing osm2gmns with Python version > 3.8. This is caused
by one of the dependency packages of osm2gmns, `osmium`_. The highest Python version that osmium supports 
is py3.8 on Windows. As a result, it is recommended that Windows users create a virtual environment with
Python version <= 3.8 for using osm2gmns. MacOS and Linux users are not affected by this issue.

.. _`PyPI`: https://pypi.org/project/osm2gmns
.. _`pip`: https://packaging.python.org/key_projects/#pip
.. _`Shapely`: https://github.com/Toblerity/Shapely
.. _`osmium`: https://github.com/osmcode/osmium-tool
.. _`numpy`: https://github.com/numpy/numpy