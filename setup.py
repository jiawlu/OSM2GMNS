import setuptools

setuptools.setup(
    name='osm2gmns',
    version='0.7.4',
    author='Jiawei Lu, Xuesong Zhou',
    author_email='jiaweil9@asu.edu, xzhou74@asu.edu',
    url='https://github.com/jiawlu/OSM2GMNS',
    description='convert map data from OpenStreetMap to network files in GMNS format',
    long_description=open('README_pypi.rst').read(),
    license='GPLv3+',
    packages=setuptools.find_packages(),
    python_requires=">=3.6.0",
    install_requires=['shapely >= 2.0.1', 'osmium >= 3.1.3', 'numpy'],
    classifiers=['License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 3']
)
