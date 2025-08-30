from iode.iode_cython import NA as NA
from iode.util import iode_number_to_str as iode_number_to_str
from typing import Any, Self

Self = Any

class Scalar:
    """
    *Scalars* are essentially estimated coefficients of econometric *equations*. 
    For this reason, each scalar contains in its definition:

    - its *value*
    - the *relaxation* parameter, set to 0 to lock the coefficient during estimation
    - its *standard deviation*, result of the last estimation

    Only the *values* of the *scalars* are relevant when calculating a *LEC* expression. 
    The other two values (relaxation and standard deviation) are only meaningful for estimation.

    The names of *scalars* must be in lowercase so that *variables* are distinct 
    from *scalars* in *LEC* formulas.

    Attributes
    ----------
    value: float
        Value of the scalar.
    relax: float
        Relaxation parameter used in the context of equations estimation.
        For example, setting the relaxation parameter to 0 will 'lock' the coefficient 
        during the estimation process. 
    std: float
        Standard deviation. Calculated during the estimation process.

    Parameters
    ----------
    value: float
        value of the scalar. Defaults to 0.9.
    relax: float
        relax value of the scalar. The value must be between 0.0 and 1.0.
        Defaults to 1.0

    Examples
    --------
    >>> import numpy as np
    >>> from iode import Scalar
    >>> # default relax
    >>> scalar = Scalar(0.9)
    >>> scalar
    Scalar(0.9, 1, na)
    >>> # specific value and relax
    >>> scalar = Scalar(0.9, 0.8)
    >>> scalar
    Scalar(0.9, 0.8, na)
    >>> # Python nan are converted to IODE NA
    >>> scalar = Scalar(np.nan)
    >>> scalar
    Scalar(na, 1, na)
    >>> # Python inf are not accepted
    >>> scalar = Scalar(np.inf)
    Traceback (most recent call last):
    ...
    ValueError: Expected 'value' to be a finite number
    >>> # relax must be between 0.0 and 1.0
    >>> scalar = Scalar(0.9, 1.1)
    Traceback (most recent call last):
    ...
    ValueError: Expected 'relax' value between 0.0 and 1.0
    """
    def __init__(self, value: float, relax: float = 1.0) -> None: ...
    @classmethod
    def get_instance(cls) -> Self: ...
    @property
    def value(self) -> float:
        """
        >>> import numpy as np
        >>> from iode import Scalar
        >>> scalar = Scalar(0.9, 0.8)
        >>> scalar
        Scalar(0.9, 0.8, na)
        >>> scalar.value
        0.9
        >>> scalar.value = 0.8
        >>> scalar.value
        0.8
        >>> # Python nan are converted to IODE NA internally
        >>> # 'scalar.value = np.nan' is equivalent to 
        >>> # 'scalar.value = NA' 
        >>> scalar.value = np.nan
        >>> scalar.value
        nan
        >>> # The numpy isnan can be used to test if  
        >>> # an IODE scalar value is NA or not
        >>> np.isnan(scalar.value)   
        True
        >>> # Python inf are not accepted
        >>> scalar.value = np.inf
        Traceback (most recent call last):
        ...
        ValueError: Expected 'value' to be a finite number
        """
    @value.setter
    def value(self, val: float): ...
    @property
    def relax(self) -> float: ...
    @relax.setter
    def relax(self, value: float): ...
    @property
    def std(self) -> float: ...
    def copy(self) -> Self:
        '''
        Return a copy of the current Scalar.

        Examples
        --------
        >>> from iode import Scalar, scalars, SAMPLE_DATA_DIR
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> scalars["acaf1"]
        Scalar(0.0157684, 1, 0.00136871)
        >>> copied_scl = scalars["acaf1"].copy()
        >>> copied_scl
        Scalar(0.0157684, 1, 0.00136871)
        '''
    def __eq__(self, other: Self) -> bool: ...
    def __copy__(self) -> Self:
        '''
        Return a copy of the current Scalar.

        Examples
        --------
        >>> from copy import copy
        >>> from iode import Scalar, scalars, SAMPLE_DATA_DIR
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> scalars["acaf1"]
        Scalar(0.0157684, 1, 0.00136871)
        >>> copied_scl = copy(scalars["acaf1"])
        >>> copied_scl
        Scalar(0.0157684, 1, 0.00136871)
        '''
    def __hash__(self) -> int: ...
