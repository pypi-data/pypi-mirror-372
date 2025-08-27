from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Registry related functions.

IDA uses the registry to store global configuration options that must persist after IDA has been closed.
On Windows, IDA uses the Windows registry directly. On Unix systems, the registry is stored in a file (typically ~/.idapro/ida.reg).
The root key for accessing IDA settings in the registry is defined by ROOT_KEY_NAME. 
    
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

def reg_data_type(name: str, subkey: str = None) -> regval_type_t: ...
    """Get data type of a given value. 
            
    @param name: value name
    @param subkey: key name
    @returns false if the [key+]value doesn't exist
    """

def reg_delete(name: str, subkey: str = None) -> bool: ...
    """Delete a value from the registry. 
            
    @param name: value name
    @param subkey: parent key
    @returns success
    """

def reg_delete_subkey(name: str) -> bool: ...
    """Delete a key from the registry.
    
    """

def reg_delete_tree(name: str) -> bool: ...
    """Delete a subtree from the registry.
    
    """

def reg_exists(name: str, subkey: str = None) -> bool: ...
    """Is there already a value with the given name? 
            
    @param name: value name
    @param subkey: parent key
    """

def reg_read_binary(name: str, subkey: str = None) -> PyObject *: ...
    """Read binary data from the registry. 
            
    @param name: value name
    @param subkey: key name
    @returns false if 'data' is not large enough to hold all data present. in this case 'data' is left untouched.
    """

def reg_read_bool(name: str, defval: bool, subkey: str = None) -> bool: ...
    """Read boolean value from the registry. 
            
    @param name: value name
    @param defval: default value
    @param subkey: key name
    @returns boolean read from registry, or 'defval' if the read failed
    """

def reg_read_int(name: str, defval: int, subkey: str = None) -> int: ...
    """Read integer value from the registry. 
            
    @param name: value name
    @param defval: default value
    @param subkey: key name
    @returns the value read from the registry, or 'defval' if the read failed
    """

def reg_read_string(name: str, subkey: str = None, _def: str = None) -> PyObject *: ...
    """Read a string from the registry. 
            
    @param name: value name
    @param subkey: key name
    @returns success
    """

def reg_read_strlist(subkey: str) -> qstrvec_t *: ...
    """Retrieve all string values associated with the given key. Also see reg_update_strlist(), reg_write_strlist() 
            
    """

def reg_subkey_exists(name: str) -> bool: ...
    """Is there already a key with the given name?
    
    """

def reg_subkey_subkeys(name: str) -> PyObject *: ...
    """Get all subkey names of given key.
    
    """

def reg_subkey_values(name: str) -> PyObject *: ...
    """Get all value names under given key.
    
    """

def reg_update_filestrlist(subkey: str, add: str, maxrecs: size_t, rem: str = None) -> None: ...
    """Update registry with a file list. Case sensitivity will vary depending on the target OS. 
            
    """

def reg_update_strlist(subkey: str, add: str, maxrecs: size_t, rem: str = None, ignorecase: bool = False) -> None: ...
    """Update list of strings associated with given key. 
            
    @param subkey: key name
    @param add: string to be added to list, can be nullptr
    @param maxrecs: limit list to this size
    @param rem: string to be removed from list, can be nullptr
    @param ignorecase: ignore case for 'add' and 'rem'
    """

def reg_write_binary(name: str, py_bytes: PyObject *, subkey: str = None) -> PyObject *: ...
    """Write binary data to the registry. 
            
    @param name: value name
    @param subkey: key name
    """

def reg_write_bool(name: str, value: int, subkey: str = None) -> None: ...
    """Write boolean value to the registry. 
            
    @param name: value name
    @param value: boolean to write (nonzero = true)
    @param subkey: key name
    """

def reg_write_int(name: str, value: int, subkey: str = None) -> None: ...
    """Write integer value to the registry. 
            
    @param name: value name
    @param value: value to write
    @param subkey: key name
    """

def reg_write_string(name: str, utf8: str, subkey: str = None) -> None: ...
    """Write a string to the registry. 
            
    @param name: value name
    @param utf8: utf8-encoded string
    @param subkey: key name
    """

def reg_write_strlist(_in: qstrvec_t const &, subkey: str) -> None: ...
    """Write string values associated with the given key. Also see reg_read_strlist(), reg_update_strlist() 
            
    """

def set_registry_name(name: str) -> bool: ...

HVUI_REGISTRY_NAME: str  # hvui
IDA_REGISTRY_NAME: str  # ida
ROOT_KEY_NAME: str  # Software\Hex-Rays\IDA
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
reg_binary: int  # 3
reg_dword: int  # 4
reg_sz: int  # 1
reg_unknown: int  # 0
weakref: module