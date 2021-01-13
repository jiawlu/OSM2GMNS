============
Installation
============

You can install the latest release of osm2gmns at `PyPI`_ via `pip`_:

.. code-block:: bash

    pip install osm2gmns

After running the command above, the osm2gmns package along with three necessary dependency packages
(`Shapely`_, `pandas`_ and `protobuf`_) will be installed to your computer (if they have not 
been installed yet).

If you install osm2gmns in a conda environment, you may get an error message: "OSError: [WinError 126]
The specified module could not be found" when importing osm2gmns. To resolve this issue, you need to uninstall
the `Shapely`_ package first, and reinstall it manually using the command below.

.. code-block:: bash

    conda install shapely


.. _`PyPI`: https://pypi.org/project/pydriosm/
.. _`pip`: https://packaging.python.org/key_projects/#pip
.. _`Shapely`: https://github.com/Toblerity/Shapely
.. _`pandas`: https://github.com/pandas-dev/pandas
.. _`protobuf`: https://developers.google.com/protocol-buffers