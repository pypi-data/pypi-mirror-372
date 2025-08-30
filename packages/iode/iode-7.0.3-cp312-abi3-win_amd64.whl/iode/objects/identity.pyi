from typing import Any, Self

Self = Any

class Identity:
    '''
    An *identity* is an expression written in the *LEC* language that allows the construction of a 
    new statistical series based on already defined series. In general, *identities* are executed
    in groups to create or update a set of *variables*. *Identities* can be executed for a specific 
    range of periods, or for all periods defined in the workspace.

    *Identities* should not be confused with *equations*. They are not part of a model.

    Parameters
    ----------
    lec: str
        formula (*LEC* expression) used to construct a series.

    Examples
    --------
    >>> from iode import Identity
    >>> idt = Identity("FLG/VBBP")
    >>> idt
    Identity(\'FLG/VBBP\')
    '''
    def __init__(self, lec: str) -> None: ...
    @classmethod
    def get_instance(cls) -> Self: ...
    @property
    def coefficients(self) -> list[str]:
        '''
        Return the list of coefficients present in the current identity.

        Returns
        -------
        list(str)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR
        >>> from iode import Identity, scalars, variables
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> idt = Identity("1 - exp((gamma2 + gamma3 * ln(W/ZJ)[-1] + gamma4 * ln(WMIN/ZJ)) / gamma_)")
        >>> idt
        Identity(\'1 - exp((gamma2 + gamma3 * ln(W/ZJ)[-1] + gamma4 * ln(WMIN/ZJ)) / gamma_)\')
        >>> idt.coefficients
        [\'gamma2\', \'gamma3\', \'gamma4\', \'gamma_\']
        '''
    @property
    def variables(self) -> list[str]:
        '''
        Return the list of variables present in the identity.

        Returns
        -------
        list(str)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR
        >>> from iode import Identity, scalars, variables
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> idt = Identity("1 - exp((gamma2 + gamma3 * ln(W/ZJ)[-1] + gamma4 * ln(WMIN/ZJ)) / gamma_)")
        >>> idt
        Identity(\'1 - exp((gamma2 + gamma3 * ln(W/ZJ)[-1] + gamma4 * ln(WMIN/ZJ)) / gamma_)\')
        >>> idt.variables
        [\'W\', \'ZJ\', \'WMIN\']
        '''
    def copy(self) -> Self:
        '''
        Return a copy of the current Identity.

        Examples
        --------
        >>> from iode import Identity
        >>> idt = Identity("FLG/VBBP")
        >>> idt
        Identity(\'FLG/VBBP\')
        >>> copied_idt = idt.copy()
        >>> copied_idt
        Identity(\'FLG/VBBP\')
        '''
    def __eq__(self, other: Self) -> bool: ...
    def __copy__(self) -> Self:
        '''
        Return a copy of the current Identity.

        Examples
        --------
        >>> from copy import copy
        >>> from iode import Identity
        >>> idt = Identity("FLG/VBBP")
        >>> idt
        Identity(\'FLG/VBBP\')
        >>> copied_idt = copy(idt)
        >>> copied_idt
        Identity(\'FLG/VBBP\')
        '''
    def __hash__(self) -> int: ...
