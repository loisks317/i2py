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

import fmap
from builtins import builtins

subroutines = {}.fromkeys(builtins)

def add_sub(name):
   name = name.upper()
   if name not in subroutines:
      subroutines[name] = None

def del_sub(name):
   name = name.upper()
   if name in subroutines:
      del subroutines[name]

def map_proc(name, pyname=None, inpars=(), outpars=(), noptional=0,
             inkeys=(), outkeys=(), callfunc=None, extracode=None):
   map = fmap.SubroutineMapping(name, pyname=pyname, function=False,
                           inpars=inpars, outpars=outpars, noptional=noptional,
                           inkeys=inkeys, outkeys=outkeys, callfunc=callfunc,
			   extracode=extracode)
   subroutines[map.name] = map

def map_func(name, pyname=None, pars=(), noptional=0, keys=(), callfunc=None,
             extracode=None):
   map = fmap.SubroutineMapping(name, pyname=pyname, function=True, inpars=pars,
                           noptional=noptional, inkeys=keys, callfunc=callfunc,
			   extracode=extracode)
   subroutines[map.name] = map

map_func('N_PARAMS', callfunc=(lambda i,o: 'n_params'))
map_func('KEYWORD_SET', pars=[1],
         callfunc=(lambda i,o: '(%s is not None)' % i[0]))

