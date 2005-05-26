# 
#  Copyright (C) 2005 Christopher J. Stawarz <chris@pseudogreen.org>
# 
#  This file is part of i2py.
# 
#  i2py is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# 
#  i2py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with i2py; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
This file defines mappings for some builtin IDL functions and procedures.  This
will need to be expanded quite a bit before the package is ready for production
use.
"""

from fmap import map_proc, map_func

# These are essential to the function mapping mechanism and can't be changed!
map_func('N_PARAMS', callfunc=(lambda i,o: 'n_params'))
map_func('KEYWORD_SET', pars=[1],
         callfunc=(lambda i,o: '(%s is not None)' % i[0]))

map_proc('ON_ERROR', inpars=[1],
         callfunc=(lambda i,o: '# ON_ERROR, %s' % i[0]))
map_proc('PRINT', inpars=range(1,101), noptional=99, inkeys=['FORMAT'],
         callfunc=(lambda i,o: 'print ' + ', '.join(i)))

def arrgen(typename):
   return (lambda i,o: 'zeros([%s], %s)' %
           (', '.join([ i[n] for n in xrange(len(i)-1, -1, -1) ]), typename))

def typeconv(typename):
   return (lambda i,o: 'array(%s, copy=False).astype(%s)' % (i[0], typename))

map_func('DOUBLE', pars=[1], callfunc=typeconv('Float64'))
map_func('FIX', pars=[1], callfunc=typeconv('Int32'))
map_func('FLOAT', pars=[1], callfunc=typeconv('Float32'))
map_func('FLTARR', pars=range(1,9), noptional=7, callfunc=arrgen('Float32'))
map_func('LONG', pars=[1], callfunc=typeconv('Int32'))
map_func('MIN', pars=[1],
         callfunc=(lambda i,o: 'array(%s, copy=False).min()' % i[0]))
map_func('N_ELEMENTS', pars=[1],
         callfunc=(lambda i,o: 'array(%s, copy=False).size()' % i[0]))
map_func('REPLICATE', pars=range(1,10), noptional=7,
         callfunc=(lambda i,o: '(%s)*ones([%s])' % (i[0],
	           ', '.join([ i[n] for n in xrange(len(i)-1, 0, -1) ]))))

# This would be nicer!
#map_func('WHERE', pars=[1,2], noptional=1,
#         callfunc=(lambda i,o: 'where(ravel(%s))[0]' % i[0]))

def callwhere(p, k):
   s = 'idlwhere(%s' % p[0]
   if len(p) > 1:
      s += ", '%s'" % p[1]
   return s + ')'

map_func('WHERE', pars=[1,2], noptional=1, callfunc=callwhere, extracode=(
"""import sys
def idlwhere(arr, cnt=None):
   rv = where(ravel(arr))[0]
   if cnt:
      sys._getframe(1).f_locals[cnt] = rv.size()
   return rv"""))

