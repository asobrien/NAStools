from distutils.core import setup
setup(name='NAStools',
      version='0.1.2',
      description='Tools for working with ICARRT and NASA Ames data file formats',
      author="Anthony O'Brien",
      author_email='anthonyo@princeton.edu',
      url='https://github.com/asobrien/NAStools',
      # packages=['distutils', 'distutils.command'],
      license = 'Public Domain',
      packages = ['nastools'],
      package_dir = {'nastools': 'src/nastools'},
      requires = ['numpy (>=1.6.1)', 
                  'pandas (>=0.10.1)'
                  ],
      classifiers = ["Development Status :: 3 - Alpha",
                     "Environment :: Console",
                     "Intended Audience :: Science/Research",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2",
                     "Topic :: Scientific/Engineering"
                    ],
      long_description = 
      """
      **nastools** is a Python package that provides a lean, simple interface to import 
      and work with NASA scientific file formats. 
      
      nastools works with:
      
        - `ICARRT Data Format <http://www-air.larc.nasa.gov/missions/etc/IcarttDataFormat.htm>`_
        - `NASA Ames Format for Data Exchange <http://badc.nerc.ac.uk/help/formats/NASA-Ames/>`_

        
      See the project `homepage <https://github.com/asobrien/NAStools>`_ for more information.
      
      Issues/bugs/feature requests/etc can be `reported here <https://github.com/asobrien/NAStools/issues>`_.
      
      """
     )