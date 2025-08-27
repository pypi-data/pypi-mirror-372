from typing import Any, Optional, List, Dict, Tuple, Callable, Union

class idasgn_header_t:
    @property
    def apptype(self) -> Any: ...
    @property
    def ctype_crc(self) -> Any: ...
    @property
    def ctype_crc_3v(self) -> Any: ...
    @property
    def ctype_crc_alt(self) -> Any: ...
    @property
    def ctype_name(self) -> Any: ...
    @property
    def file_formats(self) -> Any: ...
    @property
    def flags(self) -> Any: ...
    @property
    def libname_length(self) -> Any: ...
    @property
    def magic(self) -> Any: ...
    @property
    def number_of_modules(self) -> Any: ...
    @property
    def number_of_modules_v5(self) -> Any: ...
    @property
    def ostype(self) -> Any: ...
    @property
    def pattern_length(self) -> Any: ...
    @property
    def processor_id(self) -> Any: ...
    @property
    def version(self) -> Any: ...
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
    def __init__(self) -> Any: ...
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

def get_idasgn_header_by_short_name(out_header: idasgn_header_t, name: str) -> str: ...
    """Get idasgn header by a short signature name. 
            
    @param out_header: buffer for the signature file header
    @param name: short name of a signature
    @returns true in case of success
    """

def get_idasgn_path_by_short_name(name: str) -> str: ...
    """Get idasgn full path by a short signature name. 
            
    @param name: short name of a signature
    @returns true in case of success
    """

APPT_16BIT: int  # 128
APPT_1THREAD: int  # 32
APPT_32BIT: int  # 256
APPT_64BIT: int  # 512
APPT_CONSOLE: int  # 1
APPT_DRIVER: int  # 16
APPT_GRAPHIC: int  # 2
APPT_LIBRARY: int  # 8
APPT_MTHREAD: int  # 64
APPT_PROGRAM: int  # 4
LS_CTYPE: int  # 2
LS_CTYPE2: int  # 4
LS_CTYPE_3V: int  # 32
LS_CTYPE_ALT: int  # 8
LS_STARTUP: int  # 1
LS_ZIP: int  # 16
OSTYPE_MSDOS: int  # 1
OSTYPE_NETW: int  # 8
OSTYPE_OS2: int  # 4
OSTYPE_OTHER: int  # 32
OSTYPE_UNIX: int  # 16
OSTYPE_WIN: int  # 2
SIGN_HEADER_MAGIC: str  # IDASGN
SIGN_HEADER_VERSION: int  # 10
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module