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
Classes and functions for mapping IDL variables and subroutines to Python ones
"""


import util


################################################################################
#
# Extra code handling
#
################################################################################


_extracode = []

def add_extra_code(code):
   if not code:  return
   if isinstance(code, basestring):
      code = [code]
   for item in code:
      item = item.strip()
      if item not in _extracode:
         _extracode.append(item)

def get_extra_code():
   return '\n\n'.join(_extracode)

def clear_extra_code():
   global _extracode
   _extracode  = []


################################################################################
#
# Mapping base classes
#
################################################################################


class Error(Exception):
   "A runtime mapping error"
   pass


class Mapping(object):
   "Base class for all mappings"
   def pyname(self):
      if self._pyname:
         return self._pyname
      return util.pyname(self.name)



################################################################################
#
# Variable maps
#
################################################################################


_variables = {}

class VariableMapping(Mapping):
   def __init__(self, name, pyname=None, extracode=None, readonly=False):
      self.name = name
      keyname = name.upper()

      old_map = _variables.get(keyname)
      if old_map and old_map.readonly:
         raise Error("a read-only mapping for variable '%s' already exists",
	             self.name)

      self._pyname = pyname
      self.extracode = extracode
      self.readonly = readonly

      _variables[keyname] = self

   def pyname(self):
      add_extra_code(self.extracode)
      return Mapping.pyname(self)


def map_var(name, pycode=None, extracode=None, readonly=False):
   return VariableMapping(name, pycode, extracode, readonly)


def get_variable_map(name):
   return _variables.get(name.upper())


################################################################################
#
# Subroutine maps
#
################################################################################


_subroutines = {}

class SubroutineMapping(Mapping):
   def __init__(self, name, pyname=None, function=False,
                inpars=(), outpars=(), noptional=0, inkeys=(), outkeys=(),
		callfunc=None, extracode=None, readonly=False):

      self.name = name
      keyname = name.upper()

      # Check for an existing read-only map
      old_map = _subroutines.get(keyname)
      if old_map and old_map.readonly:
         raise Error("a read-only mapping for subroutine '%s' already exists",
	             self.name)

      # Store input and output parameters
      self.inpars = tuple(inpars)
      if outpars and function:
         raise Error('functions cannot have output parameters')
      self.outpars = tuple(outpars)

      # Store number of parameters and validate parameter list
      pars = list(self.inpars)
      pars += [ p for p in self.outpars if p not in self.inpars ]
      pars.sort()
      self.npars = len(pars)
      if pars != range(1, self.npars+1):
         raise Error('incomplete or invalid parameter list: %s' % pars)

      # Store number of optional parameters, ensuring it's >=0
      noptional = int(noptional)
      if noptional < 0:  noptional = 0
      self.noptional = noptional

      # Store input and output keywords
      self.inkeys = tuple([ k.upper() for k in inkeys ])
      if outkeys and function:
         raise Error('functions cannot have output keywords')
      self.outkeys = tuple([ k.upper() for k in outkeys ])

      # Store list of all keywords
      allkeys = list(self.inkeys)
      allkeys += [ k for k in self.outkeys if k not in self.inkeys ]
      self.allkeys = tuple(allkeys)

      # Store everything else
      self._pyname = pyname
      self.function = function
      self.callfunc = callfunc
      self.extracode = extracode
      self.readonly = readonly

      # Register the mapping
      _subroutines[keyname] = self

   def pydef(self, pars=(), keys=()):
      # Store parameter and keyword lists, converting names with pyname()
      pars = tuple([ util.pyname(p) for p in pars ])
      keys = tuple([ (util.pyname(lname), util.pyname(rname)) for
                     (lname, rname) in keys ])

      # Verify number of parameters
      if len(pars) != self.npars:
         raise Error("subroutine '%s' has %d parameters (defined with %d)" %
		     (self.name, self.npars, len(pars)))

      # Verify that all needed keywords were supplied
      keys_expected = list(self.allkeys)
      keys_expected.sort()
      keys_got = [ k[0].upper() for k in keys ]
      keys_got.sort()
      if keys_got != keys_expected:
         raise Error(("keywords for subroutine '%s' are %s " +
	              "(defined with keywords %s)") %
		     (self.name, keys_expected, keys_got))

      nrequired = self.npars - self.noptional
      in_required = [ pars[i] for i in range(nrequired) if i+1 in self.inpars ]
      in_optional = ([ pars[i] for i in range(nrequired, self.npars)
                       if (i+1 in self.inpars) or (i+1 in self.outpars) ])
      params = ', '.join(in_required + [ p + '=None' for p in in_optional ] +
			 [ k[0] + '=None' for k in keys ])

      header = 'def %s(%s):' % (self.pyname(), params)

      body = 'n_params = %d' % self.npars
      if in_optional:
	 body += ' - [%s].count(None)' % ', '.join(in_optional)

      out = [ pars[i] for i in range(nrequired) if i+1 in self.outpars ]
      out_only = ([ pars[i] for i in range(nrequired) if (i+1 in self.outpars)
                    and (i+1 not in self.inpars) ])
      for par in out_only:
         body += '\n%s = None' % par

      for k in keys:
         if k[0] != k[1]:
            body += '\n%s = %s' % (k[1], k[0])

      opt_out = ([ pars[i] for i in range(nrequired, self.npars)
                   if i+1 in self.outpars ])
      opt_out += [ k[0] for k in keys if k[0].upper() in self.outkeys ]
      if opt_out:
         body += '\n_optout = (%s' % ', '.join(opt_out)
         if len(opt_out) == 1:  body += ','
	 body += ')'

      if not self.function:
         body += '\ndef _ret():'
         if (not out) and (not opt_out):
            body += '  return None'
         elif out and (not opt_out):
	    if len(out) == 1:
	       body += '  return %s' % out[0]
	    else:
	       body += '  return (%s)' % ', '.join(out)
         else:
	    if out:
	       retbody = '_rv = [%s]\n_rv += ' % ', '.join(out)
	    else:
	       retbody = '_rv = '
	    retbody += (('[_o[1] for _o in zip(_optout,[%s]) if _o[0] is ' +
	                 'not None]') % ','.join(opt_out))
	    retbody += '\nreturn tuple(_rv)'
	    body += '\n' + util.pyindent(retbody)
         
      body += '\n'

      add_extra_code(self.extracode)

      return (header, body)

   def pycall(self, pars=(), keys=()):
      pars = tuple(pars)
      keys = tuple(keys)

      npars = len(pars)
      nrequired = self.npars - self.noptional
      if npars > self.npars:
         raise Error(("subroutine '%s' takes at most %d parameters " +
	              "(called with %d)") % (self.name, self.npars, npars))
      if npars < nrequired:
         raise Error(("subroutine '%s' requires at least %d " +
	              "parameters (called with %d)") %
		     (self.name, nrequired, npars))

      input  = [ pars[i] for i in range(npars) if i+1 in self.inpars ]
      output = [ pars[i] for i in range(npars) if i+1 in self.outpars ]

      keydict = {}

      for (name, value) in keys:
	 name = name.lower()
         matches = [ k for k in self.allkeys if k.startswith(name) ]
	 if len(matches) == 0:
	    raise Error("'%s' is not a valid keyword for subroutine '%s'" %
	                (name, self.name))
	 if len(matches) > 1:
	    raise Error(("identifier '%s' matches multiple keywords " +
	                 "for subroutine '%s': %s") %
			(name, self.name, matches))
         name = matches[0]
	 keydict[name] = value
	 if name in self.inkeys:
	    input.append('%s=%s' % (name, value))

      for name in self.outkeys:
         if name in keydict:
	    if name not in self.inkeys:
	       input.append('%s=True' % name)
	    output.append(keydict[name])

      add_extra_code(self.extracode)

      if self.callfunc:
         return self.callfunc(input, output)

      input  = ', '.join(input)
      if output:
         output = ', '.join(output) + ' = '
      else:
         output = ''

      return '%s%s(%s)' % (output, self.pyname(), input)


def map_pro(name, pyname=None, inpars=(), outpars=(), noptional=0,
            inkeys=(), outkeys=(), callfunc=None, extracode=None,
	    readonly=False):
   return SubroutineMapping(name, pyname=pyname, function=False,
                            inpars=inpars, outpars=outpars, noptional=noptional,
                            inkeys=inkeys, outkeys=outkeys, callfunc=callfunc,
			    extracode=extracode, readonly=readonly)


def map_func(name, pyname=None, pars=(), noptional=0, keys=(), callfunc=None,
             extracode=None, readonly=False):
   return SubroutineMapping(name, pyname=pyname, function=True, inpars=pars,
                            noptional=noptional, inkeys=keys, callfunc=callfunc,
			    extracode=extracode, readonly=readonly)


def get_subroutine_map(name):
   return _subroutines.get(name.upper())


#
# Read-only builtin mappings (these are needed by the function-mapping
# mechanism itself)
#

map_func('N_PARAMS', callfunc=(lambda i,o: 'n_params'), readonly=True)
map_func('KEYWORD_SET', pars=[1],
         callfunc=(lambda i,o: '(%s is not None)' % i[0]), readonly=True)


