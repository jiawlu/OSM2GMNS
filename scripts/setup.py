import setuptools

try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        modules_needed = [i.strip() for i in f.readlines()]
except Exception:
    modules_needed = []

with open("README.rst", "r", encoding="utf-8") as f:
    _long_description = f.read()

setuptools.setup(
    name='osm2gmns',
    version='1.0.0dev0',
    author='Jiawei Lu, Xuesong Zhou',
    author_email='jiaweil9@asu.edu, xzhou74@asu.edu',
    url='https://github.com/jiawlu/OSM2GMNS',
    description="convert map data from OpenStreetMap to network files in GMNS format",
    long_description=_long_description,
    long_description_content_type="text/x-rst",
    license='GPLv3+',
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    classifiers=['License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.10',
                 'Programming Language :: Python :: 3.11',
                 'Programming Language :: Python :: 3.12'
                 ],
    install_requires=modules_needed,
)
