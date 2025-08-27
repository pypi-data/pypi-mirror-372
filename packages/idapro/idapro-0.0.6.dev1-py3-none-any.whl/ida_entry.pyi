from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Functions that deal with entry points.

Exported functions are considered as entry points as well.
IDA maintains list of entry points to the program. Each entry point:
* has an address
* has a name
* may have an ordinal number 


    
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

def add_entry(ord: int, ea: int, name: str, makecode: bool, flags: int = 0) -> bool: ...
    """Add an entry point to the list of entry points. 
            
    @param ord: ordinal number if ordinal number is equal to 'ea' then ordinal is not used
    @param ea: linear address
    @param name: name of entry point. If the specified location already has a name, the old name will be appended to the regular comment. If name == nullptr, then the old name will be retained.
    @param makecode: should the kernel convert bytes at the entry point to instruction(s)
    @param flags: See AEF_*
    @returns success (currently always true)
    """

def get_entry(ord: int) -> ida_idaapi.ea_t: ...
    """Get entry point address by its ordinal 
            
    @param ord: ordinal number of entry point
    @returns address or BADADDR
    """

def get_entry_forwarder(ord: int) -> str: ...
    """Get forwarder name for the entry point by its ordinal. 
            
    @param ord: ordinal number of entry point
    @returns size of entry forwarder name or -1
    """

def get_entry_name(ord: int) -> str: ...
    """Get name of the entry point by its ordinal. 
            
    @param ord: ordinal number of entry point
    @returns size of entry name or -1
    """

def get_entry_ordinal(idx: size_t) -> int: ...
    """Get ordinal number of an entry point. 
            
    @param idx: internal number of entry point. Should be in the range 0..get_entry_qty()-1
    @returns ordinal number or 0.
    """

def get_entry_qty() -> int: ...
    """Get number of entry points.
    
    """

def rename_entry(ord: int, name: str, flags: int = 0) -> bool: ...
    """Rename entry point. 
            
    @param ord: ordinal number of the entry point
    @param name: name of entry point. If the specified location already has a name, the old name will be appended to a repeatable comment.
    @param flags: See AEF_*
    @returns success
    """

def set_entry_forwarder(ord: int, name: str, flags: int = 0) -> bool: ...
    """Set forwarder name for ordinal. 
            
    @param ord: ordinal number of the entry point
    @param name: forwarder name for entry point.
    @param flags: See AEF_*
    @returns success
    """

AEF_IDBENC: int  # 1
AEF_NODUMMY: int  # 2
AEF_UTF8: int  # 0
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module