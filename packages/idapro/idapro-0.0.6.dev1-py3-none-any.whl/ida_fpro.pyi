from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""System independent counterparts of FILE* related functions from Clib.

You should not use C standard I/O functions in your modules. The reason: Each module compiled with Borland (and statically linked to Borland's library) will host a copy of the FILE * information.
So, if you open a file in the plugin and pass the handle to the kernel, the kernel will not be able to use it.
If you really need to use the standard functions, define USE_STANDARD_FILE_FUNCTIONS. In this case do not mix them with q... functions. 
    
"""

class qfile_t:
    """A helper class to work with FILE related functions."""
    @property
    def __idc_cvt_id__(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> Any: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> Any: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> Any: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> Any: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> Any: ...
        """Return self<value."""
    def __ne__(self, value: Any) -> Any: ...
        """Return self!=value."""
    def __new__(self, args: Any, kwargs: Any) -> Any: ...
        """Create and return a new object.  See help(type) for accurate signature."""
    def __reduce__(self) -> Any: ...
        """Helper for pickle."""
    def __reduce_ex__(self, protocol: Any) -> Any: ...
        """Helper for pickle."""
    def __repr__(self) -> Any: ...
    def __setattr__(self, name: Any, value: Any) -> Any: ...
        """Implement setattr(self, name, value)."""
    def __sizeof__(self) -> Any: ...
        """Size of object in memory, in bytes."""
    def __str__(self) -> Any: ...
        """Return str(self)."""
    def __subclasshook__(self, *args: Any, **kwargs: Any) -> Any: ...
        """Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.__subclasscheck__().
        It should return True, False or NotImplemented.  If it returns
        NotImplemented, the normal algorithm is used.  Otherwise, it
        overrides the normal algorithm (and the outcome is cached).
        
        """
    def __swig_destroy__(self, *args: Any, **kwargs: Any) -> Any: ...
    def close(self) -> Any: ...
        """Closes the file"""
    def filename(self) -> PyObject *: ...
    def flush(self) -> Any: ...
    def from_capsule(self, pycapsule: PyObject *) -> qfile_t *: ...
    def from_fp(self, fp: FILE *) -> qfile_t *: ...
    def get_byte(self) -> Any: ...
        """Reads a single byte from the file. Returns None if EOF or the read byte"""
    def get_fp(self) -> FILE *: ...
    def gets(self, len: Any) -> Any: ...
        """Reads a line from the input file. Returns the read line or None
        
        @param len: the maximum line length
        """
    def open(self, filename: Any, mode: Any) -> Any: ...
        """Opens a file
        
        @param filename: the file name
        @param mode: The mode string, ala fopen() style
        @return: Boolean
        """
    def opened(self) -> Any: ...
        """Checks if the file is opened or not"""
    def put_byte(self) -> Any: ...
        """Writes a single byte to the file
        
        @param chr: the byte value
        """
    def puts(self, str: str) -> int: ...
    def read(self, size: Any) -> Any: ...
        """Reads from the file. Returns the buffer or None
        
        @param size: the maximum number of bytes to read
        @return: a str, or None
        """
    def readbytes(self, size: Any, big_endian: Any) -> Any: ...
        """Similar to read() but it respect the endianness
        
        @param size: the maximum number of bytes to read
        @param big_endian: endianness
        @return a str, or None
        """
    def seek(self, offset: Any, whence: Any = 0) -> Any: ...
        """Set input source position
        
        @param offset: the seek offset
        @param whence: the position to seek from
        @return: the new position (not 0 as fseek!)
        """
    def size(self) -> int64: ...
    def tell(self) -> Any: ...
        """Returns the current position"""
    def tmpfile(self) -> Any: ...
        """A static method to construct an instance using a temporary file"""
    def write(self, buf: Any) -> Any: ...
        """Writes to the file. Returns 0 or the number of bytes written
        
        @param buf: the str to write
        @return: result code
        """
    def writebytes(self, size: Any, big_endian: Any) -> Any: ...
        """Similar to write() but it respect the endianness
        
        @param buf: the str to write
        @param big_endian: endianness
        @return: result code
        """

def List(args: Any, kwargs: Any) -> Any: ...
    """A generic version of list."""

def Tuple(args: Any, kwargs: Any) -> Any: ...
    """Tuple type; Tuple[X, Y] is the cross-product type of X and Y.
    
        Example: Tuple[T1, T2] is a tuple of two elements corresponding
        to type variables T1 and T2.  Tuple[int, float, str] is a tuple
        of an int, a float and a string.
    
        To specify a variable-length tuple of homogeneous type, use Tuple[T, ...].
        
    """

def Union(args: Any, kwds: Any) -> Any: ...
    """Union type; Union[X, Y] means either X or Y.
    
        To define a union, use e.g. Union[int, str].  Details:
        - The arguments must be types and there must be at least one.
        - None as an argument is a special case and is replaced by
          type(None).
        - Unions of unions are flattened, e.g.::
    
            Union[Union[int, str], float] == Union[int, str, float]
    
        - Unions of a single argument vanish, e.g.::
    
            Union[int] == int  # The constructor actually returns int
    
        - Redundant arguments are skipped, e.g.::
    
            Union[int, str, int] == Union[int, str]
    
        - When comparing unions, the argument order is ignored, e.g.::
    
            Union[int, str] == Union[str, int]
    
        - You cannot subclass or instantiate a union.
        - You can use Optional[X] as a shorthand for Union[X, None].
        
    """

def qfclose(fp: FILE *) -> int: ...

def qfile_t_from_capsule(pycapsule: PyObject *) -> qfile_t *: ...

def qfile_t_from_fp(fp: FILE *) -> qfile_t *: ...

def qfile_t_tmpfile() -> Any: ...
    """A static method to construct an instance using a temporary file"""

QMOVE_CROSS_FS: int  # 1
QMOVE_OVERWRITE: int  # 2
QMOVE_OVR_RO: int  # 4
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module