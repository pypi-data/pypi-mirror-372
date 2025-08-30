from _typeshed import Incomplete
from iode.time.period import Period as Period
from typing import Any, Self

Self = Any
Axis: Incomplete
Axis = Any

class Sample:
    '''
    A sample represents the series of sub periods attached to the IODE variables or to the estimation process.

    Parameters
    ----------
    start_period: str or Period
    \tFirst period of the sample.
    \tIf str, it must be a valid period string (e.g. \'1960Y1\').
    end_period: str or Period
    \tLast period of the sample.
        If str, it must be a valid period string (e.g. \'2015Y1\').

    Attributes
    ----------
    start: str
        First period of the sample.
    end: str
        Last period of the sample.
    nb_periods: int
        Total number of sub periods in the sample. 

    Examples
    --------
    >>> from iode import Sample
    >>> Sample("1982Y1", "2020Y1")
    Sample("1982Y1:2020Y1")
    >>> Sample("1982Y1:2020Y1")
    Sample("1982Y1:2020Y1")
    '''
    def __init__(self, start_period: str | Period, end_period: str | Period = None) -> None: ...
    @classmethod
    def get_instance(cls) -> Self: ...
    def index(self, period: str | Period) -> int:
        '''
        Position of the \'period\' in the sample.

        Returns
        -------
        int

        Raises
        ------
        IndexError
            If the \'period\' has not been found in the sample.

        Examples
        --------
        >>> from iode import variables, SAMPLE_DATA_DIR
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")    # doctest: +ELLIPSIS
        Loading .../fun.var
        394 objects loaded
        >>> variables.sample.index("1982Y1")
        22
        >>> variables.sample.index("2020Y1")
        Traceback (most recent call last):
        ... 
        IndexError: The period \'2020Y1\' is not in the sample \'1960Y1:2015Y1\'
        '''
    def get_period_list(self, astype: None | str = ...) -> list[Any]:
        '''
        List of all periods of the sample.
        Periods are exported as string (default) or as float.

        Parameters
        ----------
        astype: type or str
            Allowed returned type for periods are: \'str\', \'float\', \'Period\'.
            Default to str.

        Returns
        -------
        list(str) or list(float)

        Examples
        --------
        >>> from iode import variables, SAMPLE_DATA_DIR
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")      # doctest: +ELLIPSIS
        Loading .../fun.var
        394 objects loaded
        >>> variables.sample.get_period_list()                  # doctest: +ELLIPSIS
        [\'1960Y1\', \'1961Y1\', ..., \'2014Y1\', \'2015Y1\']
        >>> variables.sample.get_period_list(astype=float)      # doctest: +ELLIPSIS
        [1960.0, 1961.0, ..., 2014.0, 2015.0]
        >>> variables.sample.get_period_list(astype=Period)     # doctest: +ELLIPSIS
        [Period("1960Y1"), Period("1961Y1"), ..., Period("2014Y1"), Period("2015Y1")]
        '''
    def intersection(self, other_sample: Self) -> Self:
        '''
        Compute the intersection between two samples.

        Returns
        -------
        Sample

        Examples
        --------
        >>> from iode import variables, SAMPLE_DATA_DIR
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")    # doctest: +ELLIPSIS
        Loading .../fun.var
        394 objects loaded
        >>> variables.sample
        Sample("1960Y1:2015Y1")
        >>> variables_2 = variables.copy()
        >>> variables_2.sample = "2000Y1:2040Y1"
        >>> variables_2.sample
        Sample("2000Y1:2040Y1")
        >>> sample_intersec = variables.sample.intersection(variables_2.sample)
        >>> sample_intersec
        Sample("2000Y1:2015Y1")
        '''
    @property
    def start(self) -> Period: ...
    @property
    def end(self) -> Period: ...
    @property
    def nb_periods(self) -> int: ...
    @property
    def periods(self) -> list[Period]:
        '''
        Return the list of periods.

        Returns
        -------
        List[Period]

        Examples
        --------
        >>> from iode import variables, SAMPLE_DATA_DIR
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")    # doctest: +ELLIPSIS
        Loading .../fun.var
        394 objects loaded
        >>> variables.sample.periods    # doctest: +ELLIPSIS
        [Period("1960Y1"), Period("1961Y1"), ..., Period("2014Y1"), Period("2015Y1")]
        '''
    def __len__(self) -> int: ...
    def __eq__(self, other: Self) -> bool: ...
