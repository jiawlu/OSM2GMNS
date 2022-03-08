============
Installation
============

You can install the latest release of osm2gmns at `PyPI`_ via `pip`_:

.. code-block:: bash

    pip install osm2gmns

By running the command above, the osm2gmns package along with three required dependency packages
(`Shapely`_, `osmium`_, and `numpy`_) will be installed to your computer (if they have not 
been installed yet).

Potential Issues
========================

- Shapely

If you install osm2gmns in a conda environment, you may get an error message: "OSError: [WinError 126]
The specified module could not be found" when importing osm2gmns. To resolve this issue, you need to uninstall
the `Shapely`_ package first, and reinstall it manually using the command below.

.. code-block:: bash

    conda install shapely

- osmium
  
Windows users may get an error message related to `osmium`_ (one of the dependency packages of osm2gmns) 
when installing or using osm2gmns with Python version > 3.8. The reason is the highest Python version
that osmium supports on PyPI is Py3.8 for Windows.

Affected users can download binary wheels of osmium from `our repository`_ or `osmium github homepage`_ and use pip to install the wheel file that matches your Python version.


.. _`PyPI`: https://pypi.org/project/osm2gmns
.. _`pip`: https://packaging.python.org/key_projects/#pip
.. _`Shapely`: https://github.com/Toblerity/Shapely
.. _`osmium`: https://github.com/osmcode/pyosmium
.. _`numpy`: https://github.com/numpy/numpy
.. _`our repository`: https://github.com/jiawlu/OSM2GMNS/tree/master/dependencies
.. _`osmium github homepage`: https://github.com/osmcode/pyosmium/actions
