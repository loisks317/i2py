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

idltab = '   '
pytab  = '   '

def indent(obj, ntabs=1, tab=None):
   if not tab:  tab = idltab
   pad = ntabs * tab
   return pad + str(obj).replace('\n', '\n' + pad).rstrip(tab)

def pycode(obj):
   if hasattr(obj, 'pycode'):
      return obj.pycode()
   return str(obj)

def pyindent(obj, ntabs=1, tab=None):
   if not tab:  tab = pytab
   pad = ntabs * tab
   return pad + pycode(obj).replace('\n', '\n' + pad).rstrip(tab)

def pycomment(obj):
   return pyindent(obj, tab='# ')

