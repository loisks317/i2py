#!/usr/bin/env python

#
# Setup script for i2py
#

from distutils.core import setup
import i2py

# Grab the description from the module's doc string
desc = i2py.__doc__.split('\n\n')

setup(name='i2py',
      version=i2py.__version__,
      author='Christopher J. Stawarz',
      author_email='chris@pseudogreen.org',
      url='http://software.pseudogreen.org/i2py/',
      license='http://www.fsf.org/copyleft/gpl.html',
      platforms=['any'],
      description=desc[0].strip(),
      long_description='\n\n'.join(desc[1:]),
      packages=['i2py'],
      scripts=['idl2python'],
     )

