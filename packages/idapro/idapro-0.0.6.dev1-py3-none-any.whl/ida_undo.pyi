from typing import Any, Optional, List, Dict, Tuple, Callable, Union

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

def create_undo_point(args: Any) -> bool: ...
    """Create a new restore point. The user can undo to this point in the future. 
            
    @param bytes: body of the record for UNDO_ACTION_START
    @param size: size of the record for UNDO_ACTION_START
    @returns success; fails if undo is disabled
    """

def get_redo_action_label() -> str: ...
    """Get the label of the action that will be redone. This function returns the text that can be displayed in the redo menu 
            
    @returns success
    """

def get_undo_action_label() -> str: ...
    """Get the label of the action that will be undone. This function returns the text that can be displayed in the undo menu 
            
    @returns success
    """

def perform_redo() -> bool: ...
    """Perform redo. 
            
    @returns success
    """

def perform_undo() -> bool: ...
    """Perform undo. 
            
    @returns success
    """

SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module