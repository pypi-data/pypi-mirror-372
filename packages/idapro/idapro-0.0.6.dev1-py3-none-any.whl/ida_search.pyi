from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Middle-level search functions.

They all are controlled by Search flags 
    
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

def find_code(ea: int, sflag: int) -> ida_idaapi.ea_t: ...

def find_data(ea: int, sflag: int) -> ida_idaapi.ea_t: ...

def find_defined(ea: int, sflag: int) -> ida_idaapi.ea_t: ...

def find_error(ea: int, sflag: int) -> int *: ...

def find_imm(ea: int, sflag: int, search_value: int) -> int *: ...

def find_not_func(ea: int, sflag: int) -> ida_idaapi.ea_t: ...

def find_notype(ea: int, sflag: int) -> int *: ...

def find_reg_access(out: reg_access_t, start_ea: int, end_ea: int, regname: str, sflag: int) -> ida_idaapi.ea_t: ...

def find_suspop(ea: int, sflag: int) -> int *: ...

def find_text(start_ea: int, y: int, x: int, ustr: str, sflag: int) -> ida_idaapi.ea_t: ...

def find_unknown(ea: int, sflag: int) -> ida_idaapi.ea_t: ...

def search_down(sflag: int) -> bool: ...
    """Is the SEARCH_DOWN bit set?
    
    """

SEARCH_BRK: int  # 256
SEARCH_CASE: int  # 4
SEARCH_DEF: int  # 1024
SEARCH_DOWN: int  # 1
SEARCH_IDENT: int  # 128
SEARCH_NEXT: int  # 2
SEARCH_NOBRK: int  # 16
SEARCH_NOSHOW: int  # 32
SEARCH_REGEX: int  # 8
SEARCH_UP: int  # 0
SEARCH_USE: int  # 512
SEARCH_USESEL: int  # 2048
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module