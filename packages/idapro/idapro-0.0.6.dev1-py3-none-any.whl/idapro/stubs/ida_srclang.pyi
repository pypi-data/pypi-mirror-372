from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Third-party compiler support.

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

def parse_decls_for_srclang(lang: srclang_t, til: til_t, input: str, is_path: bool) -> int: ...
    """Parse type declarations in the specified language 
            
    @param lang: the source language(s) expected in the input
    @param til: type library to store the types
    @param input: input source. can be a file path or decl string
    @param is_path: true if input parameter is a path to a source file, false if the input is an in-memory source snippet
    @retval -1: no parser was found that supports the given source language(s)
    @retval else: the number of errors encountered in the input source
    """

def parse_decls_with_parser(parser_name: str, til: til_t, input: str, is_path: bool) -> int: ...
    """Parse type declarations using the parser with the specified name 
            
    @param parser_name: name of the target parser
    @param til: type library to store the types
    @param input: input source. can be a file path or decl string
    @param is_path: true if input parameter is a path to a source file, false if the input is an in-memory source snippet
    @retval -1: no parser was found with the given name
    @retval else: the number of errors encountered in the input source
    """

def select_parser_by_name(name: str) -> bool: ...
    """Set the parser with the given name as the current parser. Pass nullptr or an empty string to select the default parser. 
            
    @returns false if no parser was found with the given name
    """

def select_parser_by_srclang(lang: srclang_t) -> bool: ...
    """Set the parser that supports the given language(s) as the current parser. The selected parser must support all languages specified by the given srclang_t. 
            
    @returns false if no such parser was found
    """

def set_parser_argv(parser_name: str, argv: str) -> int: ...
    """Set the command-line args to use for invocations of the parser with the given name 
            
    @param parser_name: name of the target parser
    @param argv: argument list
    @retval -1: no parser was found with the given name
    @retval -2: the operation is not supported by the given parser
    @retval 0: success
    """

SRCLANG_C: int  # 1
SRCLANG_CPP: int  # 2
SRCLANG_GO: int  # 16
SRCLANG_OBJC: int  # 4
SRCLANG_SWIFT: int  # 8
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module