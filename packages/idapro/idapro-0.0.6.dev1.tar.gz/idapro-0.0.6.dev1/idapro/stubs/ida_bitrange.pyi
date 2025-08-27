from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Definition of the bitrange_t class.

"""

class bitrange_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: bitrange_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, r: bitrange_t) -> bool: ...
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, r: bitrange_t) -> bool: ...
    def __init__(self, bit_ofs: uint16 = 0, size_in_bits: uint16 = 0) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, r: bitrange_t) -> bool: ...
    def __lt__(self, r: bitrange_t) -> bool: ...
    def __ne__(self, r: bitrange_t) -> bool: ...
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
    def __str__(self) -> str: ...
    def __subclasshook__(self, *args: Any, **kwargs: Any) -> Any: ...
        """Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.__subclasscheck__().
        It should return True, False or NotImplemented.  If it returns
        NotImplemented, the normal algorithm is used.  Otherwise, it
        overrides the normal algorithm (and the outcome is cached).
        
        """
    def __swig_destroy__(self, *args: Any, **kwargs: Any) -> Any: ...
    def apply_mask(self, subrange: bitrange_t) -> bool: ...
        """Apply mask to a bitrange 
                
        @param subrange: range *inside* the main bitrange to keep After this operation the main bitrange will be truncated to have only the bits that are specified by subrange. Example: [off=8,nbits=4], subrange[off=1,nbits=2] => [off=9,nbits=2]
        @returns success
        """
    def bitoff(self) -> uint: ...
        """Get offset of 1st bit.
        
        """
    def bitsize(self) -> uint: ...
        """Get size of the value in bits.
        
        """
    def bytesize(self) -> uint: ...
        """Size of the value in bytes.
        
        """
    def compare(self, r: bitrange_t) -> int: ...
    def create_union(self, r: bitrange_t) -> None: ...
        """Create union of 2 ranges including the hole between them.
        
        """
    def empty(self) -> bool: ...
        """Is the bitrange empty?
        
        """
    def extract(self, src: void const *, is_mf: bool) -> bool: ...
    def has_common(self, r: bitrange_t) -> bool: ...
        """Does have common bits with another bitrange?
        
        """
    def init(self, bit_ofs: uint16, size_in_bits: uint16) -> None: ...
        """Initialize offset and size to given values.
        
        """
    def inject(self, dst: void *, src: bytevec_t const &, is_mf: bool) -> bool: ...
    def intersect(self, r: bitrange_t) -> None: ...
        """Intersect two ranges.
        
        """
    def mask64(self) -> uint64: ...
        """Convert to mask of 64 bits.
        
        """
    def reset(self) -> None: ...
        """Make the bitrange empty.
        
        """
    def shift_down(self, cnt: uint) -> None: ...
        """Shift range down (left)
        
        """
    def shift_up(self, cnt: uint) -> None: ...
        """Shift range up (right)
        
        """
    def sub(self, r: bitrange_t) -> bool: ...
        """Subtract a bitrange.
        
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

SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module