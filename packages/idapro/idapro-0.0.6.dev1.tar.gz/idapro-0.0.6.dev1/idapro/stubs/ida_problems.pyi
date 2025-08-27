from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Functions that deal with the list of problems.

There are several problem lists. An address may be inserted to any list. The kernel simply maintains these lists, no additional processing is done.
The problem lists are accessible for the user from the View->Subviews->Problems menu item.
Addresses in the lists are kept sorted. In general IDA just maintains these lists without using them during analysis (except PR_ROLLED). 
    
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

def forget_problem(type: problist_id_t, ea: int) -> bool: ...
    """Remove an address from a problem list 
            
    @param type: problem list type
    @param ea: linear address
    @returns success
    """

def get_problem(type: problist_id_t, lowea: int) -> ida_idaapi.ea_t: ...
    """Get an address from the specified problem list. The address is not removed from the list. 
            
    @param type: problem list type
    @param lowea: the returned address will be higher or equal than the specified address
    @returns linear address or BADADDR
    """

def get_problem_desc(t: problist_id_t, ea: int) -> str: ...
    """Get the human-friendly description of the problem, if one was provided to remember_problem. 
            
    @param t: problem list type.
    @param ea: linear address.
    @returns the message length or -1 if none
    """

def get_problem_name(type: problist_id_t, longname: bool = True) -> str: ...
    """Get problem list description.
    
    """

def is_problem_present(t: problist_id_t, ea: int) -> bool: ...
    """Check if the specified address is present in the problem list.
    
    """

def remember_problem(type: problist_id_t, ea: int, msg: str = None) -> None: ...
    """Insert an address to a list of problems. Display a message saying about the problem (except of PR_ATTN,PR_FINAL) PR_JUMP is temporarily ignored. 
            
    @param type: problem list type
    @param ea: linear address
    @param msg: a user-friendly message to be displayed instead of the default more generic one associated with the type of problem. Defaults to nullptr.
    """

def was_ida_decision(ea: int) -> bool: ...

PR_ATTN: int  # 12
PR_BADSTACK: int  # 11
PR_COLLISION: int  # 15
PR_DECIMP: int  # 16
PR_DISASM: int  # 7
PR_END: int  # 17
PR_FINAL: int  # 13
PR_HEAD: int  # 8
PR_ILLADDR: int  # 9
PR_JUMP: int  # 6
PR_MANYLINES: int  # 10
PR_NOBASE: int  # 1
PR_NOCMT: int  # 4
PR_NOFOP: int  # 3
PR_NONAME: int  # 2
PR_NOXREFS: int  # 5
PR_ROLLED: int  # 14
SWIG_PYTHON_LEGACY_BOOL: int  # 1
cvar: swigvarlink
ida_idaapi: module
weakref: module