import ctypes
import os
import platform
from typing import Optional

class Kernl:
    """Python wrapper for Kernl SDK"""
    
    def __init__(self):
        self._lib = self._load_library()
        self._handle = None
        self._setup_functions()
        self._create_handle()
    
    def _load_library(self) -> ctypes.CDLL:
        """Load the native library"""
        # Determine library name based on platform
        library_names = {
            'Darwin': 'libkernl_c.dylib',
            'Linux': 'libkernl_c.so',
            'Windows': 'kernl_c.dll'
        }
        
        library_name = library_names.get(platform.system(), 'libkernl_c.so')
        
        # Try different locations
        search_paths = [
            # Look in the embedded lib directory (for wheels)
            os.path.join(os.path.dirname(__file__), 'lib', library_name),
            # Look in the same directory as this Python file (fallback)
            os.path.join(os.path.dirname(__file__), library_name),
            # Look in common build directories relative to current working dir (for development)
            os.path.join(os.getcwd(), 'build', 'lib', library_name),
            os.path.join(os.getcwd(), 'dist', 'native', 'lib', library_name),
            # Look in common absolute paths for testing
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'build', 'lib', library_name)),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'dist', 'native', 'lib', library_name)),
            # Try just the library name (system paths)
            library_name
        ]
        
        for path in search_paths:
            try:
                if os.path.exists(path):
                    # On Windows, add the directory containing the DLL to PATH
                    if platform.system() == 'Windows':
                        dll_dir = os.path.dirname(os.path.abspath(path))
                        old_path = os.environ.get('PATH', '')
                        os.environ['PATH'] = dll_dir + os.pathsep + old_path
                    return ctypes.CDLL(path)
            except OSError as e:
                # Debug output for troubleshooting
                if os.path.exists(path):
                    import sys
                    print(f"Failed to load {path}: {e}", file=sys.stderr)
                continue
        
        raise RuntimeError(f"Could not load Kernl library: {library_name}")
    
    def _setup_functions(self):
        """Setup function signatures"""
        # kernl_create
        self._lib.kernl_create.restype = ctypes.c_void_p
        self._lib.kernl_create.argtypes = []
        
        # kernl_destroy
        self._lib.kernl_destroy.restype = None
        self._lib.kernl_destroy.argtypes = [ctypes.c_void_p]
        
        # kernl_initialize
        self._lib.kernl_initialize.restype = ctypes.c_int
        self._lib.kernl_initialize.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        
        # kernl_print
        self._lib.kernl_print.restype = None
        self._lib.kernl_print.argtypes = [ctypes.c_void_p]
        
        # kernl_get_message
        self._lib.kernl_get_message.restype = ctypes.c_char_p
        self._lib.kernl_get_message.argtypes = [ctypes.c_void_p]
        
        # kernl_is_initialized
        self._lib.kernl_is_initialized.restype = ctypes.c_int
        self._lib.kernl_is_initialized.argtypes = [ctypes.c_void_p]
    
    def _create_handle(self):
        """Create the native handle"""
        self._handle = self._lib.kernl_create()
        if not self._handle:
            raise RuntimeError("Failed to create Kernl handle")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, '_handle') and self._handle:
            self._lib.kernl_destroy(self._handle)
    
    def initialize(self, message: str) -> bool:
        """Initialize Kernl with a message"""
        if not self._handle:
            return False
        
        result = self._lib.kernl_initialize(self._handle, message.encode('utf-8'))
        return result == 1
    
    def print(self):
        """Print the stored message"""
        if self._handle:
            self._lib.kernl_print(self._handle)
    
    @property
    def message(self) -> Optional[str]:
        """Get the stored message"""
        if not self._handle:
            return None
        
        result = self._lib.kernl_get_message(self._handle)
        return result.decode('utf-8') if result else None
    
    @property
    def is_initialized(self) -> bool:
        """Check if Kernl is initialized"""
        if not self._handle:
            return False
        
        return self._lib.kernl_is_initialized(self._handle) == 1