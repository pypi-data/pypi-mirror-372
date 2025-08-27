from typing import Any, Optional, List, Dict, Tuple, Callable, Union

"""Definitions of IDP, LDR, PLUGIN module interfaces.

This file also contains:
* functions to load files into the database
* functions to generate output files
* high level functions to work with the database (open, save, close)


The LDR interface consists of one structure: loader_t 
The IDP interface consists of one structure: processor_t 
The PLUGIN interface consists of one structure: plugin_t
Modules can't use standard FILE* functions. They must use functions from <fpro.h>
Modules can't use standard memory allocation functions. They must use functions from <pro.h>
The exported entry #1 in the module should point to the the appropriate structure. (loader_t for LDR module, for example) 
    
"""

class idp_desc_t:
    @property
    def checked(self) -> Any: ...
    @property
    def family(self) -> Any: ...
    @property
    def is_script(self) -> Any: ...
    @property
    def mtime(self) -> Any: ...
    @property
    def names(self) -> Any: ...
    @property
    def path(self) -> Any: ...
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

class idp_name_t:
    @property
    def hidden(self) -> Any: ...
    @property
    def lname(self) -> Any: ...
    @property
    def sname(self) -> Any: ...
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

class loader_t:
    @property
    def flags(self) -> Any: ...
    @property
    def version(self) -> Any: ...
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

class plugin_info_t:
    @property
    def arg(self) -> Any: ...
    @property
    def comment(self) -> Any: ...
    @property
    def dllmem(self) -> Any: ...
    @property
    def entry(self) -> Any: ...
    @property
    def flags(self) -> Any: ...
    @property
    def hotkey(self) -> Any: ...
    @property
    def idaplg_name(self) -> Any: ...
    @property
    def name(self) -> Any: ...
    @property
    def next(self) -> Any: ...
    @property
    def org_hotkey(self) -> Any: ...
    @property
    def org_name(self) -> Any: ...
    @property
    def path(self) -> Any: ...
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

class qvector_snapshotvec_t:
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: qvector_snapshotvec_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, value: Any) -> bool: ...
        """Return self>=value."""
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __getitem__(self, i: size_t) -> snapshot_t *: ...
    def __gt__(self, value: Any) -> bool: ...
        """Return self>value."""
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
    def __ne__(self, r: qvector_snapshotvec_t) -> bool: ...
    def __new__(self, args: Any, kwargs: Any) -> Any: ...
        """Create and return a new object.  See help(type) for accurate signature."""
    def __reduce__(self) -> Any: ...
        """Helper for pickle."""
    def __reduce_ex__(self, protocol: Any) -> Any: ...
        """Helper for pickle."""
    def __repr__(self) -> Any: ...
    def __setattr__(self, name: Any, value: Any) -> Any: ...
        """Implement setattr(self, name, value)."""
    def __setitem__(self, i: size_t, v: snapshot_t) -> None: ...
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
    def add_unique(self, x: snapshot_t) -> bool: ...
    def append(self, x: snapshot_t) -> None: ...
    def at(self, _idx: size_t) -> snapshot_t *: ...
    def back(self) -> Any: ...
    def begin(self, args: Any) -> qvector< snapshot_t * >: ...
    def capacity(self) -> int: ...
    def clear(self) -> None: ...
    def empty(self) -> bool: ...
    def end(self, args: Any) -> qvector< snapshot_t * >: ...
    def erase(self, args: Any) -> qvector< snapshot_t * >: ...
    def extend(self, x: qvector_snapshotvec_t) -> None: ...
    def extract(self) -> snapshot_t **: ...
    def find(self, args: Any) -> qvector< snapshot_t * >: ...
    def front(self) -> Any: ...
    def has(self, x: snapshot_t) -> bool: ...
    def inject(self, s: snapshot_t **, len: size_t) -> None: ...
    def insert(self, it: qvector< snapshot_t * >::iterator, x: snapshot_t) -> qvector< snapshot_t * >: ...
    def pop_back(self) -> None: ...
    def push_back(self, args: Any) -> snapshot_t *&: ...
    def qclear(self) -> None: ...
    def reserve(self, cnt: size_t) -> None: ...
    def resize(self, args: Any) -> None: ...
    def size(self) -> int: ...
    def swap(self, r: qvector_snapshotvec_t) -> None: ...
    def truncate(self) -> None: ...

class snapshot_t:
    @property
    def children(self) -> Any: ...
    @property
    def desc(self) -> Any: ...
    @property
    def filename(self) -> Any: ...
    @property
    def flags(self) -> Any: ...
    @property
    def id(self) -> Any: ...
    def __delattr__(self, name: Any) -> Any: ...
        """Implement delattr(self, name)."""
    def __dir__(self) -> Any: ...
        """Default dir() implementation."""
    def __eq__(self, r: snapshot_t) -> bool: ...
    def __format__(self, format_spec: Any) -> Any: ...
        """Default object formatter."""
    def __ge__(self, r: snapshot_t) -> bool: ...
    def __getattribute__(self, name: Any) -> Any: ...
        """Return getattr(self, name)."""
    def __gt__(self, r: snapshot_t) -> bool: ...
    def __init__(self) -> Any: ...
    def __init_subclass__(self, *args: Any, **kwargs: Any) -> Any: ...
        """This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
    def __le__(self, r: snapshot_t) -> bool: ...
    def __lt__(self, r: snapshot_t) -> bool: ...
    def __ne__(self, r: snapshot_t) -> bool: ...
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
    def clear(self) -> None: ...

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

def base2file(fp: FILE *, pos: qoff64_t, ea1: int, ea2: int) -> int: ...
    """Unload database to a binary file. This function works for wide byte processors too. 
            
    @param fp: pointer to file
    @param pos: position in the file
    @param ea1: range of source linear addresses
    @param ea2: range of source linear addresses
    @returns 1-ok(always), write error leads to immediate exit
    """

def build_snapshot_tree(root: snapshot_t) -> bool: ...
    """Build the snapshot tree. 
            
    @param root: snapshot root that will contain the snapshot tree elements.
    @returns success
    """

def clr_database_flag(dbfl: int) -> None: ...

def extract_module_from_archive(fname: str, is_remote: bool = False) -> PyObject *: ...
    """Extract a module for an archive file. Parse an archive file, show the list of modules to the user, allow him to select a module, extract the selected module to a file (if the extract module is an archive, repeat the process). This function can handle ZIP, AR, AIXAR, OMFLIB files. The temporary file will be automatically deleted by IDA at the end. 
            
    @param is_remote: is the input file remote?
    @retval true: ok
    @retval false: something bad happened (error message has been displayed to the user)
    """

def file2base(li: linput_t *, pos: qoff64_t, ea1: int, ea2: int, patchable: int) -> int: ...
    """Load portion of file into the database. This function will include (ea1..ea2) into the addressing space of the program (make it enabled). 
            
    @param li: pointer of input source
    @param pos: position in the file
    @param ea1: range of destination linear addresses
    @param ea2: range of destination linear addresses
    @param patchable: should the kernel remember correspondence of file offsets to linear addresses.
    @retval 1: ok
    @retval 0: read error, a warning is displayed
    """

def find_plugin(name: str, load_if_needed: bool = False) -> plugin_t *: ...
    """Find a user-defined plugin and optionally load it. 
            
    @param name: short plugin name without path and extension, or absolute path to the file name
    @param load_if_needed: if the plugin is not present in the memory, try to load it
    @returns pointer to plugin description block
    """

def flush_buffers() -> int: ...
    """Flush buffers to the disk.
    
    """

def gen_exe_file(fp: FILE *) -> int: ...
    """Generate an exe file (unload the database in binary form). 
            
    @returns fp the output file handle. if fp == nullptr then return:
    * 1: can generate an executable file
    * 0: can't generate an executable file
    @retval 1: ok
    @retval 0: failed
    """

def gen_file(otype: ofile_type_t, fp: FILE *, ea1: int, ea2: int, flags: int) -> int: ...
    """Generate an output file. OFILE_EXE: 
            
    @param otype: type of output file.
    @param fp: the output file handle
    @param ea1: start address. For some file types this argument is ignored
    @param ea2: end address. For some file types this argument is ignored as usual in ida, the end address of the range is not included
    @param flags: Generate file flags
    @returns number of the generated lines. -1 if an error occurred
    @retval 0: can't generate exe file
    @retval 1: ok
    """

def get_basic_file_type(li: linput_t *) -> filetype_t: ...
    """Get the input file type. This function can recognize libraries and zip files. 
            
    """

def get_elf_debug_file_directory() -> str: ...
    """Get the value of the ELF_DEBUG_FILE_DIRECTORY configuration directive. 
            
    """

def get_file_type_name() -> str: ...
    """Get name of the current file type. The current file type is kept in idainfo::filetype. 
            
    @returns size of answer, this function always succeeds
    """

def get_fileregion_ea(offset: qoff64_t) -> ida_idaapi.ea_t: ...
    """Get linear address which corresponds to the specified input file offset. If can't be found, return BADADDR 
            
    """

def get_fileregion_offset(ea: int) -> qoff64_t: ...
    """Get offset in the input file which corresponds to the given ea. If the specified ea can't be mapped into the input file offset, return -1. 
            
    """

def get_path(pt: path_type_t) -> str: ...
    """Get the file path 
            
    @param pt: file path type Types of the file pathes
    @returns file path, never returns nullptr
    """

def get_plugin_options(plugin: str) -> str: ...
    """Get plugin options from the command line. If the user has specified the options in the -Oplugin_name:options format, them this function will return the 'options' part of it The 'plugin' parameter should denote the plugin name Returns nullptr if there we no options specified 
            
    """

def is_database_flag(dbfl: int) -> bool: ...
    """Get the current database flag 
            
    @param dbfl: flag Database flags
    @returns the state of the flag (set or cleared)
    """

def is_trusted_idb() -> bool: ...
    """Is the database considered as trusted?
    
    """

def load_and_run_plugin(name: str, arg: size_t) -> bool: ...
    """Load & run a plugin.
    
    """

def load_binary_file(filename: str, li: linput_t *, _neflags: ushort, fileoff: qoff64_t, basepara: int, binoff: int, nbytes: uint64) -> bool: ...
    """Load a binary file into the database. This function usually is called from ui. 
            
    @param filename: the name of input file as is (if the input file is from library, then this is the name from the library)
    @param li: loader input source
    @param _neflags: Load file flags. For the first file, the flag NEF_FIRST must be set.
    @param fileoff: Offset in the input file
    @param basepara: Load address in paragraphs
    @param binoff: Load offset (load_address=(basepara<<4)+binoff)
    @param nbytes: Number of bytes to load from the file.
    * 0: up to the end of the file
    @retval true: ok
    @retval false: failed (couldn't open the file)
    """

def load_ids_module(fname: char *) -> int: ...
    """Load and apply IDS file. This function loads the specified IDS file and applies it to the database. If the program imports functions from a module with the same name as the name of the ids file being loaded, then only functions from this module will be affected. Otherwise (i.e. when the program does not import a module with this name) any function in the program may be affected. 
            
    @param fname: name of file to apply
    @retval 1: ok
    @retval 0: some error (a message is displayed). if the ids file does not exist, no message is displayed
    """

def load_plugin(name: Any) -> Any: ...
    """Loads a plugin
    
    @param name: short plugin name without path and extension,
                 or absolute path to the file name
    @return:
        - None if plugin could not be loaded
        - An opaque object representing the loaded plugin
    """

def mem2base(mem: Any, ea: Any, fpos: Any) -> Any: ...
    """Load database from the memory.
    
    @param mem: the buffer
    @param ea: start linear addresses
    @param fpos: position in the input file the data is taken from.
                 if == -1, then no file position correspond to the data.
    @return:
        - Returns zero if the passed buffer was not a string
        - Otherwise 1 is returned
    """

def process_archive(temp_file: str, li: linput_t *, module_name: str, neflags: ushort *, defmember: str, loader: load_info_t const *) -> str: ...
    """Calls loader_t::process_archive() For parameters and return value description look at loader_t::process_archive(). Additional parameter 'loader' is a pointer to load_info_t structure. 
            
    """

def reload_file(file: str, is_remote: bool) -> bool: ...
    """Reload the input file. This function reloads the byte values from the input file. It doesn't modify the segmentation, names, comments, etc. 
            
    @param file: name of the input file. if file == nullptr then returns:
    * 1: can reload the input file
    * 0: can't reload the input file
    @param is_remote: is the file located on a remote computer with the debugger server?
    @returns success
    """

def run_plugin(plg: Any, arg: Any) -> Any: ...
    """Runs a plugin
    
    @param plg: A plugin object (returned by load_plugin())
    @param arg: the code to pass to the plugin's "run()" function
    @return: Boolean
    """

def save_database(outfile: str = None, flags: int = -1, root: snapshot_t = None, attr: snapshot_t = None) -> bool: ...
    """Save current database using a new file name. 
            
    @param outfile: output database file name; nullptr means the current path
    @param flags: Database flags; -1 means the current flags
    @param root: optional: snapshot tree root.
    @param attr: optional: snapshot attributes
    @returns success
    """

def set_database_flag(dbfl: int, cnd: bool = True) -> None: ...
    """Set or clear database flag 
            
    @param dbfl: flag Database flags
    @param cnd: set if true or clear flag otherwise
    """

def set_import_name(modnode: int, ea: int, name: str) -> None: ...
    """Set information about the named import entry. This function performs 'modnode.supset_ea(ea, name);' 
            
    @param modnode: node with information about imported entries
    @param ea: linear address of the entry
    @param name: name of the entry
    """

def set_import_ordinal(modnode: int, ea: int, ord: int) -> None: ...
    """Set information about the ordinal import entry. This function performs 'modnode.altset(ord, ea2node(ea));' 
            
    @param modnode: node with information about imported entries
    @param ea: linear address of the entry
    @param ord: ordinal number of the entry
    """

def set_path(pt: path_type_t, path: str) -> None: ...
    """Set the file path 
            
    @param pt: file path type Types of the file pathes
    @param path: new file path, use nullptr or empty string to clear the file path
    """

ACCEPT_ARCHIVE: int  # 8192
ACCEPT_CONTINUE: int  # 16384
ACCEPT_FIRST: int  # 32768
DBFL_BAK: int  # 4
DBFL_COMP: int  # 2
DBFL_KILL: int  # 1
DBFL_TEMP: int  # 8
DLLEXT: str  # so
FILEREG_NOTPATCHABLE: int  # 0
FILEREG_PATCHABLE: int  # 1
GENFLG_ASMINC: int  # 64
GENFLG_ASMTYPE: int  # 16
GENFLG_GENHTML: int  # 32
GENFLG_IDCTYPE: int  # 8
GENFLG_MAPDMNG: int  # 4
GENFLG_MAPLOC: int  # 8
GENFLG_MAPNAME: int  # 2
GENFLG_MAPSEG: int  # 1
IDP_DLL: str  # *.so
LDRF_RELOAD: int  # 1
LDRF_REQ_PROC: int  # 2
LOADER_DLL: str  # *.so
MAX_DATABASE_DESCRIPTION: int  # 128
MODULE_ENTRY_IDP: str  # LPH
MODULE_ENTRY_LOADER: str  # LDSC
MODULE_ENTRY_PLUGIN: str  # PLUGIN
NEF_CODE: int  # 256
NEF_FILL: int  # 16
NEF_FIRST: int  # 128
NEF_FLAT: int  # 1024
NEF_IMPS: int  # 32
NEF_LALL: int  # 8192
NEF_LOPT: int  # 4096
NEF_MAN: int  # 8
NEF_MINI: int  # 2048
NEF_NAME: int  # 4
NEF_RELOAD: int  # 512
NEF_RSCS: int  # 2
NEF_SEGS: int  # 1
OFILE_ASM: int  # 4
OFILE_DIF: int  # 5
OFILE_EXE: int  # 1
OFILE_IDC: int  # 2
OFILE_LST: int  # 3
OFILE_MAP: int  # 0
PATH_TYPE_CMD: int  # 0
PATH_TYPE_ID0: int  # 2
PATH_TYPE_IDB: int  # 1
PLUGIN_DLL: str  # *.so
SSF_AUTOMATIC: int  # 1
SSUF_DESC: int  # 1
SSUF_FLAGS: int  # 4
SSUF_PATH: int  # 2
SWIG_PYTHON_LEGACY_BOOL: int  # 1
ida_idaapi: module
weakref: module