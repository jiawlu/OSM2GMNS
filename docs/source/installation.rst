============
Installation
============

You can install the latest release of osm2gmns at `PyPI`_ via `pip`_:

.. code-block:: bash

    pip install osm2gmns

After running the command above, the osm2gmns package along with two necessary dependency packages
(`Shapely`_ and `pandas`_) will also be installed to your computer (if they have not been installed yet).

Note that the GDAL library must be installed if you need to use function ``getNetFromPBFFile()``.
For machines running windows, users can download the proper whl file from the `website`_, 
then install it using ``pip install`` command.

.. code-block:: bash

    pip install GDAL-x.x.x-xxx.whl

.. _`PyPI`: https://pypi.org/project/pydriosm/
.. _`pip`: https://packaging.python.org/key_projects/#pip
.. _`Shapely`: https://github.com/Toblerity/Shapely
.. _`pandas`: https://github.com/pandas-dev/pandas
.. _`website`: https://packaging.python.org/key_projects/#pip