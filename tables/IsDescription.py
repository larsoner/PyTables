########################################################################
#
#       License:        BSD
#       Created:        September 21, 2002
#       Author:  Francesc Altet - faltet@carabos.com
#
#       $Source: /home/ivan/_/programari/pytables/svn/cvs/pytables/pytables/tables/IsDescription.py,v $
#       $Id: IsDescription.py,v 1.39 2004/12/18 11:15:17 falted Exp $
#
########################################################################

"""Classes and metaclasses for defining user data columns for Table objects.

Classes:

    metaIsDescription
    IsDescription

Functions:

Misc variables:

    __version__

"""

__version__ = "$Revision: 1.39 $"


import warnings
import struct
import types
import sys

import numarray as NA
import numarray.records as records
from utils import checkNameValidity

# Map between the numarray types and struct datatypes
tostructfmt = {NA.Int8:'b', NA.UInt8:'B',
               NA.Int16:'h', NA.UInt16:'H',
               NA.Int32:'i', NA.UInt32:'I',
               NA.Int64:'q', NA.UInt64:'Q',
               NA.Float32:'f', NA.Float64:'d',
               NA.Complex32:'F', NA.Complex64:'D', # Added top support complex
               NA.Bool:'c', records.CharType:'s', 
               }

# translation table from the Struct data types to numarray types
fromstructfmt = {'b':NA.Int8, 'B':NA.UInt8,
                 'h':NA.Int16, 'H':NA.UInt16,
                 'i':NA.Int32, 'I':NA.UInt32,
                 'q':NA.Int64, 'Q':NA.UInt64,
                 'f':NA.Float32, 'd':NA.Float64,
                 'F':NA.Complex32, 'D':NA.Complex64,# Added top support complex
                 'c':NA.Bool, 's':records.CharType,
                 }

class Col:
    """ Define a general column that supports all numarray data types"""
    def __init__(self, dtype="Float64", shape=1, dflt=None, pos=None,
                 indexed=0):

        self.pos = pos
        self.indexed = indexed

        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported '%s'" % `shape`

        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            # HDF5 does not support ranks greater than 32
            assert len(shape) <= 32, \
               "Shapes with rank > 32 are not supported '%s'" % `shape`
            self.shape = tuple(shape)
        else:
            raise ValueError, "Illegal shape object: '%s'" % `shape`

        self.dflt = dflt

        if dtype in NA.typeDict:
            self.type = NA.typeDict[dtype]
            self.recarrtype = records.revfmt[self.type]
            self.itemsize = self.type.bytes
            if self.indexed and (dtype == NA.Complex32 or
                                 dtype == NA.Complex64):
                raise TypeError, "'%s' do not support indexation" % repr(dtype)
        elif dtype == "CharType" or isinstance(dtype, records.Char):
            # Special case for Strings
            self.type = records.CharType
            if type(shape) in [types.IntType, types.LongType]:
                self.shape = 1
                self.itemsize = shape
            else:
                shape = list(self.shape)
                self.itemsize = shape.pop()
                if shape == ():
                    self.shape = 1
                elif len(shape) == 1:
                    #self.shape = shape[0]
                    # This is better for Atoms
                    self.shape = (shape[0],)
                else:
                    self.shape = tuple(shape)
                    
            self.recarrtype = records.revfmt[self.type]
        else:
            raise TypeError, "Illegal type: %s" % `dtype`

        self.rectype = tostructfmt[self.type]

    def __repr__(self):
        if self.type == "CharType" or isinstance(self.type, records.Char):
            if self.shape == 1:
                shape = [self.itemsize]
            else:
                shape = list(self.shape)
                shape.append(self.itemsize)
            shape = tuple(shape)
        else:
            shape = self.shape

        out = "Col(dtype='" +  str(self.type) + "'" + \
              ", shape=" +  str(shape) + \
              ", dflt=" + str(self.dflt) + \
              ", pos=" + str(self.pos) + \
              ", indexed=" + str(self.indexed) + \
              ")"
        return out

class BoolCol(Col):
    """ Define a boolean column """
    
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):

        self.pos = pos
        self.indexed = indexed

        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported '%s'" % `shape`

        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            self.shape = tuple(shape)
        else: raise ValueError, "Illegal shape %s" % `shape`

        self.dflt = dflt

        self.type = NA.typeDict["Bool"]
        self.itemsize = 1
        self.recarrtype = records.revfmt[self.type]
        self.rectype = tostructfmt[self.type]

    
class StringCol(Col):
    """ Define a string column """
    
    def __init__(self, length=None, dflt=None, shape=1, pos=None,
                 indexed=0):

        self.pos = pos
        self.indexed = indexed

        assert isinstance(dflt, types.StringTypes) or dflt == None, \
               "Invalid default value: '%s'" % dflt
        
        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported: '%s'" % `shape`

        # Deduce the length from the default value if it is not specified!
        if length == None and dflt:
            length = len(dflt)
        if not length:
            raise RuntimeError, \
"""You must specify at least a length or a default value where this length
  can be infered from."""
        
        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            self.shape = tuple(shape)
        else: raise ValueError, "Illegal shape %s" % `shape`

        self.dflt = dflt

        self.type = records.CharType
        self.itemsize = length
        self.recarrtype = records.revfmt[self.type]
        self.rectype = tostructfmt[self.type]

    
class IntCol(Col):
    """ Define an integer column """
    def __init__(self, dflt=0, shape=1, itemsize=4, sign=1, pos=None,
                 indexed=0):

        self.pos = pos
        self.indexed = indexed

        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported '%s':" % `shape`

        assert itemsize in [1, 2, 4, 8], \
               "Integer itemsizes different from 1,2,4 or 8 are not supported"
        
        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            self.shape = tuple(shape)
        else: raise ValueError, "Illegal shape %s" % `shape`

        self.dflt = dflt

        self.itemsize = itemsize
        if itemsize == 1:
            if sign:
                self.type = NA.typeDict["Int8"]
            else:
                self.type = NA.typeDict["UInt8"]
        elif itemsize == 2:
            if sign:
                self.type = NA.typeDict["Int16"]
            else:
                self.type = NA.typeDict["UInt16"]
        elif itemsize == 4:
            if sign:
                self.type = NA.typeDict["Int32"]
            else:
                self.type = NA.typeDict["UInt32"]
        elif itemsize == 8:
            if sign:
                self.type = NA.typeDict["Int64"]
            else:
                self.type = NA.typeDict["UInt64"]
                
        self.recarrtype = records.revfmt[self.type]
        self.rectype = tostructfmt[self.type]

class Int8Col(IntCol):
    "Description class for a signed integer of 8 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt, itemsize=1, shape=shape, sign=1,
                        pos=pos, indexed=indexed)
        
class UInt8Col(IntCol):
    "Description class for an unsigned integer of 8 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=1, shape=shape, sign=0,
                        pos=pos, indexed=indexed)
        
class Int16Col(IntCol):
    "Description class for a signed integer of 16 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=2, shape=shape, sign=1,
                        pos=pos, indexed=indexed)
        
class UInt16Col(IntCol):
    "Description class for an unsigned integer of 16 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=2, shape=shape, sign=0,
                        pos=pos, indexed=indexed)
        
class Int32Col(IntCol):
    "Description class for a signed integer of 32 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=4, shape=shape, sign=1,
                        pos=pos, indexed=indexed)
        
class UInt32Col(IntCol):
    "Description class for an unsigned integer of 32 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=4, shape=shape, sign=0,
                        pos=pos, indexed=indexed)
        
class Int64Col(IntCol):
    "Description class for a signed integer of 64 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=8, shape=shape, sign=1,
                        pos=pos, indexed=indexed)
        
class UInt64Col(IntCol):
    "Description class for an unsigned integer of 64 bits "
    def __init__(self, dflt=0, shape=1, pos=None, indexed=0):
        IntCol.__init__(self, dflt , itemsize=8, shape=shape, sign=0,
                        pos=pos, indexed=indexed)
        
class FloatCol(Col):
    """ Define a float column """
    def __init__(self, dflt=0.0, shape=1, itemsize=8, pos=None,
                 indexed=0):

        self.pos = pos
        self.indexed = indexed

        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported '%s'" % `shape`

        assert itemsize in [4,8], \
               "Float itemsizes different from 4 and 8 are not supported"
        
        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            self.shape = tuple(shape)
        else: raise ValueError, "Illegal shape %s" % `shape`

        self.dflt = dflt

        self.itemsize = itemsize
        if itemsize == 4:
            self.type = NA.typeDict["Float32"]
        elif itemsize == 8:
            self.type = NA.typeDict["Float64"]
                
        self.recarrtype = records.revfmt[self.type]
        self.rectype = tostructfmt[self.type]

class Float32Col(FloatCol):
    "Description class for a floating point of 32 bits "
    def __init__(self, dflt=0.0, shape=1, pos=None, indexed=0):
        FloatCol.__init__(self, dflt , shape=shape, itemsize=4,
                          pos=pos, indexed=indexed)
        
class Float64Col(FloatCol):
    "Description class for a floating point of 64 bits "
    def __init__(self, dflt=0.0, shape=1, pos=None, indexed=0):
        FloatCol.__init__(self, dflt , shape=shape, itemsize=8,
                          pos=pos, indexed=indexed)
        
class ComplexCol(Col):
    """ Define a complex column """
    def __init__(self, dflt=(0.0+0.0j), shape=1, itemsize=16, pos=None):

        self.pos = pos
        self.indexed = 0  # This attribuet is needed
        assert shape != None and shape != 0, \
               "None or zero-valued shapes are not supported '%s'" % `shape`

        assert itemsize in [8, 16], \
               "Copmplex itemsizes different from 8 and 16 are not supported"
        
        if type(shape) in [types.IntType, types.LongType]:
            if shape < 1:
                raise ValueError(
                    "Shape value must be greater than 0: %s" % (shape,))
            elif shape == 1:
                self.shape = shape
            else:
                # To prevent confusions between 2 and (2,):
                # the meaning is the same
                self.shape = (shape,)
        elif type(shape) in [types.ListType, types.TupleType]:
            self.shape = tuple(shape)
        else: raise ValueError, "Illegal shape %s" % `shape`

        self.dflt = dflt

        self.itemsize = itemsize
        if itemsize == 8:
            self.type = NA.typeDict["Complex32"]
        elif itemsize == 16:
            self.type = NA.typeDict["Complex64"]
                
        self.recarrtype = records.revfmt[self.type]
        self.rectype = tostructfmt[self.type]

class Complex32Col(ComplexCol):
    "Description class for a complex of simple precision "
    def __init__(self, dflt=(0.0+0.0j), shape=1, pos=None):
        ComplexCol.__init__(self, dflt, shape=shape, itemsize=8, pos=pos)
        
class Complex64Col(ComplexCol):
    "Description class for a complex of double precision "
    def __init__(self, dflt=(0.0+0.0j), shape=1, pos=None):
        ComplexCol.__init__(self, dflt , shape=shape, itemsize=16, pos=pos)


class Description(object):
    "Regular class to keep table description metadata"

    def __init__(self, classdict):

        self.classdict = classdict
        keys = classdict.keys()
        newdict = self.__dict__
        newdict["__names__"] = []
        newdict["__types__"] = {}
        newdict["__dflts__"] = {}
        newdict["_v_ColObjects"] = {}
        newdict["_v_shapes"] = {}
        newdict["_v_itemsizes"] = {}
        newdict["_v_fmt"] = ""
        # Check if we have any .pos position attribute
        for column in classdict.values():
            if hasattr(column, "pos") and column.pos:
                keys.sort(self.cmpkeys)
                break
        else:
            # No .pos was set
            # fall back to alphanumerical order
            keys.sort()
            
        recarrfmt = []
        if "__check_validity__" in keys:
            check_validity = classdict["__check_validity__"]
        else:
            check_validity = 1   # Default value for name validity check
        for k in keys:
            if (k.startswith('__') or k.startswith('_v_')):
                if k in newdict:
                    # special methods &c: copy to newdict, warn about conflicts
                    warnings.warn("Can't set attr %r in coldescr-class %r" % (
                        k, classname))
                else:
                    #print "Special variable!:", k
                    newdict[k] = classdict[k]
            else:
                # Class variables
                if check_validity:
                    # Check for key name validity
                    checkNameValidity(k)
                object = classdict[k]
                if not isinstance(object, Col):
                    raise TypeError, \
"""Passing an incorrect value to a table column.
  Please, make use of the Col(), or descendant, constructor to
  properly initialize columns. Expected a Col (or subclass) instance
  and got: "%s"

""" % object
                newdict['__names__'].append(k)
                newdict['_v_ColObjects'][k] = object
                newdict['__types__'][k] = object.type
                if hasattr(object, 'dflt') and not object.dflt is None:
                    newdict['__dflts__'][k] = object.dflt
                else:
                    newdict['__dflts__'][k] = self.testtype(object)

                # Special case for strings: "aN"
                if object.recarrtype == "a":
                    # This needs to be fixed when calcoffset will support
                    # the recarray format, for ex: "(1,3)f4,3i4,(2,)a5,i2"
                    if type(object.shape) in [types.IntType, types.LongType]:
                        # If shape is int type, it is always 1
                        shape = object.itemsize
                    else:
                        shape = list(object.shape)
                        shape.append(object.itemsize)
                        shape = tuple(shape)
                        
                    newdict['_v_fmt'] +=  str(shape) + object.rectype
                    newdict['_v_shapes'][k] = object.shape
                    newdict['_v_itemsizes'][k] = object.itemsize
                    recarrfmt.append(str(object.shape) + \
                                     object.recarrtype + str(object.itemsize))
                else:
                    newdict['_v_fmt'] += str(object.shape) + object.rectype
                    recarrfmt.append(str(object.shape) + object.recarrtype)
                    newdict['_v_shapes'][k] = object.shape
                    newdict['_v_itemsizes'][k] = object.itemsize

        # Set up the alignment
        if newdict.has_key('_v_align'):
            newdict['_v_fmt'] = newdict['_v_align'] + newdict['_v_fmt']
        else:
            newdict['_v_fmt'] = "=" + newdict['_v_fmt']  # Standard align
        # Assign the formats list to _v_recarrfmt
        newdict['_v_recarrfmt'] = recarrfmt
        # finally delegate the rest of the work to type.__new__
        return

    def __repr__(self):
        """ Gives a Table column representation
        """
        rep = [ '\"%s\": %r' %  \
                (k, self._v_ColObjects[k])
                for k in self.__names__]
        return '{\n    %s }' % (',\n    '.join(rep))

    def __str__(self):
        """ Gives a Table representation for printing purposes
        """
        rep = [ '%s(%r%r)' %  \
                (k, self.__types__[k], self._v_shapes[k])
                for k in self.__names__ ]
        return '[%s]' % (', '.join(rep))

    def _close(self):
        self._v_ColObjects.clear()
        del self.__dict__["_v_ColObjects"]
        self._v_itemsizes.clear()
        self._v_shapes.clear()
        self.__dflts__.clear()
        self.__types__.clear()
        self.__dict__.clear()
        return

    def testtype(self, object):
        """Test if datatype is valid and returns a default value for
        each one.
        """
        datatype = object.rectype
        if datatype in ('b', 'B', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q'):
            dfltvalue = int(0)
        elif datatype in ('f', 'd'):
            dfltvalue = float(0)
        elif datatype in ('F', 'D'):
            dfltvalue = complex(0)
        elif datatype in ('c',):
#             dfltvalue = str(" ")
            dfltvalue = int(0)
        # Add more code to check for validity on string type!
        elif datatype.find("s") != -1:
            dfltvalue = str("")
        else:
            raise TypeError, "DataType \'%s\' not supported!." \
                  % datatype
        return dfltvalue

    def cmpkeys(self, key1, key2):
        """Helps .sort() to respect pos field in type definition"""
        # Do not try to order variables that starts with special
        # prefixes
        if ((key1.startswith('__') or key1.startswith('_v_')) and
            (key2.startswith('__') or key2.startswith('_v_'))):
            return 0
        # A variable that starts with a special prefix
        # is always greater than a normal variable
        elif (key1.startswith('__') or key1.startswith('_v_')):
            return 1
        elif (key2.startswith('__') or key2.startswith('_v_')):
            return -1
        pos1 = self.classdict[key1].pos
        pos2 = self.classdict[key2].pos
        # pos = None is always greater than a number
        if pos1 == None:
            return 1
        if pos2 == None:
            return -1
        if pos1 < pos2:
            return -1
        if pos1 == pos2:
            return 0
        if pos1 > pos2:
            return 1


class metaIsDescription(type):
    "Helper metaclass to return the class variables as a dictionary "
    
    def __new__(cls, classname, bases, classdict):
        """ Return a new class with a "columns" attribute filled
        """

        newdict = {"columns":{},
                   }
        for k in classdict.keys():
            #if not (k.startswith('__') or k.startswith('_v_')):
            # We let pass _v_ variables to configure class behaviour
            if not (k.startswith('__')):
                newdict["columns"][k] = classdict[k]

        # Return a new class with the "columns" attribute filled
        return type.__new__(cls, classname, bases, newdict)
    

class IsDescription(object):
    """ For convenience: inheriting from IsDescription can be used to get
        the new metaclass (same as defining __metaclass__ yourself).
    """
    __metaclass__ = metaIsDescription


if __name__=="__main__":
    """Test code"""
    
    class Test(IsDescription):
        """A description that has several columns"""
        x = Col("Int32", 2, 0)
        y = FloatCol(1, shape=(2,3))
        z = UInt8Col(1)
        color = StringCol(2, " ")

    # example cases of class Test
    klass = Test()
    rec = Description(klass.columns)
    print "rec value ==>", rec
    print "Column names ==>", rec.__names__
    print "Format for this table ==>", rec._v_fmt
    print "recarray Format for this table ==>", rec._v_recarrfmt
