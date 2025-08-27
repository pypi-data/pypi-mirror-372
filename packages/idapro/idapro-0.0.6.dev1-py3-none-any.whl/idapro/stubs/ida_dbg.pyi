from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Contains functions to control the debugging of a process.

See Debugger functions for a complete explanation of these functions.
These functions are inlined for the kernel. They are not inlined for the user-interfaces. 
    
"""

class DBG_Hooks:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __disown__(self) -> Any: ...
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, _flags: int = 0, _hkcb_flags: int = 1) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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
    def dbg_bpt(self, tid: thid_t, bptea: int) -> int: ...
        """A user defined breakpoint was reached. 
                  
        @param tid: (thid_t)
        @param bptea: (::ea_t)
        """
    def dbg_bpt_changed(self, bptev_code: int, bpt: bpt_t) -> None: ...
        """Breakpoint has been changed. 
                  
        @param bptev_code: (int) Breakpoint modification events
        @param bpt: (bpt_t *)
        """
    def dbg_exception(self, pid: pid_t, tid: thid_t, ea: int, exc_code: int, exc_can_cont: bool, exc_ea: int, exc_info: str) -> int: ...
    def dbg_finished_loading_bpts(self) -> None: ...
        """Finished loading breakpoint info from idb.
        
        """
    def dbg_information(self, pid: pid_t, tid: thid_t, ea: int, info: str) -> None: ...
    def dbg_library_load(self, pid: pid_t, tid: thid_t, ea: int, modinfo_name: str, modinfo_base: int, modinfo_size: asize_t) -> None: ...
    def dbg_library_unload(self, pid: pid_t, tid: thid_t, ea: int, info: str) -> None: ...
    def dbg_process_attach(self, pid: pid_t, tid: thid_t, ea: int, modinfo_name: str, modinfo_base: int, modinfo_size: asize_t) -> None: ...
    def dbg_process_detach(self, pid: pid_t, tid: thid_t, ea: int) -> None: ...
    def dbg_process_exit(self, pid: pid_t, tid: thid_t, ea: int, exit_code: int) -> None: ...
    def dbg_process_start(self, pid: pid_t, tid: thid_t, ea: int, modinfo_name: str, modinfo_base: int, modinfo_size: asize_t) -> None: ...
    def dbg_request_error(self, failed_command: int, failed_dbg_notification: int) -> None: ...
        """An error occurred during the processing of a request. 
                  
        @param failed_command: (ui_notification_t)
        @param failed_dbg_notification: (dbg_notification_t)
        """
    def dbg_run_to(self, pid: pid_t, tid: thid_t, ea: int) -> None: ...
    def dbg_started_loading_bpts(self) -> None: ...
        """Started loading breakpoint info from idb.
        
        """
    def dbg_step_into(self) -> None: ...
    def dbg_step_over(self) -> None: ...
    def dbg_step_until_ret(self) -> None: ...
    def dbg_suspend_process(self) -> None: ...
        """The process is now suspended. 
                  
        """
    def dbg_thread_exit(self, pid: pid_t, tid: thid_t, ea: int, exit_code: int) -> None: ...
    def dbg_thread_start(self, pid: pid_t, tid: thid_t, ea: int) -> None: ...
    def dbg_trace(self, tid: thid_t, ip: int) -> int: ...
        """A step occurred (one instruction was executed). This event notification is only generated if step tracing is enabled. 
                  
        @param tid: (thid_t) thread ID
        @param ip: (::ea_t) current instruction pointer. usually points after the executed instruction
        @retval 1: do not log this trace event
        @retval 0: log it
        """
    def hook(self) -> bool: ...
    def unhook(self) -> bool: ...

class bpt_location_t:
    @property
    def index(self) -> Any: ...
    @property
    def info(self) -> Any: ...
    @property
    def loctype(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: bpt_location_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, r: bpt_location_t) -> bool: ...
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, r: bpt_location_t) -> bool: ...
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, r: bpt_location_t) -> bool: ...
    def __lt__(self, r: bpt_location_t) -> bool: ...
    def __ne__(self, r: bpt_location_t) -> bool: ...
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
    def compare(self, r: bpt_location_t) -> int: ...
        """Lexically compare two breakpoint locations. Bpt locations are first compared based on type (i.e. BPLT_ABS < BPLT_REL). BPLT_ABS locations are compared based on their ea values. For all other location types, locations are first compared based on their string (path/filename/symbol), then their offset/lineno. 
                
        """
    def ea(self) -> ida_idaapi.ea_t: ...
        """Get address (BPLT_ABS)
        
        """
    def is_empty_path(self) -> bool: ...
        """No path/filename specified? (BPLT_REL, BPLT_SRC)
        
        """
    def lineno(self) -> int: ...
        """Get line number (BPLT_SRC)
        
        """
    def offset(self) -> int: ...
        """Get offset (BPLT_REL, BPLT_SYM)
        
        """
    def path(self) -> str: ...
        """Get path/filename (BPLT_REL, BPLT_SRC)
        
        """
    def set_abs_bpt(self, a: int) -> None: ...
        """Specify an absolute address location.
        
        """
    def set_rel_bpt(self, mod: str, _offset: int) -> None: ...
        """Specify a relative address location.
        
        """
    def set_src_bpt(self, fn: str, _lineno: int) -> None: ...
        """Specify a source level location.
        
        """
    def set_sym_bpt(self, _symbol: str, _offset: int = 0) -> None: ...
        """Specify a symbolic location.
        
        """
    def symbol(self) -> str: ...
        """Get symbol name (BPLT_SYM)
        
        """
    def type(self) -> bpt_loctype_t: ...
        """Get bpt type.
        
        """

class bpt_t:
    @property
    def bptid(self) -> Any: ...
    @property
    def cb(self) -> Any: ...
    @property
    def cndidx(self) -> Any: ...
    @property
    def condition(self) -> Any: ...
    @property
    def ea(self) -> Any: ...
    @property
    def elang(self) -> Any: ...
    @property
    def flags(self) -> Any: ...
    @property
    def loc(self) -> Any: ...
    @property
    def pass_count(self) -> Any: ...
    @property
    def pid(self) -> Any: ...
    @property
    def props(self) -> Any: ...
    @property
    def size(self) -> Any: ...
    @property
    def tid(self) -> Any: ...
    @property
    def type(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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
    def badbpt(self) -> bool: ...
        """Failed to write bpt to process memory?
        
        """
    def enabled(self) -> bool: ...
        """Is breakpoint enabled?
        
        """
    def get_cnd_elang_idx(self) -> int: ...
    def get_size(self) -> int: ...
        """Get bpt size.
        
        """
    def is_absbpt(self) -> bool: ...
        """Is absolute address breakpoint?
        
        """
    def is_active(self) -> bool: ...
        """Written completely to process?
        
        """
    def is_compiled(self) -> bool: ...
        """Condition has been compiled? 
                
        """
    def is_hwbpt(self) -> bool: ...
        """Is hardware breakpoint?
        
        """
    def is_inactive(self) -> bool: ...
        """Not written to process at all?
        
        """
    def is_low_level(self) -> bool: ...
        """Is bpt condition calculated at low level?
        
        """
    def is_page_bpt(self) -> bool: ...
        """Page breakpoint?
        
        """
    def is_partially_active(self) -> bool: ...
        """Written partially to process?
        
        """
    def is_relbpt(self) -> bool: ...
        """Is relative address breakpoint?
        
        """
    def is_srcbpt(self) -> bool: ...
        """Is source level breakpoint?
        
        """
    def is_symbpt(self) -> bool: ...
        """Is symbolic breakpoint?
        
        """
    def is_tracemodebpt(self) -> bool: ...
        """Does breakpoint trace anything?
        
        """
    def is_traceoffbpt(self) -> bool: ...
        """Is this a tracing breakpoint, and is tracing disabled?
        
        """
    def is_traceonbpt(self) -> bool: ...
        """Is this a tracing breakpoint, and is tracing enabled?
        
        """
    def listbpt(self) -> bool: ...
        """Include in the bpt list?
        
        """
    def set_abs_bpt(self, a: int) -> None: ...
        """Set bpt location to an absolute address.
        
        """
    def set_rel_bpt(self, mod: str, o: int) -> None: ...
        """Set bpt location to a relative address.
        
        """
    def set_src_bpt(self, fn: str, lineno: int) -> None: ...
        """Set bpt location to a source line.
        
        """
    def set_sym_bpt(self, sym: str, o: int) -> None: ...
        """Set bpt location to a symbol.
        
        """
    def set_trace_action(self, enable: bool, trace_types: int) -> bool: ...
        """Configure tracing options.
        
        """

class bpt_vec_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> memreg_info_t: ...
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __iter__(self) -> Any: ...
        """Helper function, to be set as __iter__ method for qvector-, or array-based classes."""
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> bool: ...
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
    def __setitem__(self, i: size_t, v: bpt_t) -> None: ...
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
    def append(self, x: bpt_t) -> None: ...
    def at(self, _idx: size_t) -> memreg_info_t: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< memreg_info_t >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< memreg_info_t >: ...
    def erase(self, args: Any) -> qvector< memreg_info_t >: ...
    def extend(self, x: bpt_vec_t) -> None: ...
    def extract(self) -> memreg_info_t *: ...
    def front(self) -> Any: ...
    def grow(self, args: Any) -> None: ...
    def inject(self, s: bpt_t, len: size_t) -> None: ...
    def insert(self, it: bpt_t, x: bpt_t) -> qvector< memreg_info_t >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> memreg_info_t &: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: bpt_vec_t) -> None: ...
    def truncate(self) -> None: ...

class bptaddrs_t:
    @property
    def bpt(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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

class eval_ctx_t:
    @property
    def ea(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, _ea: int) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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

class memreg_info_t:
    @property
    def bytes(self) -> Any: ...
    @property
    def ea(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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
    def get_bytes(self) -> PyObject *: ...

class memreg_infos_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> memreg_info_t: ...
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __iter__(self) -> Any: ...
        """Helper function, to be set as __iter__ method for qvector-, or array-based classes."""
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> bool: ...
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
    def __setitem__(self, i: size_t, v: memreg_info_t) -> None: ...
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
    def append(self, x: memreg_info_t) -> None: ...
    def at(self, _idx: size_t) -> memreg_info_t: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< memreg_info_t >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< memreg_info_t >: ...
    def erase(self, args: Any) -> qvector< memreg_info_t >: ...
    def extend(self, x: memreg_infos_t) -> None: ...
    def extract(self) -> memreg_info_t *: ...
    def front(self) -> Any: ...
    def grow(self, args: Any) -> None: ...
    def inject(self, s: memreg_info_t, len: size_t) -> None: ...
    def insert(self, it: memreg_info_t, x: memreg_info_t) -> qvector< memreg_info_t >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> memreg_info_t &: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: memreg_infos_t) -> None: ...
    def truncate(self) -> None: ...

class tev_info_reg_t:
    @property
    def info(self) -> Any: ...
    @property
    def registers(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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

class tev_info_t:
    @property
    def ea(self) -> Any: ...
    @property
    def tid(self) -> Any: ...
    @property
    def type(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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

class tev_reg_value_t:
    @property
    def reg_idx(self) -> Any: ...
    @property
    def value(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __lt__(self, value: Any) -> bool: ...
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

class tev_reg_values_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> memreg_info_t: ...
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __iter__(self) -> Any: ...
        """Helper function, to be set as __iter__ method for qvector-, or array-based classes."""
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> bool: ...
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
    def __setitem__(self, i: size_t, v: tev_reg_value_t) -> None: ...
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
    def append(self, x: tev_reg_value_t) -> None: ...
    def at(self, _idx: size_t) -> memreg_info_t: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< memreg_info_t >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< memreg_info_t >: ...
    def erase(self, args: Any) -> qvector< memreg_info_t >: ...
    def extend(self, x: tev_reg_values_t) -> None: ...
    def extract(self) -> memreg_info_t *: ...
    def front(self) -> Any: ...
    def grow(self, args: Any) -> None: ...
    def inject(self, s: tev_reg_value_t, len: size_t) -> None: ...
    def insert(self, it: tev_reg_value_t, x: tev_reg_value_t) -> qvector< memreg_info_t >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> memreg_info_t &: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: tev_reg_values_t) -> None: ...
    def truncate(self) -> None: ...

class tevinforeg_vec_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, value: Any) -> bool: ...
        """Return self==value."""
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> memreg_info_t: ...
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
    def __hash__(self) -> Any: ...
        """Return hash(self)."""
    def __init__(self, args: Any) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __iter__(self) -> Any: ...
        """Helper function, to be set as __iter__ method for qvector-, or array-based classes."""
    def __le__(self, value: Any) -> bool: ...
        """Return self<=value."""
    def __len__(self) -> int: ...
    def __lt__(self, value: Any) -> bool: ...
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
    def __setitem__(self, i: size_t, v: tev_info_reg_t) -> None: ...
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
    def append(self, x: tev_info_reg_t) -> None: ...
    def at(self, _idx: size_t) -> memreg_info_t: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< memreg_info_t >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< memreg_info_t >: ...
    def erase(self, args: Any) -> qvector< memreg_info_t >: ...
    def extend(self, x: tevinforeg_vec_t) -> None: ...
    def extract(self) -> memreg_info_t *: ...
    def front(self) -> Any: ...
    def grow(self, args: Any) -> None: ...
    def inject(self, s: tev_info_reg_t, len: size_t) -> None: ...
    def insert(self, it: tev_info_reg_t, x: tev_info_reg_t) -> qvector< memreg_info_t >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> memreg_info_t &: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: tevinforeg_vec_t) -> None: ...
    def truncate(self) -> None: ...

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

def add_bpt(args: Any) -> bool: ...
    """This function has the following signatures:
    
        0. add_bpt(ea: ida_idaapi.ea_t, size: asize_t=0, type: bpttype_t=BPT_DEFAULT) -> bool
        1. add_bpt(bpt: const bpt_t &) -> bool
    
    # 0: add_bpt(ea: ida_idaapi.ea_t, size: asize_t=0, type: bpttype_t=BPT_DEFAULT) -> bool
    
    Add a new breakpoint in the debugged process. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    
    # 1: add_bpt(bpt: const bpt_t &) -> bool
    
    Add a new breakpoint in the debugged process. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    
    """

def add_path_mapping(src: str, dst: str) -> None: ...

def add_virt_module(mod: modinfo_t) -> bool: ...

def attach_process(args: Any) -> int: ...
    """Attach the debugger to a running process. \sq{Type, Asynchronous function - available as Request, Notification, dbg_process_attach} 
            
    @param pid: PID of the process to attach to. If NO_PROCESS, a dialog box will interactively ask the user for the process to attach to.
    @param event_id: event to trigger upon attaching
    @retval -4: debugger was not inited
    @retval -3: the attaching is not supported
    @retval -2: impossible to find a compatible process
    @retval -1: impossible to attach to the given process (process died, privilege needed, not supported by the debugger plugin, ...)
    @retval 0: the user cancelled the attaching to the process
    @retval 1: the debugger properly attached to the process
    """

def bring_debugger_to_front() -> None: ...

def check_bpt(ea: int) -> int: ...
    """Check the breakpoint at the specified address. 
            
    @returns one of Breakpoint status codes
    """

def choose_trace_file() -> str: ...
    """Show the choose trace dialog.
    
    """

def clear_requests_queue() -> None: ...
    """Clear the queue of waiting requests. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def clear_trace() -> None: ...
    """Clear all events in the trace buffer. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    """

def collect_stack_trace(tid: thid_t, trace: call_stack_t) -> bool: ...

def continue_backwards() -> bool: ...
    """Continue the execution of the process in the debugger backwards. Can only be used with debuggers that support time-travel debugging. \sq{Type, Synchronous function - available as Request, Notification, none (synchronous function)} 
            
    """

def continue_process() -> bool: ...
    """Continue the execution of the process in the debugger. \sq{Type, Synchronous function - available as Request, Notification, none (synchronous function)} 
            
    """

def create_source_viewer(out_ccv: TWidget **, parent: TWidget *, custview: TWidget *, sf: source_file_ptr, lines: strvec_t *, lnnum: int, colnum: int, flags: int) -> source_view_t *: ...
    """Create a source code view.
    
    """

def dbg_add_bpt_tev(tid: thid_t, ea: int, bp: int) -> bool: ...
    """Add a new breakpoint trace element to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns false if the operation failed, true otherwise
    """

def dbg_add_call_tev(tid: thid_t, caller: int, callee: int) -> None: ...
    """Add a new call trace element to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_add_debug_event(event: debug_event_t) -> None: ...
    """Add a new debug event to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_add_insn_tev(tid: thid_t, ea: int, save: save_reg_values_t = 1) -> bool: ...
    """Add a new instruction trace element to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns false if the operation failed, true otherwise
    """

def dbg_add_many_tevs(new_tevs: tevinforeg_vec_t) -> bool: ...
    """Add many new trace elements to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns false if the operation failed for any tev_info_t object
    """

def dbg_add_ret_tev(tid: thid_t, ret_insn: int, return_to: int) -> None: ...
    """Add a new return trace element to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_add_tev(type: tev_type_t, tid: thid_t, address: int) -> None: ...
    """Add a new trace element to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_add_thread(tid: thid_t) -> None: ...
    """Add a thread to the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_bin_search(start_ea: int, end_ea: int, data: compiled_binpat_vec_t const &, srch_flags: int) -> str: ...

def dbg_can_query() -> Any: ...
    """This function can be used to check if the debugger can be queried:
      - debugger is loaded
      - process is suspended
      - process is not suspended but can take requests. In this case some requests like
        memory read/write, bpt management succeed and register querying will fail.
        Check if idaapi.get_process_state() < 0 to tell if the process is suspended
    
    @return: Boolean
    """

def dbg_del_thread(tid: thid_t) -> None: ...
    """Delete a thread from the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def dbg_is_loaded() -> Any: ...
    """Checks if a debugger is loaded
    
    @return: Boolean
    """

def define_exception(code: uint, name: str, desc: str, flags: int) -> str: ...
    """Convenience function: define new exception code. 
            
    @param code: exception code (cannot be 0)
    @param name: exception name (cannot be empty or nullptr)
    @param desc: exception description (maybe nullptr)
    @param flags: combination of Exception info flags
    @returns failure message or nullptr. You must call store_exceptions() if this function succeeds
    """

def del_bpt(args: Any) -> bool: ...
    """This function has the following signatures:
    
        0. del_bpt(ea: ida_idaapi.ea_t) -> bool
        1. del_bpt(bptloc: const bpt_location_t &) -> bool
    
    # 0: del_bpt(ea: ida_idaapi.ea_t) -> bool
    
    Delete an existing breakpoint in the debugged process. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    
    # 1: del_bpt(bptloc: const bpt_location_t &) -> bool
    
    Delete an existing breakpoint in the debugged process. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    
    """

def del_bptgrp(name: str) -> bool: ...
    """Delete a folder, bpt that were part of this folder are moved to the root folder \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param name: full path to the folder to be deleted
    @returns success
    """

def del_virt_module(base: ea_t const) -> bool: ...

def detach_process() -> bool: ...
    """Detach the debugger from the debugged process. \sq{Type, Asynchronous function - available as Request, Notification, dbg_process_detach} 
            
    """

def diff_trace_file(NONNULL_filename: str) -> bool: ...
    """Show difference between the current trace and the one from 'filename'.
    
    """

def disable_bblk_trace() -> bool: ...

def disable_bpt(args: Any) -> bool: ...

def disable_func_trace() -> bool: ...

def disable_insn_trace() -> bool: ...

def disable_step_trace() -> bool: ...

def edit_manual_regions() -> None: ...

def enable_bblk_trace(enable: bool = True) -> bool: ...

def enable_bpt(args: Any) -> bool: ...

def enable_bptgrp(bptgrp_name: str, enable: bool = True) -> int: ...
    """Enable (or disable) all bpts in a folder \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bptgrp_name: absolute path to the folder
    @param enable: by default true, enable bpts, false disable bpts
    @retval -1: an error occured
    @retval 0: no changes
    @retval >0: nubmers of bpts udpated
    """

def enable_func_trace(enable: bool = True) -> bool: ...

def enable_insn_trace(enable: bool = True) -> bool: ...

def enable_manual_regions(enable: bool) -> None: ...

def enable_step_trace(enable: int = 1) -> bool: ...

def exist_bpt(ea: int) -> bool: ...
    """Does a breakpoint exist at the given location?
    
    """

def exit_process() -> bool: ...
    """Terminate the debugging of the current process. \sq{Type, Asynchronous function - available as Request, Notification, dbg_process_exit} 
            
    """

def find_bpt(bptloc: bpt_location_t, bpt: bpt_t) -> bool: ...
    """Find a breakpoint by location. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    @param bptloc: Breakpoint location
    @param bpt: bpt is filled if the breakpoint was found
    """

def get_bblk_trace_options() -> int: ...
    """Get current basic block tracing options. Also see BT_LOG_INSTS \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_bpt(ea: int, bpt: bpt_t) -> bool: ...
    """Get the characteristics of a breakpoint. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param ea: any address in the breakpoint range
    @param bpt: if not nullptr, is filled with the characteristics.
    @returns false if no breakpoint exists
    """

def get_bpt_group(bptloc: bpt_location_t) -> str: ...
    """Retrieve the absolute path to the folder of the bpt based on the bpt_location find_bpt is called to retrieve the bpt \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bptloc: bptlocation of the bpt
    @returns success
    @retval true: breakpoint correclty moved to the directory
    """

def get_bpt_qty() -> int: ...
    """Get number of breakpoints. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_bpt_tev_ea(n: int) -> ida_idaapi.ea_t: ...
    """Get the address associated to a read, read/write or execution trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @returns BADADDR if not a read, read/write or execution trace event.
    """

def get_bptloc_string(i: int) -> str: ...

def get_call_tev_callee(n: int) -> ida_idaapi.ea_t: ...
    """Get the called function from a function call trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @returns BADADDR if not a function call event.
    """

def get_current_source_file() -> str: ...

def get_current_source_line() -> int: ...

def get_current_thread() -> thid_t: ...
    """Get current thread ID. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_dbg_byte(ea: int) -> uint32 *: ...
    """Get one byte of the debugged process memory. 
            
    @param ea: linear address
    @returns success
    @retval true: success
    @retval false: address inaccessible or debugger not running
    """

def get_dbg_memory_info(ranges: meminfo_vec_t) -> int: ...

def get_dbg_reg_info(regname: str, ri: register_info_t) -> bool: ...
    """Get register information \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_debug_event() -> debug_event_t const *: ...
    """Get the current debugger event.
    
    """

def get_debugger_event_cond() -> str: ...

def get_first_module(modinfo: modinfo_t) -> bool: ...

def get_func_trace_options() -> int: ...
    """Get current function tracing options. Also see FT_LOG_RET \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_global_var(prov: srcinfo_provider_t *, ea: int, name: str, out: source_item_ptr *) -> bool: ...

def get_grp_bpts(bpts: bpt_vec_t, grp_name: str) -> ssize_t: ...
    """Retrieve a copy the bpts stored in a folder \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bpts: : pointer to a vector where the copy of bpts are stored
    @param grp_name: absolute path to the folder
    @returns number of bpts present in the vector
    """

def get_insn_tev_reg_mem(n: int, memmap: memreg_infos_t) -> bool: ...
    """Read the memory pointed by register values from an instruction trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param memmap: result
    @returns false if not an instruction event or no memory is available
    """

def get_insn_tev_reg_result(n: int, regname: str, regval: regval_t) -> bool: ...
    """Read the resulting register value from an instruction trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param regname: name of desired register
    @param regval: result
    @returns false if not an instruction trace event or register wasn't modified.
    """

def get_insn_tev_reg_val(n: int, regname: str, regval: regval_t) -> bool: ...
    """Read a register value from an instruction trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param regname: name of desired register
    @param regval: result
    @returns false if not an instruction event.
    """

def get_insn_trace_options() -> int: ...
    """Get current instruction tracing options. Also see IT_LOG_SAME_IP \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_ip_val() -> uint64 *: ...
    """Get value of the IP (program counter) register for the current thread. Requires a suspended debugger. 
            
    """

def get_local_var(prov: srcinfo_provider_t *, ea: int, name: str, out: source_item_ptr *) -> bool: ...

def get_local_vars(prov: srcinfo_provider_t *, ea: int, out: source_items_t *) -> bool: ...

def get_manual_regions(args: Any) -> Any: ...
    """Returns the manual memory regions
    
    This function has the following signatures:
    
        1. get_manual_regions() -> List[Tuple(ida_idaapi.ea_t, ida_idaapi.ea_t, str, str, ida_idaapi.ea_t, int, int)]
           Where each tuple holds (start_ea, end_ea, name, sclass, sbase, bitness, perm)
        2. get_manual_regions(storage: meminfo_vec_t) -> None
    """

def get_module_info(ea: int, modinfo: modinfo_t) -> bool: ...

def get_next_module(modinfo: modinfo_t) -> bool: ...

def get_process_options() -> qstring *, qstring *, qstring *, qstring *, qstring *, int *: ...
    """Get process options. Any of the arguments may be nullptr 
            
    """

def get_process_options2() -> qstring *, qstring *, launch_env_t *, qstring *, qstring *, qstring *, int *: ...

def get_process_state() -> int: ...
    """Return the state of the currently debugged process. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns one of Debugged process states
    """

def get_processes(proclist: procinfo_vec_t) -> ssize_t: ...
    """Take a snapshot of running processes and return their description. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param proclist: array with information about each running process
    @returns number of processes or -1 on error
    """

def get_reg_val(args: Any) -> Any: ...
    """Get a register value.
    
    This function has the following signatures:
    
        1. get_reg_val(name: str) -> Union[int, float, bytes]
        2. get_reg_val(name: str, regval: regval_t) -> bool
    
    The first (and most user-friendly) form will return
    a value whose type is related to the register type.
    I.e., either an integer, a float or, in the case of large
    vector registers, a bytes sequence.
    
    @param name the register name
    @return the register value (1st form)
    """

def get_reg_vals(tid: int, clsmask: int = -1) -> ida_idd.regvals_t: ...
    """Fetch live registers values for the thread
    
    @param tid The ID of the thread to read registers for
    @param clsmask An OR'ed mask of register classes to
           read values for (can be used to speed up the
           retrieval process)
    
    @return: a list of register values (empty if an error occurs)
    """

def get_ret_tev_return(n: int) -> ida_idaapi.ea_t: ...
    """Get the return address from a function return trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @returns BADADDR if not a function return event.
    """

def get_running_notification() -> dbg_notification_t: ...
    """Get the notification associated (if any) with the current running request. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns dbg_null if no running request
    """

def get_running_request() -> ui_notification_t: ...
    """Get the current running request. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns ui_null if no running request
    """

def get_sp_val() -> uint64 *: ...
    """Get value of the SP register for the current thread. Requires a suspended debugger. 
            
    """

def get_srcinfo_provider(name: str) -> srcinfo_provider_t *: ...

def get_step_trace_options() -> int: ...
    """Get current step tracing options. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns Step trace options
    """

def get_tev_ea(n: int) -> ida_idaapi.ea_t: ...

def get_tev_event(n: int, d: debug_event_t) -> bool: ...
    """Get the corresponding debug event, if any, for the specified tev object. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param d: result
    @returns false if the tev_t object doesn't have any associated debug event, true otherwise, with the debug event in "d".
    """

def get_tev_info(n: int, tev_info: tev_info_t) -> bool: ...
    """Get main information about a trace event. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param tev_info: result
    @returns success
    """

def get_tev_memory_info(n: int, mi: meminfo_vec_t) -> bool: ...
    """Get the memory layout, if any, for the specified tev object. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of trace event, is in range 0..get_tev_qty()-1. 0 represents the latest added trace event.
    @param mi: result
    @returns false if the tev_t object is not of type tev_mem, true otherwise, with the new memory layout in "mi".
    """

def get_tev_qty() -> int: ...
    """Get number of trace events available in trace buffer. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_tev_reg_mem(tev: Any, idx: Any) -> Any: ...

def get_tev_reg_mem_ea(tev: Any, idx: Any) -> Any: ...

def get_tev_reg_mem_qty(tev: Any) -> Any: ...

def get_tev_reg_val(tev: Any, reg: Any) -> Any: ...

def get_tev_tid(n: int) -> int: ...

def get_tev_type(n: int) -> int: ...

def get_thread_qty() -> int: ...
    """Get number of threads. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def get_trace_base_address() -> ida_idaapi.ea_t: ...
    """Get the base address of the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns the base address of the currently loaded trace
    """

def get_trace_dynamic_register_set(idaregs: dynamic_register_set_t *) -> None: ...
    """Get dynamic register set of current trace.
    
    """

def get_trace_file_desc(filename: str) -> str: ...
    """Get the file header of the specified trace file.
    
    """

def get_trace_platform() -> str: ...
    """Get platform name of current trace.
    
    """

def getn_bpt(n: int, bpt: bpt_t) -> bool: ...
    """Get the characteristics of a breakpoint. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of breakpoint, is in range 0..get_bpt_qty()-1
    @param bpt: filled with the characteristics.
    @returns false if no breakpoint exists
    """

def getn_thread(n: int) -> thid_t: ...
    """Get the ID of a thread. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of thread, is in range 0..get_thread_qty()-1
    @returns NO_THREAD if the thread doesn't exist.
    """

def getn_thread_name(n: int) -> str: ...
    """Get the NAME of a thread \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param n: number of thread, is in range 0..get_thread_qty()-1 or -1 for the current thread
    @returns thread name or nullptr if the thread doesn't exist.
    """

def graph_trace() -> bool: ...
    """Show the trace callgraph.
    
    """

def handle_debug_event(ev: debug_event_t, rqflags: int) -> int: ...

def hide_all_bpts() -> int: ...

def internal_get_sreg_base(tid: int, sreg_value: int) -> Any: ...
    """Get the sreg base, for the given thread.
    
    @param tid: the thread ID
    @param sreg_value: the sreg value
    @return: The sreg base, or BADADDR on failure.
    """

def internal_ioctl(fn: int, buf: void const *, poutbuf: void **, poutsize: ssize_t *) -> int: ...

def invalidate_dbg_state(dbginv: int) -> int: ...
    """Invalidate cached debugger information. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param dbginv: Debugged process invalidation options
    @returns current debugger state (one of Debugged process states)
    """

def invalidate_dbgmem_config() -> None: ...
    """Invalidate the debugged process memory configuration. Call this function if the debugged process might have changed its memory layout (allocated more memory, for example) 
            
    """

def invalidate_dbgmem_contents(ea: int, size: asize_t) -> None: ...
    """Invalidate the debugged process memory contents. Call this function each time the process has been stopped or the process memory is modified. If ea == BADADDR, then the whole memory contents will be invalidated 
            
    """

def is_bblk_trace_enabled() -> bool: ...

def is_debugger_busy() -> bool: ...
    """Is the debugger busy?. Some debuggers do not accept any commands while the debugged application is running. For such a debugger, it is unsafe to do anything with the database (even simple queries like get_byte may lead to undesired consequences). Returns: true if the debugged application is running under such a debugger 
            
    """

def is_debugger_memory(ea: int) -> bool: ...
    """Is the address mapped to debugger memory?
    
    """

def is_debugger_on() -> bool: ...
    """Is the debugger currently running?
    
    """

def is_func_trace_enabled() -> bool: ...
    """Get current state of functions tracing. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_insn_trace_enabled() -> bool: ...
    """Get current state of instruction tracing. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_reg_custom(regname: str) -> bool: ...
    """Does a register contain a value of a custom data type? \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_reg_float(regname: str) -> bool: ...
    """Does a register contain a floating point value? \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_reg_integer(regname: str) -> bool: ...
    """Does a register contain an integer value? \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_request_running() -> bool: ...
    """Is a request currently running?
    
    """

def is_step_trace_enabled() -> bool: ...
    """Get current state of step tracing. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def is_valid_dstate(state: int) -> bool: ...

def is_valid_trace_file(filename: str) -> bool: ...
    """Is the specified file a valid trace file for the current database?
    
    """

def list_bptgrps() -> List[str]: ...
    """Retrieve the list of absolute path of all folders of bpt dirtree.
    Synchronous function, Notification, none (synchronous function)
    """

def load_debugger(dbgname: str, use_remote: bool) -> bool: ...

def load_trace_file(filename: str) -> str: ...
    """Load a recorded trace file in the 'Tracing' window. If the call succeeds and 'buf' is not null, the description of the trace stored in the binary trace file will be returned in 'buf' 
            
    """

def move_bpt_to_grp(bpt: bpt_t, grp_name: str) -> bool: ...
    """Move a bpt into a folder in the breakpoint dirtree if the folder didn't exists, it will be created \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bpt: bpt that will be moved
    @param grp_name: absolute path to the breakpoint dirtree folder
    @returns success
    """

def put_dbg_byte(ea: int, x: int) -> bool: ...
    """Change one byte of the debugged process memory. 
            
    @param ea: linear address
    @param x: byte value
    @returns true if the process memory has been modified
    """

def read_dbg_memory(ea: int, buffer: void *, size: size_t) -> ssize_t: ...

def refresh_debugger_memory() -> Any: ...
    """Refreshes the debugger memory
    
    @return: Nothing
    """

def rename_bptgrp(old_name: str, new_name: str) -> bool: ...
    """Rename a folder of bpt dirtree \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param old_name: absolute path to the folder to be renamed
    @param new_name: absolute path of the new folder name
    @returns success
    """

def request_add_bpt(args: Any) -> bool: ...
    """This function has the following signatures:
    
        0. request_add_bpt(ea: ida_idaapi.ea_t, size: asize_t=0, type: bpttype_t=BPT_DEFAULT) -> bool
        1. request_add_bpt(bpt: const bpt_t &) -> bool
    
    # 0: request_add_bpt(ea: ida_idaapi.ea_t, size: asize_t=0, type: bpttype_t=BPT_DEFAULT) -> bool
    
    Post an add_bpt(ea_t, asize_t, bpttype_t) request.
    
    
    # 1: request_add_bpt(bpt: const bpt_t &) -> bool
    
    Post an add_bpt(const bpt_t &) request.
    
    
    """

def request_attach_process(pid: pid_t, event_id: int) -> int: ...
    """Post an attach_process() request.
    
    """

def request_clear_trace() -> None: ...
    """Post a clear_trace() request.
    
    """

def request_continue_backwards() -> bool: ...
    """Post a continue_backwards() request. 
            
    """

def request_continue_process() -> bool: ...
    """Post a continue_process() request. 
            
    """

def request_del_bpt(args: Any) -> bool: ...
    """This function has the following signatures:
    
        0. request_del_bpt(ea: ida_idaapi.ea_t) -> bool
        1. request_del_bpt(bptloc: const bpt_location_t &) -> bool
    
    # 0: request_del_bpt(ea: ida_idaapi.ea_t) -> bool
    
    Post a del_bpt(ea_t) request.
    
    
    # 1: request_del_bpt(bptloc: const bpt_location_t &) -> bool
    
    Post a del_bpt(const bpt_location_t &) request.
    
    
    """

def request_detach_process() -> bool: ...
    """Post a detach_process() request.
    
    """

def request_disable_bblk_trace() -> bool: ...

def request_disable_bpt(args: Any) -> bool: ...

def request_disable_func_trace() -> bool: ...

def request_disable_insn_trace() -> bool: ...

def request_disable_step_trace() -> bool: ...

def request_enable_bblk_trace(enable: bool = True) -> bool: ...

def request_enable_bpt(args: Any) -> bool: ...

def request_enable_func_trace(enable: bool = True) -> bool: ...

def request_enable_insn_trace(enable: bool = True) -> bool: ...

def request_enable_step_trace(enable: int = 1) -> bool: ...

def request_exit_process() -> bool: ...
    """Post an exit_process() request.
    
    """

def request_resume_thread(tid: thid_t) -> int: ...
    """Post a resume_thread() request.
    
    """

def request_run_to(args: Any) -> bool: ...
    """Post a run_to() request.
    
    """

def request_run_to_backwards(args: Any) -> bool: ...
    """Post a run_to_backwards() request.
    
    """

def request_select_thread(tid: thid_t) -> bool: ...
    """Post a select_thread() request.
    
    """

def request_set_bblk_trace_options(options: int) -> None: ...
    """Post a set_bblk_trace_options() request.
    
    """

def request_set_func_trace_options(options: int) -> None: ...
    """Post a set_func_trace_options() request.
    
    """

def request_set_insn_trace_options(options: int) -> None: ...
    """Post a set_insn_trace_options() request.
    
    """

def request_set_reg_val(regname: str, o: PyObject *) -> PyObject *: ...
    """Post a set_reg_val() request.
    
    """

def request_set_resume_mode(tid: thid_t, mode: resume_mode_t) -> bool: ...
    """Post a set_resume_mode() request.
    
    """

def request_set_step_trace_options(options: int) -> None: ...
    """Post a set_step_trace_options() request.
    
    """

def request_start_process(path: str = None, args: str = None, sdir: str = None) -> int: ...
    """Post a start_process() request.
    
    """

def request_step_into() -> bool: ...
    """Post a step_into() request.
    
    """

def request_step_into_backwards() -> bool: ...
    """Post a step_into_backwards() request.
    
    """

def request_step_over() -> bool: ...
    """Post a step_over() request.
    
    """

def request_step_over_backwards() -> bool: ...
    """Post a step_over_backwards() request.
    
    """

def request_step_until_ret() -> bool: ...
    """Post a step_until_ret() request.
    
    """

def request_suspend_process() -> bool: ...
    """Post a suspend_process() request.
    
    """

def request_suspend_thread(tid: thid_t) -> int: ...
    """Post a suspend_thread() request.
    
    """

def resume_thread(tid: thid_t) -> int: ...
    """Resume thread. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    @param tid: thread id
    @retval -1: network error
    @retval 0: failed
    @retval 1: ok
    """

def retrieve_exceptions() -> excvec_t *: ...
    """Retrieve the exception information. You may freely modify the returned vector and add/edit/delete exceptions You must call store_exceptions() after any modifications Note: exceptions with code zero, multiple exception codes or names are prohibited 
            
    """

def run_requests() -> bool: ...
    """Execute requests until all requests are processed or an asynchronous function is called. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @returns false if not all requests could be processed (indicates an asynchronous function was started)
    """

def run_to(args: Any) -> bool: ...
    """Execute the process until the given address is reached. If no process is active, a new process is started. Technically, the debugger sets up a temporary breakpoint at the given address, and continues (or starts) the execution of the whole process. So, all threads continue their execution! \sq{Type, Asynchronous function - available as Request, Notification, dbg_run_to} 
            
    @param ea: target address
    @param pid: not used yet. please do not specify this parameter.
    @param tid: not used yet. please do not specify this parameter.
    """

def run_to_backwards(args: Any) -> bool: ...
    """Execute the process backwards until the given address is reached. Technically, the debugger sets up a temporary breakpoint at the given address, and continues (or starts) the execution of the whole process. \sq{Type, Asynchronous function - available as Request, Notification, dbg_run_to} 
            
    @param ea: target address
    @param pid: not used yet. please do not specify this parameter.
    @param tid: not used yet. please do not specify this parameter.
    """

def save_trace_file(filename: str, description: str) -> bool: ...
    """Save the current trace in the specified file.
    
    """

def select_thread(tid: thid_t) -> bool: ...
    """Select the given thread as the current debugged thread. All thread related execution functions will work on this thread. The process must be suspended to select a new thread. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    @param tid: ID of the thread to select
    @returns false if the thread doesn't exist.
    """

def send_dbg_command(command: Any) -> Any: ...
    """
        Send a direct command to the debugger backend, and
        retrieve the result as a string.
    
        Note: any double-quotes in 'command' must be backslash-escaped.
        Note: this only works with some debugger backends: Bochs, WinDbg, GDB.
    
        Returns: (True, <result string>) on success, or (False, <Error message string>) on failure
        
    """

def set_bblk_trace_options(options: int) -> None: ...
    """Modify basic block tracing options (see BT_LOG_INSTS)
    
    """

def set_bpt_group(bpt: bpt_t, grp_name: str) -> bool: ...
    """Move a bpt into a folder in the breakpoint dirtree if the folder didn't exists, it will be created \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bpt: bpt that will be moved
    @param grp_name: absolute path to the breakpoint dirtree folder
    @returns success
    """

def set_bptloc_group(bptloc: bpt_location_t, grp_name: str) -> bool: ...
    """Move a bpt into a folder in the breakpoint dirtree based on the bpt_location find_bpt is called to retrieve the bpt and then set_bpt_group if the folder didn't exists, it will be created \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param bptloc: bptlocation of the bpt that will be moved
    @param grp_name: absolute path to the breakpoint dirtree folder
    @returns success
    """

def set_bptloc_string(s: str) -> int: ...

def set_debugger_event_cond(NONNULL_evcond: str) -> None: ...

def set_debugger_options(options: uint) -> uint: ...
    """Set debugger options. Replaces debugger options with the specification combination Debugger options 
            
    @returns the old debugger options
    """

def set_func_trace_options(options: int) -> None: ...
    """Modify function tracing options. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    """

def set_highlight_trace_options(hilight: bool, color: bgcolor_t, diff: bgcolor_t) -> None: ...
    """Set highlight trace parameters.
    
    """

def set_insn_trace_options(options: int) -> None: ...
    """Modify instruction tracing options. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    """

def set_manual_regions(ranges: meminfo_vec_t) -> None: ...

def set_process_options(args: Any) -> None: ...
    """Set process options. Any of the arguments may be nullptr, which means 'do not modify' 
            
    """

def set_process_state(newstate: int, p_thid: thid_t *, dbginv: int) -> int: ...
    """Set new state for the debugged process. Notifies the IDA kernel about the change of the debugged process state. For example, a debugger module could call this function when it knows that the process is suspended for a short period of time. Some IDA API calls can be made only when the process is suspended. The process state is usually restored before returning control to the caller. You must know that it is ok to change the process state, doing it at arbitrary moments may crash the application or IDA. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param newstate: new process state (one of Debugged process states) if DSTATE_NOTASK is passed then the state is not changed
    @param p_thid: ptr to new thread id. may be nullptr or pointer to NO_THREAD. the pointed variable will contain the old thread id upon return
    @param dbginv: Debugged process invalidation options
    @returns old debugger state (one of Debugged process states)
    """

def set_reg_val(args: Any) -> bool: ...
    """Set a register value by name
    
    This function has the following signatures:
        1. set_reg_val(name: str, value: Union[int, float, bytes]) -> bool
        1. set_reg_val(tid: int, regidx: int, value: Union[int, float, bytes]) -> bool
    
    Depending on the register type, this will expect
    either an integer, a float or, in the case of large
    vector registers, a bytes sequence.
    
    @param name (1st form) the register name
    @param tid (2nd form) the thread ID
    @param regidx (2nd form) the register index
    @param value the register value
    @return success
    """

def set_remote_debugger(host: str, _pass: str, port: int = -1) -> None: ...
    """Set remote debugging options. Should be used before starting the debugger. 
            
    @param host: If empty, IDA will use local debugger. If nullptr, the host will not be set.
    @param port: If -1, the default port number will be used
    """

def set_resume_mode(tid: thid_t, mode: resume_mode_t) -> bool: ...
    """How to resume the application. Set resume mode but do not resume process. 
            
    """

def set_step_trace_options(options: int) -> None: ...
    """Modify step tracing options. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    """

def set_trace_base_address(ea: int) -> None: ...
    """Set the base address of the current trace. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def set_trace_dynamic_register_set(idaregs: dynamic_register_set_t &) -> None: ...
    """Set dynamic register set of current trace.
    
    """

def set_trace_file_desc(filename: str, description: str) -> bool: ...
    """Change the description of the specified trace file.
    
    """

def set_trace_platform(platform: str) -> None: ...
    """Set platform name of current trace.
    
    """

def set_trace_size(size: int) -> bool: ...
    """Specify the new size of the circular buffer. \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    @param size: if 0, buffer isn't circular and events are never removed. If the new size is smaller than the existing number of trace events, a corresponding number of trace events are removed.
    """

def srcdbg_request_step_into() -> bool: ...

def srcdbg_request_step_over() -> bool: ...

def srcdbg_request_step_until_ret() -> bool: ...

def srcdbg_step_into() -> bool: ...

def srcdbg_step_over() -> bool: ...

def srcdbg_step_until_ret() -> bool: ...

def start_process(path: str = None, args: str = None, sdir: str = None) -> int: ...
    """Start a process in the debugger. \sq{Type, Asynchronous function - available as Request, Notification, dbg_process_start} 
            
    @param path: path to the executable to start
    @param args: arguments to pass to process
    @param sdir: starting directory for the process
    @retval -1: impossible to create the process
    @retval 0: the starting of the process was cancelled by the user
    @retval 1: the process was properly started
    """

def step_into() -> bool: ...
    """Execute one instruction in the current thread. Other threads are kept suspended. \sq{Type, Asynchronous function - available as Request, Notification, dbg_step_into} 
            
    """

def step_into_backwards() -> bool: ...
    """Execute one instruction backwards in the current thread. Other threads are kept suspended. \sq{Type, Asynchronous function - available as Request, Notification, dbg_step_into} 
            
    """

def step_over() -> bool: ...
    """Execute one instruction in the current thread, but without entering into functions. Others threads keep suspended. \sq{Type, Asynchronous function - available as Request, Notification, dbg_step_over} 
            
    """

def step_over_backwards() -> bool: ...
    """Execute one instruction backwards in the current thread, but without entering into functions. Other threads are kept suspended. \sq{Type, Asynchronous function - available as Request, Notification, dbg_step_over} 
            
    """

def step_until_ret() -> bool: ...
    """Execute instructions in the current thread until a function return instruction is executed (aka "step out"). Other threads are kept suspended. \sq{Type, Asynchronous function - available as Request, Notification, dbg_step_until_ret} 
            
    """

def store_exceptions() -> bool: ...
    """Update the exception information stored in the debugger module by invoking its dbg->set_exception_info callback 
            
    """

def suspend_process() -> bool: ...
    """Suspend the process in the debugger. \sq{ Type,
    * Synchronous function (if in a notification handler)
    * Asynchronous function (everywhere else)
    * available as Request, Notification,
    * none (if in a notification handler)
    * dbg_suspend_process (everywhere else) }
    
    
    
    """

def suspend_thread(tid: thid_t) -> int: ...
    """Suspend thread. Suspending a thread may deadlock the whole application if the suspended was owning some synchronization objects. \sq{Type, Synchronous function - available as request, Notification, none (synchronous function)} 
            
    @param tid: thread id
    @retval -1: network error
    @retval 0: failed
    @retval 1: ok
    """

def update_bpt(bpt: bpt_t) -> bool: ...
    """Update modifiable characteristics of an existing breakpoint. To update the breakpoint location, use change_bptlocs() \sq{Type, Synchronous function, Notification, none (synchronous function)} 
            
    """

def wait_for_next_event(wfne: int, timeout: int) -> dbg_event_code_t: ...
    """Wait for the next event.
    This function (optionally) resumes the process execution, and waits for a debugger event until a possible timeout occurs.
    
    @param wfne: combination of Wait for debugger event flags constants
    @param timeout: number of seconds to wait, -1-infinity
    @returns either an event_id_t (if > 0), or a dbg_event_code_t (if <= 0)
    """

def write_dbg_memory(args: Any) -> ssize_t: ...

BKPT_ACTIVE: int  # 8
BKPT_BADBPT: int  # 1
BKPT_CNDREADY: int  # 32
BKPT_FAKEPEND: int  # 64
BKPT_LISTBPT: int  # 2
BKPT_PAGE: int  # 128
BKPT_PARTIAL: int  # 16
BKPT_TRACE: int  # 4
BPLT_ABS: int  # 0
BPLT_REL: int  # 1
BPLT_SRC: int  # 3
BPLT_SYM: int  # 2
BPTCK_ACT: int  # 2
BPTCK_NO: int  # 0
BPTCK_NONE: int  # -1
BPTCK_YES: int  # 1
BPTEV_ADDED: int  # 0
BPTEV_CHANGED: int  # 2
BPTEV_REMOVED: int  # 1
BPT_BRK: int  # 1
BPT_ELANG_MASK: int  # 4026531840
BPT_ELANG_SHIFT: int  # 28
BPT_ENABLED: int  # 8
BPT_LOWCND: int  # 16
BPT_TRACE: int  # 2
BPT_TRACEON: int  # 32
BPT_TRACE_BBLK: int  # 256
BPT_TRACE_FUNC: int  # 128
BPT_TRACE_INSN: int  # 64
BPT_TRACE_TYPES: int  # 448
BPT_UPDMEM: int  # 4
BT_LOG_INSTS: int  # 1
DBGINV_ALL: int  # 32767
DBGINV_MEMCFG: int  # 2
DBGINV_MEMORY: int  # 1
DBGINV_NONE: int  # 0
DBGINV_REDRAW: int  # 32768
DBGINV_REGS: int  # 4
DEC_ERROR: int  # -1
DEC_NOTASK: int  # -2
DEC_TIMEOUT: int  # 0
DOPT_BPT_MSGS: int  # 16
DOPT_DISABLE_ASLR: int  # 524288
DOPT_END_BPT: int  # 65536
DOPT_ENTRY_BPT: int  # 4096
DOPT_EXCDLG: int  # 24576
DOPT_FAST_STEP: int  # 262144
DOPT_INFO_BPT: int  # 512
DOPT_INFO_MSGS: int  # 256
DOPT_LIB_BPT: int  # 128
DOPT_LIB_MSGS: int  # 64
DOPT_LOAD_DINFO: int  # 32768
DOPT_REAL_MEMORY: int  # 1024
DOPT_REDO_STACK: int  # 2048
DOPT_SEGM_MSGS: int  # 1
DOPT_START_BPT: int  # 2
DOPT_TEMP_HWBPT: int  # 131072
DOPT_THREAD_BPT: int  # 8
DOPT_THREAD_MSGS: int  # 4
DSTATE_NOTASK: int  # 0
DSTATE_RUN: int  # 1
DSTATE_SUSP: int  # -1
EXCDLG_ALWAYS: int  # 24576
EXCDLG_NEVER: int  # 0
EXCDLG_UNKNOWN: int  # 8192
FT_LOG_RET: int  # 1
IT_LOG_SAME_IP: int  # 1
MOVBPT_BAD_TYPE: int  # 3
MOVBPT_DEST_BUSY: int  # 2
MOVBPT_NOT_FOUND: int  # 1
MOVBPT_OK: int  # 0
SAVE_ALL_VALUES: int  # 0
SAVE_DIFF: int  # 1
SAVE_NONE: int  # 2
SRCDBG_PROV_VERSION: int  # 4
SRCIT_EXPR: int  # 4
SRCIT_FUNC: int  # 2
SRCIT_LOCVAR: int  # 6
SRCIT_MODULE: int  # 1
SRCIT_NONE: int  # 0
SRCIT_STMT: int  # 3
SRCIT_STTVAR: int  # 5
ST_ALREADY_LOGGED: int  # 4
ST_DIFFERENTIAL: int  # 16
ST_OPTIONS_DEFAULT: int  # 3
ST_OPTIONS_MASK: int  # 31
ST_OVER_DEBUG_SEG: int  # 1
ST_OVER_LIB_FUNC: int  # 2
ST_SKIP_LOOPS: int  # 8
SWIG_PYTHON_LEGACY_BOOL: int  # 1
WFNE_ANY: int  # 1
WFNE_CONT: int  # 8
WFNE_NOWAIT: int  # 16
WFNE_SILENT: int  # 4
WFNE_SUSP: int  # 2
WFNE_USEC: int  # 32
dbg_bpt: int  # 12
dbg_bpt_changed: int  # 19
dbg_exception: int  # 10
dbg_finished_loading_bpts: int  # 21
dbg_information: int  # 9
dbg_last: int  # 22
dbg_library_load: int  # 7
dbg_library_unload: int  # 8
dbg_null: int  # 0
dbg_process_attach: int  # 3
dbg_process_detach: int  # 4
dbg_process_exit: int  # 2
dbg_process_start: int  # 1
dbg_request_error: int  # 14
dbg_run_to: int  # 17
dbg_started_loading_bpts: int  # 20
dbg_step_into: int  # 15
dbg_step_over: int  # 16
dbg_step_until_ret: int  # 18
dbg_suspend_process: int  # 11
dbg_thread_exit: int  # 6
dbg_thread_start: int  # 5
dbg_trace: int  # 13
ida_expr: module
ida_idaapi: module
ida_idd: module
tev_bpt: int  # 4
tev_call: int  # 2
tev_event: int  # 6
tev_insn: int  # 1
tev_max: int  # 7
tev_mem: int  # 5
tev_none: int  # 0
tev_ret: int  # 3
weakref: module