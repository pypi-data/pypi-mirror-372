from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Functions that deal with fixup information.

A loader should setup fixup information using set_fixup(). 
    
"""

class fixup_data_t:
    @property
    def displacement(self) -> Any: ...
    @property
    def off(self) -> Any: ...
    @property
    def sel(self) -> Any: ...
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
    def calc_size(self) -> int: ...
        """calc_fixup_size()
        
        """
    def clr_extdef(self) -> None: ...
    def clr_unused(self) -> None: ...
    def get(self, source: int) -> bool: ...
        """get_fixup()
        
        """
    def get_base(self) -> ida_idaapi.ea_t: ...
        """Get base of fixup. 
                
        """
    def get_desc(self, source: int) -> str: ...
        """get_fixup_desc()
        
        """
    def get_flags(self) -> int: ...
        """Fixup flags Fixup flags.
        
        """
    def get_handler(self) -> fixup_handler_t const *: ...
        """get_fixup_handler()
        
        """
    def get_type(self) -> fixup_type_t: ...
        """Fixup type Types of fixups.
        
        """
    def get_value(self, ea: int) -> int: ...
        """get_fixup_value()
        
        """
    def has_base(self) -> bool: ...
        """Is fixup relative?
        
        """
    def is_custom(self) -> bool: ...
        """is_fixup_custom()
        
        """
    def is_extdef(self) -> bool: ...
    def is_unused(self) -> bool: ...
    def patch_value(self, ea: int) -> bool: ...
        """patch_fixup_value()
        
        """
    def set(self, source: int) -> None: ...
        """set_fixup()
        
        """
    def set_base(self, new_base: int) -> None: ...
        """Set base of fixup. The target should be set before a call of this function. 
                
        """
    def set_extdef(self) -> None: ...
    def set_sel(self, seg: segment_t const *) -> None: ...
    def set_target_sel(self) -> None: ...
        """Set selector of fixup to the target. The target should be set before a call of this function. 
                
        """
    def set_type(self, type_: fixup_type_t) -> None: ...
    def set_type_and_flags(self, type_: fixup_type_t, flags_: int = 0) -> None: ...
    def set_unused(self) -> None: ...
    def was_created(self) -> bool: ...
        """Is fixup artificial?
        
        """

class fixup_info_t:
    @property
    def ea(self) -> Any: ...
    @property
    def fd(self) -> Any: ...
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

def calc_fixup_size(type: fixup_type_t) -> int: ...
    """Calculate size of fixup in bytes (the number of bytes the fixup patches) 
            
    @retval -1: means error
    """

def contains_fixups(ea: int, size: asize_t) -> bool: ...
    """Does the specified address range contain any fixup information?
    
    """

def del_fixup(source: int) -> None: ...
    """Delete fixup information.
    
    """

def exists_fixup(source: int) -> bool: ...
    """Check that a fixup exists at the given address.
    
    """

def find_custom_fixup(name: str) -> fixup_type_t: ...

def gen_fix_fixups(_from: int, to: int, size: asize_t) -> None: ...
    """Relocate the bytes with fixup information once more (generic function). This function may be called from loader_t::move_segm() if it suits the goal. If loader_t::move_segm is not defined then this function will be called automatically when moving segments or rebasing the entire program. Special parameter values (from = BADADDR, size = 0, to = delta) are used when the function is called from rebase_program(delta). 
            
    """

def get_first_fixup_ea() -> ida_idaapi.ea_t: ...

def get_fixup(fd: fixup_data_t, source: int) -> bool: ...
    """Get fixup information.
    
    """

def get_fixup_desc(source: int, fd: fixup_data_t) -> str: ...
    """Get FIXUP description comment.
    
    """

def get_fixup_handler(type: fixup_type_t) -> fixup_handler_t const *: ...
    """Get handler of standard or custom fixup.
    
    """

def get_fixup_value(ea: int, type: fixup_type_t) -> int: ...
    """Get the operand value. This function get fixup bytes from data or an instruction at `ea` and convert them to the operand value (maybe partially). It is opposite in meaning to the `patch_fixup_value()`. For example, FIXUP_HI8 read a byte at `ea` and shifts it left by 8 bits, or AArch64's custom fixup BRANCH26 get low 26 bits of the insn at `ea` and shifts it left by 2 bits. This function is mainly used to get a relocation addend. 
            
    @param ea: address to get fixup bytes from, the size of the fixup bytes depends on the fixup type.
    @param type: fixup type
    @retval operand: value
    """

def get_fixups(out: fixups_t *, ea: int, size: asize_t) -> bool: ...

def get_next_fixup_ea(ea: int) -> ida_idaapi.ea_t: ...

def get_prev_fixup_ea(ea: int) -> ida_idaapi.ea_t: ...

def handle_fixups_in_macro(ri: refinfo_t, ea: int, other: fixup_type_t, macro_reft_and_flags: int) -> bool: ...
    """Handle two fixups in a macro. We often combine two instruction that load parts of a value into one macro instruction. For example: 
           ADRP  X0, #var@PAGE
               ADD   X0, X0, #var@PAGEOFF  --> ADRL X0, var
          lui   $v0, %hi(var)
               addiu $v0, $v0, %lo(var)    --> la   $v0, var
    
    
            
    @returns success ('false' means that RI was not changed)
    """

def is_fixup_custom(type: fixup_type_t) -> bool: ...
    """Is fixup processed by processor module?
    
    """

def patch_fixup_value(ea: int, fd: fixup_data_t) -> bool: ...
    """Patch the fixup bytes. This function updates data or an instruction at `ea` to the fixup bytes. For example, FIXUP_HI8 updates a byte at `ea` to the high byte of `fd->off`, or AArch64's custom fixup BRANCH26 updates low 26 bits of the insn at `ea` to the value of `fd->off` shifted right by 2. 
            
    @param ea: address where data are changed, the size of the changed data depends on the fixup type.
    @param fd: fixup data
    @retval false: the fixup bytes do not fit (e.g. `fd->off` is greater than 0xFFFFFFC for BRANCH26). The database is changed even in this case.
    """

def set_fixup(source: int, fd: fixup_data_t) -> None: ...
    """Set fixup information. You should fill fixup_data_t and call this function and the kernel will remember information in the database. 
            
    @param source: the fixup source address, i.e. the address modified by the fixup
    @param fd: fixup data
    """

FIXUPF_CREATED: int  # 8
FIXUPF_EXTDEF: int  # 2
FIXUPF_LOADER_MASK: int  # -268435456
FIXUPF_REL: int  # 1
FIXUPF_UNUSED: int  # 4
FIXUP_CUSTOM: int  # 32768
FIXUP_HI16: int  # 7
FIXUP_HI8: int  # 6
FIXUP_LOW16: int  # 9
FIXUP_LOW8: int  # 8
FIXUP_OFF16: int  # 1
FIXUP_OFF16S: int  # 15
FIXUP_OFF32: int  # 4
FIXUP_OFF32S: int  # 16
FIXUP_OFF64: int  # 12
FIXUP_OFF8: int  # 13
FIXUP_OFF8S: int  # 14
FIXUP_PTR16: int  # 3
FIXUP_PTR32: int  # 5
FIXUP_SEG16: int  # 2
SWIG_PYTHON_LEGACY_BOOL: int  # 1
V695_FIXUP_VHIGH: int  # 10
V695_FIXUP_VLOW: int  # 11
ida_idaapi: module
weakref: module