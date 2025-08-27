
from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

#get version
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(
    name='pikobs',
    version=version,
    url='https://gitlab.science.gc.ca/dlo001/pikobs',
    license='GPL-3.0-or-later',
    author='David Lobon',
    author_email='dhlobon@gmail.com',
    description="pikobs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    package_data={
        'pikobs': ['extension/*.so'],
    },
    python_requires='>=3.8', 
    install_requires=['matplotlib','numpy >= 1.17.0','geopandas==0.10.0', 'earthpy==0.9.4', 'shapely==1.7.0',  'cartopy', 'h5py','packaging', 'pygrib', 'domutils' ,'dask==2022.9.1', 'scipy', 'pytz'],
)
