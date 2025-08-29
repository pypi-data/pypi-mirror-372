from setuptools import setup, find_packages

PACKAGE_NAME="sgclimaapiclient"
exec(open("{}/version.py".format(PACKAGE_NAME)).read())

setup(name=PACKAGE_NAME,
      version=__version__,
      description='Module to use sgclimaapi from python',
      url='',
      author='Indoorclima',
      author_email='',
      license='',
      packages=find_packages(),
      # entry_points={'console_scripts': [f'{PACKAGE_NAME} = {PACKAGE_NAME}.launcher:launcher']},
      # package_data={PACKAGE_NAME: ['apps/prv_front_tools/template_coords_2.csv']},
      zip_safe=False,
      install_requires=["setuptools>=45.2.0",
                        "pandas>=1.2.0",
                        "numpy>=1.19.5",
                        "requests>=2.21.0",
                        "azure-storage-blob>=12.14.1",
                        "aiohttp>=3.5.1",
                        "fastparquet>=0.8.3",
                        #"pytest>= 7.0.0",
                        "pyarrow>=21.0.0"
			])