########################################################################
#
#       License: BSD
#       Created: December 17, 2004
#       Author:  Francesc Altet - faltet@carabos.com
#
#       $Id$
#
########################################################################

"""
Declare exceptions and warnings that are specific to PyTables.

Classes:

`HDF5ExtError`
    A low level HDF5 operation failed.
`ClosedNodeError`
    The operation can not be completed because the node is closed.
`ClosedFileError`
    The operation can not be completed because the hosting file is
    closed.
`FileModeError`
    The operation can not be carried out because the mode in which the
    hosting file is opened is not adequate.
`NodeError`
    Invalid hierarchy manipulation operation requested.
`NoSuchNodeError`
    An operation was requested on a node that does not exist.
`UndoRedoError`
    Problems with doing/redoing actions with Undo/Redo feature.
`UndoRedoWarning`
    Issued when an action not supporting undo/redo is run.
`NaturalNameWarning`
    Issued when a non-pythonic name is given for a node.
`PerformanceWarning`
    Warning for operations which may cause a performance drop.
"""

__docformat__ = 'reStructuredText'
"""The format of documentation strings in this module."""

__version__ = '$Revision$'
"""Repository version of this file."""



class HDF5ExtError(RuntimeError):
    """
    A low level HDF5 operation failed.

    This exception is raised by ``hdf5Extension`` (the low level
    PyTables component used for accessing HDF5 files).  It usually
    signals that something is not going well in the HDF5 library or even
    at the Input/Output level, and uses to be accompanied by an
    extensive HDF5 back trace on standard error.
    """
    pass



# The following exceptions are concretions of the ``ValueError`` exceptions
# raised by ``file`` objects on certain operations.

class ClosedNodeError(ValueError):
    """
    The operation can not be completed because the node is closed.

    For instance, listing the children of a closed group is not allowed.
    """
    pass


class ClosedFileError(ValueError):
    """
    The operation can not be completed because the hosting file is
    closed.

    For instance, getting an existing node from a closed file is not
    allowed.
    """
    pass


class FileModeError(ValueError):
    """
    The operation can not be carried out because the mode in which the
    hosting file is opened is not adequate.

    For instance, removing an existing leaf from a read-only file is not
    allowed.
    """
    pass



class NodeError(AttributeError, LookupError):
    """
    Invalid hierarchy manipulation operation requested.

    This exception is raised when the user requests an operation on the
    hierarchy which can not be run because of the current layout of the
    tree.  This includes accessing nonexistent nodes, moving or copying
    or creating over an existing node, non-recursively removing groups
    with children, and other similarly invalid operations.

    A node in a PyTables database cannot be simply overwritten by
    replacing it.  Instead, the old node must be removed explicitely
    before another one can take its place.  This is done to protect
    interactive users from inadvertedly deleting whole trees of data by
    a single erroneous command.
    """
    pass


class NoSuchNodeError(NodeError):
    """
    An operation was requested on a node that does not exist.

    This exception is raised when an operation gets a path name or a
    ``(where, name)`` pair leading to a nonexistent node.
    """
    pass



class UndoRedoError(Exception):
    """
    Problems with doing/redoing actions with Undo/Redo feature.

    This exception indicates a problem related to the Undo/Redo
    mechanism, such as trying to undo or redo actions with this
    mechanism disabled, or going to a nonexistent mark.
    """
    pass


class UndoRedoWarning(Warning):
    """
    Issued when an action not supporting Undo/Redo is run.

    This warning is only shown when the Undo/Redo mechanism is enabled.
    """
    pass



class NaturalNameWarning(Warning):
    """
    Issued when a non-pythonic name is given for a node.

    This is not an error and may even be very useful in certain
    contexts, but one should be aware that such nodes cannot be accessed
    using natural naming.  (Instead, ``getattr()`` or
    ``group._f_getChild()`` must be used explicitly.)
    """
    pass


class PerformanceWarning(Warning):
    """
    Warning for operations which may cause a performance drop.

    This warning is issued when an operation is made on the database
    which may cause it to slow down on future operations (i.e. making
    the node tree grow too much).
    """
    pass



## Local Variables:
## mode: python
## py-indent-offset: 4
## tab-width: 4
## fill-column: 72
## End:
