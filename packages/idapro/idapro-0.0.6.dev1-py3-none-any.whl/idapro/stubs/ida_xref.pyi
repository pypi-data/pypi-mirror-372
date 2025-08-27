from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Functions that deal with cross-references.

There are 2 types of xrefs: CODE and DATA references. All xrefs are kept in the bTree except ordinary execution flow to the next instruction. Ordinary execution flow to the next instruction is kept in flags (see bytes.hpp)
The source address of a cross-reference must be an item head (is_head) or a structure member id.
Cross-references are automatically sorted. 
    
"""

class cases_and_targets_t:
    @property
    def cases(self) -> Any: ...
    @property
    def targets(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
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
    def __ne__(self, value: Any) -> bool: ...
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

class casevec_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: casevec_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> Any: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> qvector< long long >: ...
    def __gt__(self, value: Any) -> Any: ...
        """Return self>value."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __iter__(self) -> Any: ...
        """Helper function, to be set as __iter__ method for qvector-, or array-based classes."""
    def __le__(self, value: Any) -> Any: ...
        """Return self<=value."""
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> Any: ...
        """Return self<value."""
    def __ne__(self, r: casevec_t) -> bool: ...
    def __new__(self, args: Any, kwargs: Any) -> Any: ...
        """Create and return a new object.  See help(type) for accurate signature."""
    def __reduce__(self) -> Any: ...
        """Helper for pickle."""
    def __reduce_ex__(self, protocol: Any) -> Any: ...
        """Helper for pickle."""
    def __repr__(self) -> Any: ...
    def __setattr__(self, name: Any, value: Any) -> Any: ...
        """Implement setattr(self, name, value)."""
    def __setitem__(self, i: size_t, v: qvector< long long > const &) -> None: ...
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
    def add_unique(self, x: qvector< long long > const &) -> bool: ...
    def append(self, args: Any) -> None: ...
    def at(self, i: size_t) -> qvector< long long >: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< qvector< long long > >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< qvector< long long > >: ...
    def erase(self, args: Any) -> qvector< qvector< long long > >: ...
    def extend(self, x: casevec_t) -> None: ...
    def extract(self) -> qvector< long long > *: ...
    def find(self, args: Any) -> qvector< qvector< long long > >: ...
    def front(self) -> Any: ...
    def grow(self, args: Any) -> None: ...
    def has(self, x: qvector< long long > const &) -> bool: ...
    def inject(self, s: qvector< long long > *, len: size_t) -> None: ...
    def insert(self, it: qvector< qvector< long long > >::iterator, x: qvector< long long > const &) -> qvector< qvector< long long > >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> qvector< long long > &: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: casevec_t) -> None: ...
    def truncate(self) -> None: ...

class xrefblk_t:
    @property
    def frm(self) -> Any: ...
    @property
    def iscode(self) -> Any: ...
    @property
    def to(self) -> Any: ...
    @property
    def type(self) -> Any: ...
    @property
    def user(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
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
    def __ne__(self, value: Any) -> bool: ...
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
    def crefs_from(self, ea: Any) -> Any: ...
        """
                Provide an iterator on code references from ea including flow references
                
        """
    def crefs_to(self, ea: Any) -> Any: ...
        """
                Provide an iterator on code references to ea including flow references
                
        """
    def drefs_from(self, ea: Any) -> Any: ...
        """
                Provide an iterator on data references from ea
                
        """
    def drefs_to(self, ea: Any) -> Any: ...
        """
                Provide an iterator on data references to ea
                
        """
    def fcrefs_from(self, ea: Any) -> Any: ...
        """
                Provide an iterator on code references from ea
                
        """
    def fcrefs_to(self, ea: Any) -> Any: ...
        """
                Provide an iterator on code references to ea
                
        """
    def first_from(self, _from: int, flags: int = 0) -> bool: ...
    def first_to(self, _to: int, flags: int = 0) -> bool: ...
    def next_from(self, args: Any) -> bool: ...
    def next_to(self, args: Any) -> bool: ...
    def refs_from(self, ea: Any, flag: Any) -> Any: ...
        """
                Provide an iterator on from reference represented by flag
                
        """
    def refs_to(self, ea: Any, flag: Any) -> Any: ...
        """
                Provide an iterator on to reference represented by flag
                
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

def add_cref(frm: int, to: int, type: cref_t) -> bool: ...
    """Create a code cross-reference. 
            
    @param to: linear address of referenced instruction
    @param type: cross-reference type
    @returns success
    """

def add_dref(frm: int, to: int, type: dref_t) -> bool: ...
    """Create a data cross-reference. 
            
    @param to: linear address of referenced data
    @param type: cross-reference type
    @returns success (may fail if user-defined xref exists from->to)
    """

def calc_switch_cases(ea: Any, si: Any) -> Any: ...
    """Get information about a switch's cases.
    
    The returned information can be used as follows:
    
        for idx in range(len(results.cases)):
            cur_case = results.cases[idx]
            for cidx in range(len(cur_case)):
                print("case: %d" % cur_case[cidx])
            print("  goto 0x%x" % results.targets[idx])
    
    @param ea: address of the 'indirect jump' instruction
    @param si: switch information
    
    @return: a structure with 2 members: 'cases', and 'targets'.
    """

def create_switch_table(ea: Any, si: Any) -> Any: ...
    """Create switch table from the switch information
    
    @param ea: address of the 'indirect jump' instruction
    @param si: switch information
    
    @return: Boolean
    """

def create_switch_xrefs(ea: Any, si: Any) -> Any: ...
    """This function creates xrefs from the indirect jump.
    
    Usually there is no need to call this function directly because the kernel
    will call it for switch tables
    
    Note: Custom switch information are not supported yet.
    
    @param ea: address of the 'indirect jump' instruction
    @param si: switch information
    
    @return: Boolean
    """

def del_cref(frm: int, to: int, expand: bool) -> bool: ...
    """Delete a code cross-reference. 
            
    @param to: linear address of referenced instruction
    @param expand: policy to delete the referenced instruction
    * 1: plan to delete the referenced instruction if it has no more references.
    * 0: don't delete the referenced instruction even if no more cross-references point to it
    @retval true: if the referenced instruction will be deleted
    """

def del_dref(frm: int, to: int) -> None: ...
    """Delete a data cross-reference. 
            
    @param to: linear address of referenced data
    """

def delete_switch_table(jump_ea: int, si: switch_info_t) -> None: ...

def get_first_cref_from(frm: int) -> ida_idaapi.ea_t: ...
    """Get first instruction referenced from the specified instruction. If the specified instruction passes execution to the next instruction then the next instruction is returned. Otherwise the lowest referenced address is returned (remember that xrefs are kept sorted!). 
            
    @returns first referenced address. If the specified instruction doesn't reference to other instructions then returns BADADDR.
    """

def get_first_cref_to(to: int) -> ida_idaapi.ea_t: ...
    """Get first instruction referencing to the specified instruction. If the specified instruction may be executed immediately after its previous instruction then the previous instruction is returned. Otherwise the lowest referencing address is returned. (remember that xrefs are kept sorted!). 
            
    @param to: linear address of referenced instruction
    @returns linear address of the first referencing instruction or BADADDR.
    """

def get_first_dref_from(frm: int) -> ida_idaapi.ea_t: ...
    """Get first data referenced from the specified address. 
            
    @returns linear address of first (lowest) data referenced from the specified address. Return BADADDR if the specified instruction/data doesn't reference to anything.
    """

def get_first_dref_to(to: int) -> ida_idaapi.ea_t: ...
    """Get address of instruction/data referencing to the specified data. 
            
    @param to: linear address of referencing instruction or data
    @returns BADADDR if nobody refers to the specified data.
    """

def get_first_fcref_from(frm: int) -> ida_idaapi.ea_t: ...

def get_first_fcref_to(to: int) -> ida_idaapi.ea_t: ...

def get_next_cref_from(frm: int, current: int) -> ida_idaapi.ea_t: ...
    """Get next instruction referenced from the specified instruction. 
            
    @param current: linear address of current referenced instruction This value is returned by get_first_cref_from() or previous call to get_next_cref_from() functions.
    @returns next referenced address or BADADDR.
    """

def get_next_cref_to(to: int, current: int) -> ida_idaapi.ea_t: ...
    """Get next instruction referencing to the specified instruction. 
            
    @param to: linear address of referenced instruction
    @param current: linear address of current referenced instruction This value is returned by get_first_cref_to() or previous call to get_next_cref_to() functions.
    @returns linear address of the next referencing instruction or BADADDR.
    """

def get_next_dref_from(frm: int, current: int) -> ida_idaapi.ea_t: ...
    """Get next data referenced from the specified address. 
            
    @param current: linear address of current referenced data. This value is returned by get_first_dref_from() or previous call to get_next_dref_from() functions.
    @returns linear address of next data or BADADDR.
    """

def get_next_dref_to(to: int, current: int) -> ida_idaapi.ea_t: ...
    """Get address of instruction/data referencing to the specified data 
            
    @param to: linear address of referencing instruction or data
    @param current: current linear address. This value is returned by get_first_dref_to() or previous call to get_next_dref_to() functions.
    @returns BADADDR if nobody refers to the specified data.
    """

def get_next_fcref_from(frm: int, current: int) -> ida_idaapi.ea_t: ...

def get_next_fcref_to(to: int, current: int) -> ida_idaapi.ea_t: ...

def has_external_refs(pfn: func_t *, ea: int) -> bool: ...
    """Does 'ea' have references from outside of 'pfn'?
    
    """

def has_jump_or_flow_xref(ea: int) -> bool: ...
    """Are there jump or flow references to EA?
    
    """

def xrefchar(xrtype: char) -> char: ...
    """Get character describing the xref type. 
            
    @param xrtype: combination of Cross-Reference type flags and a cref_t of dref_t value
    """

SWIG_PYTHON_LEGACY_BOOL: int  # 1
XREF_ALL: int  # 0
XREF_BASE: int  # 128
XREF_CODE: int  # 4
XREF_DATA: int  # 2
XREF_EA: int  # 8
XREF_FAR: int  # 1
XREF_FLOW: int  # 0
XREF_MASK: int  # 31
XREF_NOFLOW: int  # 1
XREF_PASTEND: int  # 256
XREF_TAIL: int  # 64
XREF_TID: int  # 16
XREF_USER: int  # 32
dr_I: int  # 5
dr_O: int  # 1
dr_R: int  # 3
dr_S: int  # 6
dr_T: int  # 4
dr_U: int  # 0
dr_W: int  # 2
fl_CF: int  # 16
fl_CN: int  # 17
fl_F: int  # 21
fl_JF: int  # 18
fl_JN: int  # 19
fl_U: int  # 0
fl_USobsolete: int  # 20
ida_idaapi: module
weakref: module