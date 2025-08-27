from typing import Any, Optional, List, Dict, Tuple, Callable, Union

class reg_value_def_t:
    NOVAL: int  # 0
    SPVAL: int  # 2
    UVAL: int  # 1
    @property
    def LIKE_GOT(self) -> Any: ...
    @property
    def PC_BASED(self) -> Any: ...
    @property
    def SHORT_INSN(self) -> Any: ...
    @property
    def def_ea(self) -> Any: ...
    @property
    def def_itype(self) -> Any: ...
    @property
    def flags(self) -> Any: ...
    @property
    def val(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: reg_value_def_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> Any: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> Any: ...
        """Return self>value."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> Any: ...
        """Return self<=value."""
    def __lt__(self, r: reg_value_def_t) -> bool: ...
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
    def __str__(self) -> str: ...
        """Return str(self)."""
    def __subclasshook__(self, *args: Any, **kwargs: Any) -> Any: ...
        """Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.__subclasscheck__().
        It should return True, False or NotImplemented.  If it returns
        NotImplemented, the normal algorithm is used.  Otherwise, it
        overrides the normal algorithm (and the outcome is cached).
        
        """
    def __swig_destroy__(self, *args: Any, **kwargs: Any) -> Any: ...
    def dstr(self, how: reg_value_def_t::dstr_val_t, pm: procmod_t = None) -> str: ...
        """Return the string representation.
        
        """
    def is_like_got(self) -> bool: ...
    def is_pc_based(self) -> bool: ...
    def is_short_insn(self, args: Any) -> bool: ...
        """This function has the following signatures:
        
            0. is_short_insn() -> bool
            1. is_short_insn(insn: const insn_t &) -> bool
        
        # 0: is_short_insn() -> bool
        
        
        # 1: is_short_insn(insn: const insn_t &) -> bool
        
        
        """

class reg_value_info_t:
    ADD: int  # 0
    AND: int  # 3
    AND_NOT: int  # 5
    CONTAINED: int  # 2
    CONTAINS: int  # 1
    EQUAL: int  # 0
    MOVT: int  # 8
    NEG: int  # 9
    NOT: int  # 10
    NOT_COMPARABLE: int  # 3
    OR: int  # 2
    SLL: int  # 6
    SLR: int  # 7
    SUB: int  # 1
    XOR: int  # 4
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
    def __getitem__(self, i: size_t) -> reg_value_def_t: ...
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
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> bool: ...
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
    def __str__(self) -> str: ...
    def __subclasshook__(self, *args: Any, **kwargs: Any) -> Any: ...
        """Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.__subclasscheck__().
        It should return True, False or NotImplemented.  If it returns
        NotImplemented, the normal algorithm is used.  Otherwise, it
        overrides the normal algorithm (and the outcome is cached).
        
        """
    def __swig_destroy__(self, *args: Any, **kwargs: Any) -> Any: ...
    def aborted(self) -> bool: ...
        """Return 'true' if the tracking process was aborted.
        
        """
    def add(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Add R to the value, save INSN as a defining instruction. 
                
        """
    def add_num(self, args: Any) -> None: ...
        """This function has the following signatures:
        
            0. add_num(r: int, insn: const insn_t &) -> None
            1. add_num(r: int) -> None
        
        # 0: add_num(r: int, insn: const insn_t &) -> None
        
        Add R to the value, save INSN as a defining instruction. 
                
        
        # 1: add_num(r: int) -> None
        
        Add R to the value, do not change the defining instructions. 
                
        
        """
    def band(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Make bitwise AND of R to the value, save INSN as a defining instruction. 
                
        """
    def bandnot(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Make bitwise AND of the inverse of R to the value, save INSN as a defining instruction. 
                
        """
    def bnot(self, insn: insn_t const &) -> None: ...
        """Make bitwise inverse of the value, save INSN as a defining instruction. 
                
        """
    def bor(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Make bitwise OR of R to the value, save INSN as a defining instruction. 
                
        """
    def bxor(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Make bitwise eXclusive OR of R to the value, save INSN as a defining instruction. 
                
        """
    def clear(self) -> None: ...
        """Undefine the value.
        
        """
    def empty(self) -> bool: ...
        """Return 'true' if we know nothing about a value.
        
        """
    def extend(self, pm: procmod_t, width: int, is_signed: bool) -> None: ...
        """Sign-, or zero-extend the number or SP delta value to full size. The initial value is considered to be of size WIDTH. 
                
        """
    def get_def_ea(self) -> ida_idaapi.ea_t: ...
        """Return the defining address.
        
        """
    def get_def_itype(self) -> uint16: ...
        """Return the defining instruction code (processor specific).
        
        """
    def get_num(self) -> bool: ...
        """Return the number if the value is a constant. 
                
        """
    def get_spd(self) -> bool: ...
        """Return the SP delta if the value depends on the stack pointer. 
                
        """
    def has_any_vals_flag(self, val_flags: uint16) -> bool: ...
    def have_all_vals_flag(self, val_flags: uint16) -> bool: ...
        """Check the given flag for each value.
        
        """
    def is_all_vals_like_got(self) -> bool: ...
    def is_all_vals_pc_based(self) -> bool: ...
    def is_any_vals_like_got(self) -> bool: ...
    def is_any_vals_pc_based(self) -> bool: ...
    def is_badinsn(self) -> bool: ...
        """Return 'true' if the value is unknown because of a bad insn.
        
        """
    def is_dead_end(self) -> bool: ...
        """Return 'true' if the value is undefined because of a dead end.
        
        """
    def is_known(self) -> bool: ...
        """Return 'true' if the value is known (i.e. it is a number or SP delta).
        
        """
    def is_num(self) -> bool: ...
        """Return 'true' if the value is a constant.
        
        """
    def is_spd(self) -> bool: ...
        """Return 'true' if the value depends on the stack pointer.
        
        """
    def is_special(self) -> bool: ...
        """Return 'true' if the value requires special handling.
        
        """
    def is_unkfunc(self) -> bool: ...
        """Return 'true' if the value is unknown from the function start.
        
        """
    def is_unkinsn(self) -> bool: ...
        """Return 'true' if the value is unknown after executing the insn.
        
        """
    def is_unkloop(self) -> bool: ...
        """Return 'true' if the value is unknown because it changes in a loop.
        
        """
    def is_unkmult(self) -> bool: ...
        """Return 'true' if the value is unknown because the register has incompatible values (a number and SP delta). 
                
        """
    def is_unknown(self) -> bool: ...
        """Return 'true' if the value is unknown.
        
        """
    def is_unkvals(self) -> bool: ...
        """Return 'true' if the value is unknown because the register has too many values. 
                
        """
    def is_unkxref(self) -> bool: ...
        """Return 'true' if the value is unknown because there are too many xrefs.
        
        """
    def is_value_unique(self) -> bool: ...
        """Check that the value is unique.
        
        """
    def make_aborted(self, bblk_ea: int) -> reg_value_info_t: ...
        """Return the value after aborting. 
                
        """
    def make_badinsn(self, insn_ea: int) -> reg_value_info_t: ...
        """Return the unknown value after a bad insn. 
                
        """
    def make_dead_end(self, dead_end_ea: int) -> reg_value_info_t: ...
        """Return the undefined value because of a dead end. 
                
        """
    def make_initial_sp(self, func_ea: int) -> reg_value_info_t: ...
        """Return the value that is the initial stack pointer. 
                
        """
    def make_num(self, args: Any) -> reg_value_info_t: ...
        """This function has the following signatures:
        
            0. make_num(rval: int, insn: const insn_t &, val_flags: uint16=0) -> reg_value_info_t
            1. make_num(rval: int, val_ea: ida_idaapi.ea_t, val_flags: uint16=0) -> reg_value_info_t
        
        # 0: make_num(rval: int, insn: const insn_t &, val_flags: uint16=0) -> reg_value_info_t
        
        Return the value that is the RVAL number. 
                
        
        # 1: make_num(rval: int, val_ea: ida_idaapi.ea_t, val_flags: uint16=0) -> reg_value_info_t
        
        Return the value that is the RVAL number. 
                
        
        """
    def make_unkfunc(self, func_ea: int) -> reg_value_info_t: ...
        """Return the unknown value from the function start. 
                
        """
    def make_unkinsn(self, insn: insn_t const &) -> reg_value_info_t: ...
        """Return the unknown value after executing the insn. 
                
        """
    def make_unkloop(self, bblk_ea: int) -> reg_value_info_t: ...
        """Return the unknown value if it changes in a loop. 
                
        """
    def make_unkmult(self, bblk_ea: int) -> reg_value_info_t: ...
        """Return the unknown value if the register has incompatible values. 
                
        """
    def make_unkvals(self, bblk_ea: int) -> reg_value_info_t: ...
        """Return the unknown value if the register has too many values. 
                
        """
    def make_unkxref(self, bblk_ea: int) -> reg_value_info_t: ...
        """Return the unknown value if there are too many xrefs. 
                
        """
    def movt(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Replace the top 16 bits with bottom 16 bits of R, leaving the bottom 16 bits untouched, save INSN as a defining instruction. 
                
        """
    def neg(self, insn: insn_t const &) -> None: ...
        """Negate the value, save INSN as a defining instruction.
        
        """
    def set_aborted(self, bblk_ea: int) -> None: ...
        """Set the value after aborting. 
                
        """
    def set_all_vals_flag(self, val_flags: uint16) -> None: ...
        """Set the given flag for each value.
        
        """
    def set_all_vals_got_based(self) -> None: ...
    def set_all_vals_pc_based(self) -> None: ...
    def set_badinsn(self, insn_ea: int) -> None: ...
        """Set the value to be unknown after a bad insn. 
                
        """
    def set_dead_end(self, dead_end_ea: int) -> None: ...
        """Set the value to be undefined because of a dead end. 
                
        """
    def set_num(self, args: Any) -> None: ...
        """This function has the following signatures:
        
            0. set_num(rval: int, insn: const insn_t &, val_flags: uint16=0) -> None
            1. set_num(rvals: uvalvec_t *, insn: const insn_t &) -> None
            2. set_num(rval: int, val_ea: ida_idaapi.ea_t, val_flags: uint16=0) -> None
        
        # 0: set_num(rval: int, insn: const insn_t &, val_flags: uint16=0) -> None
        
        Set the value to be a number after executing an insn. 
                
        
        # 1: set_num(rvals: uvalvec_t *, insn: const insn_t &) -> None
        
        Set the value to be numbers after executing an insn. 
                
        
        # 2: set_num(rval: int, val_ea: ida_idaapi.ea_t, val_flags: uint16=0) -> None
        
        Set the value to be a number before an address. 
                
        
        """
    def set_unkfunc(self, func_ea: int) -> None: ...
        """Set the value to be unknown from the function start. 
                
        """
    def set_unkinsn(self, insn: insn_t const &) -> None: ...
        """Set the value to be unknown after executing the insn. 
                
        """
    def set_unkloop(self, bblk_ea: int) -> None: ...
        """Set the value to be unknown because it changes in a loop. 
                
        """
    def set_unkmult(self, bblk_ea: int) -> None: ...
        """Set the value to be unknown because the register has incompatible values. 
                
        """
    def set_unkvals(self, bblk_ea: int) -> None: ...
        """Set the value to be unknown because the register has too many values. 
                
        """
    def set_unkxref(self, bblk_ea: int) -> None: ...
        """Set the value to be unknown because there are too many xrefs. 
                
        """
    def shift_left(self, r: int) -> None: ...
        """Shift the value left by R, do not change the defining instructions. 
                
        """
    def shift_right(self, r: int) -> None: ...
        """Shift the value right by R, do not change the defining instructions. 
                
        """
    def sll(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Shift the value left by R, save INSN as a defining instruction. 
                
        """
    def slr(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Shift the value right by R, save INSN as a defining instruction. 
                
        """
    def sub(self, r: reg_value_info_t, insn: insn_t const &) -> None: ...
        """Subtract R from the value, save INSN as a defining instruction. 
                
        """
    def swap(self, r: reg_value_info_t) -> None: ...
    def trunc_uval(self, pm: procmod_t) -> None: ...
        """Truncate the number to the application bitness. 
                
        """
    def vals_union(self, r: reg_value_info_t) -> reg_value_info_t: ...
        """Add values from R into THIS ignoring duplicates. 
                
        @retval EQUAL: THIS is not changed
        @retval CONTAINS: THIS is not changed
        @retval CONTAINED: THIS is a copy of R
        @retval NOT_COMPARABLE: values from R are added to THIS
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

def find_nearest_rvi(rvi: reg_value_info_t, ea: int, reg: int const [2]) -> int: ...
    """Find the value of any of the two registers using the register tracker. First, this function tries to find the registers in the basic block of EA, and if it could not do this, then it tries to find in the entire function. 
            
    @param rvi: the found value with additional attributes
    @param ea: the address to find a value at
    @param reg: the registers to find
    @returns the index of the found register or -1
    """

def find_reg_value(ea: int, reg: int) -> uint64 *: ...
    """Find register value using the register tracker. 
            
    @param ea: the address to find a value at
    @param reg: the register to find
    @retval 0: no value (the value is varying or the find depth is not enough to find a value)
    @retval 1: the found value is in VAL
    @retval -1: the processor module does not support a register tracker
    """

def find_reg_value_info(rvi: reg_value_info_t, ea: int, reg: int, max_depth: int = 0) -> bool: ...
    """Find register value using the register tracker. 
            
    @param rvi: the found value with additional attributes
    @param ea: the address to find a value at
    @param reg: the register to find
    @param max_depth: the number of basic blocks to look before aborting the search and returning the unknown value. 0 means the value of REGTRACK_MAX_DEPTH from ida.cfg for ordinal registers or REGTRACK_FUNC_MAX_DEPTH for the function-wide registers, -1 means the value of REGTRACK_FUNC_MAX_DEPTH from ida.cfg.
    @retval 'false': the processor module does not support a register tracker
    @retval 'true': the found value is in RVI
    """

def find_sp_value(ea: int, reg: int = -1) -> int64 *: ...
    """Find a value of the SP based register using the register tracker. 
            
    @param ea: the address to find a value at
    @param reg: the register to find. by default the SP register is used.
    @retval 0: no value (the value is varying or the find depth is not enough to find a value)
    @retval 1: the found value is in VAL
    @retval -1: the processor module does not support a register tracker
    """

def invalidate_regfinder_cache(args: Any) -> None: ...
    """The control flow from FROM to TO has changed. Remove from the register tracker cache all values at TO and all dependent values. if TO == BADADDR then clear the entire cache. 
            
    """

SWIG_PYTHON_LEGACY_BOOL: int  # 1
cvar: swigvarlink
ida_idaapi: module
weakref: module