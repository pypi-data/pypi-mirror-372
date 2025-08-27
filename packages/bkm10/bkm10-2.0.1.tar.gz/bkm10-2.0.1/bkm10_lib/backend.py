"""
The BKM10 formalism has been needed for machine-learning purposes.
Here, we provide the logic that facilitates usage of the library
in TensorFlow contexts.
"""

# 3rd Party Library | NumPy:
import numpy as _np

# 3rd Party Library | TensorFlow:
import tensorflow as _tf

# (X): Set the default backend "math computation" library to be NumPy:
_backend = "numpy"

def set_backend(backend):
    """
    ## Description:
    We provide an interface for the user to inform the library
    what kind of math computation is required.
    """

    # (X): In order for this to work, we need to make the backend option global:
    global _backend

    # (X): If a provided backend value does not correspond to NumPy or TensorFlow..
    if backend not in ["numpy", "tensorflow"]:

        # (X): ... raise a Value error demanding the *value* be NP or TF:
        raise ValueError("Backend must be 'numpy' or 'tensorflow'")
    
    # (X): Otherwise, we go ahead and set the backend to whatever it is:
    _backend = backend

def get_backend():
    """
    ## Description:
    Now that we have provided the opportunity change the backend setting,
    we need to be able to find what it is currently set to.
    """

    # (X): Return the backend variable:
    return _backend

def safe_cast(x, promote_to_complex_if_needed=False):
    """
    ## Description:
    In order to handle `complex` types *and* TensorFlow tensors,
    we need to implement a function that will *always* guarantee that
    we are not performing illegal operations between Tensors of different
    type
    - In TensorFlow mode, floats become tf.float32, complexes become tf.complex64.
    - If promote_to_complex_if_needed is True, tf.float32 values are promoted to tf.complex64.
    """
    if get_backend() == "tensorflow":
        if isinstance(x, float):
            x = _tf.constant(x, dtype = _tf.float32)

        elif isinstance(x, complex):
            x = _tf.complex(_tf.constant(x.real, dtype = _tf.float32),
                           _tf.constant(x.imag, dtype = _tf.float32))
            
        elif not _tf.is_tensor(x):
            x = _tf.convert_to_tensor(x)

        if promote_to_complex_if_needed and x.dtype == _tf.float32:
            x = _tf.complex(x, _tf.zeros_like(x))

    return x

class MathWrapper:
    """
    ## Description:
    The `MathWrapper` class helps us easily pass between computing
    values with NumPy or TensorFlow.
    """
    def __getattr__(self, name):
        """
        ## Description:
        In order to handle equivalent math operations between NumPy and
        TensorFlow, we need to be able to *map* (bjectively) between the
        two libraries. So, we need this wrapper to handle this check: 
        Whenever a "math attribute" is used, we have to check if we're
        going to use NumPy or TensorFlow based on the backend setting and
        then evaluate it accordingly.

        ## Notes:
        The main reason we have this --- perhaps the *only* reason --- is 
        because raising things to powers in NumPy is done with np.power() but
        it is tf.pow() in TensorFlow... Thanks, Obama!
        """

        # (X): Sly trick expose either NP or TF computing based on backkend setting:
        mod = _np if _backend == "numpy" else _tf

        # (X): The major exception is that np.power() is equivalent to tf.pow()... Annoying!
        if name == "power" and _backend == "tensorflow":
            return _tf.pow
       
        # (X): Another exception is that the constant pi is *not* in TensorFlow. Yay!
        if name == "pi":
            return _np.pi if _backend == "numpy" else _tf.constant(_np.pi, dtype = _tf.float32)
        
        # (X): TensorFlow also doesn't come with Euler's Number:
        if name == "e":
            return _np.e if _backend == "numpy" else _tf.constant(_np.e, dtype=_tf.float32)
        
        # (X): A major, major hurdle is having TensorFlow handle complex types!
        if name == "complex":
            return complex if _backend == "numpy" else lambda real_part, imag_part: _tf.complex(real_part, imag_part)
        
        # (X): Since we're relying on complex types, NumPy and TensorFlow will not handle them similarly,
        # | so we need to tell it when to us `.real` versus TensorFlow's `.real`.
        if name == "real":
            return (lambda x: x.real) if _backend == "numpy" else _tf.math.real
        
        # (X): Same as above, but for `.imag`:
        if name == "imag":
            return (lambda x: x.imag) if _backend == "numpy" else _tf.math.imag
        
        # (X): We also used the NumPy method `atleast_1d`
        if name == "atleast_1d":

            if _backend == "tensorflow":
                return lambda x: _tf.convert_to_tensor(x) if isinstance(x, (list, tuple)) else _tf.expand_dims(x, axis = 0)
            
            else:
                return _np.atleast_1d
        
        # (X): Return the computed attribute according to the backend setting:
        return getattr(mod, name)
    
    def safe_cast(self, x, promote_to_complex_if_needed = False):
        """
        ## Description:
        For a description of what's happening, please see the function `safe_cast` above.
        """
        return safe_cast(x, promote_to_complex_if_needed)
    
    def promote_scalar_to_dtype(self, scalar, reference):
        """
        ## Description:
        Promote a Python scalar to the same dtype as the reference tensor/array.
        Works under both NumPy and TensorFlow backends.

        ## Arguments:
            scalar: A Python scalar (float or int)

            reference: A tensor or array whose dtype will be matched

        ## Returns:
            A scalar of the same backend and dtype as `reference`
        """

        if _backend == "tensorflow":
            if hasattr(reference, "dtype"):
                ref_dtype = reference.dtype
            else:
                ref_dtype = _tf.complex64 if isinstance(reference, complex) else _tf.float32

            if ref_dtype.is_complex:
                return _tf.complex(
                    _tf.constant(scalar, dtype = _tf.float32),
                    _tf.constant(0.0, dtype = _tf.float32)
                )
            else:
                return _tf.constant(scalar, dtype=ref_dtype)

        elif _backend == "numpy":
            reference_datatype = reference.dtype if hasattr(reference, "dtype") else _np.float32

            return _np.array(scalar, dtype = reference_datatype)

        else:
            raise ValueError(f"Unsupported backend: {_backend}")
        
# (X): Export the wrapper that handles the library-specific attribute business:
math = MathWrapper()
